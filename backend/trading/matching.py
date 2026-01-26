"""
Order Matching Engine with Sound Price Discovery

This module implements a robust order matching system that:
1. Matches buy/sell orders efficiently
2. Updates market prices based on trade volume (VWAP - Volume Weighted Average Price)
3. Handles partial fills correctly
4. Updates positions and credits accurately
5. Maintains price consistency (yes_price + no_price = 1.00)
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN
from .models import Order, Trade, Position
from markets.models import Market


def match_orders(new_order):
    """
    Match a new order against existing orders and execute trades.
    
    Algorithm:
    1. Find matching orders (opposite side, compatible price)
    2. Execute trades at the best available price
    3. Update market prices using VWAP (Volume Weighted Average Price)
    4. Update positions and credits
    5. Handle partial fills
    
    Returns: List of created Trade objects
    """
    with transaction.atomic():
        trades = []
        remaining_quantity = new_order.quantity
        
        # Determine what we're looking for
        # If buying YES, we need someone selling YES (same side, opposite action)
        # If buying NO, we need someone selling NO (same side, opposite action)
        # For now, we match same-side orders where price is compatible
        # Note: In a full system, we'd track buy vs sell orders separately
        # For simplicity, we match orders of the same side where prices overlap
        
        if new_order.side == 'yes':
            # Buying YES - look for YES orders with compatible price
            # Match if their price <= our price (we're willing to pay their ask)
            matching_orders = Order.objects.filter(
                market=new_order.market,
                side='yes',
                status__in=['pending', 'partial'],
                price__lte=new_order.price
            ).exclude(user=new_order.user).order_by('price', 'created_at')
            
        else:  # new_order.side == 'no'
            # Buying NO - look for NO orders with compatible price
            matching_orders = Order.objects.filter(
                market=new_order.market,
                side='no',
                status__in=['pending', 'partial'],
                price__lte=new_order.price
            ).exclude(user=new_order.user).order_by('price', 'created_at')
        
        # Try to match against existing orders
        for matching_order in matching_orders:
            if remaining_quantity <= 0:
                break
            
            # Determine trade price (use the better price for the new order)
            # If new order is limit, use matching order's price (better for new order)
            trade_price = matching_order.price
            
            # Calculate how much we can fill
            available_quantity = matching_order.quantity - matching_order.filled_quantity
            fill_quantity = min(remaining_quantity, available_quantity)
            
            if fill_quantity <= 0:
                continue
            
            # Create the trade
            # Determine which is buy and which is sell based on order creation time
            # Earlier order is the "seller" (maker), later is "buyer" (taker)
            if new_order.created_at < matching_order.created_at:
                buy_order = matching_order
                sell_order = new_order
            else:
                buy_order = new_order
                sell_order = matching_order
            
            trade = create_trade(
                buy_order=buy_order,
                sell_order=sell_order,
                price=trade_price,
                quantity=fill_quantity
            )
            trades.append(trade)
            
            # Update order statuses
            update_order_after_trade(new_order, fill_quantity)
            update_order_after_trade(matching_order, fill_quantity)
            
            remaining_quantity -= fill_quantity
        
        # Update market price based on trades (VWAP)
        if trades:
            update_market_price(new_order.market, trades)
        
        return trades


def create_trade(buy_order, sell_order, price, quantity):
    """
    Create a trade record and update positions/credits.
    
    This is the core trade execution logic that ensures:
    - Credits are transferred correctly
    - Positions are updated accurately
    - Market volume is tracked
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Determine buyer and seller
    if buy_order.side == 'yes':
        buyer = buy_order.user
        seller = sell_order.user
        side = 'yes'
    else:
        buyer = buy_order.user
        seller = sell_order.user
        side = 'no'
    
    # Calculate trade value
    total_value = price * quantity
    
    # Create trade record
    trade = Trade.objects.create(
        market=buy_order.market,
        buy_order=buy_order,
        sell_order=sell_order,
        buyer=buyer,
        seller=seller,
        side=side,
        price=price,
        quantity=quantity,
        total_value=total_value,
        executed_at=timezone.now()
    )
    
    # Update buyer's position and credits
    # Buyer pays: price * quantity
    # Buyer receives: quantity shares
    buyer_cost = total_value
    buyer.update_credits_from_trade(-buyer_cost)
    update_position(buyer, buy_order.market, side, quantity, price, is_buy=True)
    
    # Update seller's position and credits
    # Seller receives: price * quantity
    # Seller gives up: quantity shares
    seller_proceeds = total_value
    seller.update_credits_from_trade(seller_proceeds)
    update_position(seller, sell_order.market, side, quantity, price, is_buy=False)
    
    # Update market volume
    buy_order.market.total_volume += total_value
    buy_order.market.save(update_fields=['total_volume'])
    
    return trade


def update_position(user, market, side, quantity, price, is_buy=True):
    """
    Update user's position in a market after a trade.
    
    For YES shares:
    - Buying YES: Add to yes_shares, update avg cost
    - Selling YES: Subtract from yes_shares
    
    For NO shares:
    - Buying NO: Add to no_shares, update avg cost
    - Selling NO: Subtract from no_shares
    """
    position, created = Position.objects.get_or_create(
        user=user,
        market=market,
        defaults={
            'yes_shares': Decimal('0.00'),
            'no_shares': Decimal('0.00'),
            'yes_avg_cost': Decimal('0.0000'),
            'no_avg_cost': Decimal('0.0000'),
        }
    )
    
    if side == 'yes':
        if is_buy:
            # Buying YES shares
            # Update average cost: (old_avg * old_qty + new_price * new_qty) / (old_qty + new_qty)
            old_qty = position.yes_shares
            old_avg = position.yes_avg_cost
            new_qty = quantity
            
            if old_qty > 0:
                total_cost = (old_avg * old_qty) + (price * new_qty)
                total_qty = old_qty + new_qty
                position.yes_avg_cost = (total_cost / total_qty).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
            else:
                position.yes_avg_cost = price
            
            position.yes_shares += quantity
        else:
            # Selling YES shares
            position.yes_shares = max(Decimal('0.00'), position.yes_shares - quantity)
            # If all shares sold, reset avg cost
            if position.yes_shares == 0:
                position.yes_avg_cost = Decimal('0.0000')
    else:  # side == 'no'
        if is_buy:
            # Buying NO shares
            old_qty = position.no_shares
            old_avg = position.no_avg_cost
            new_qty = quantity
            
            if old_qty > 0:
                total_cost = (old_avg * old_qty) + (price * new_qty)
                total_qty = old_qty + new_qty
                position.no_avg_cost = (total_cost / total_qty).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
            else:
                position.no_avg_cost = price
            
            position.no_shares += quantity
        else:
            # Selling NO shares
            position.no_shares = max(Decimal('0.00'), position.no_shares - quantity)
            if position.no_shares == 0:
                position.no_avg_cost = Decimal('0.0000')
    
    position.save()


def update_order_after_trade(order, filled_quantity):
    """Update order status after a trade."""
    order.filled_quantity += filled_quantity
    
    if order.filled_quantity >= order.quantity:
        order.status = 'filled'
        order.filled_at = timezone.now()
    else:
        order.status = 'partial'
    
    order.save()


def update_market_price(market, trades):
    """
    Update market prices using Volume Weighted Average Price (VWAP).
    
    This ensures prices reflect actual trading activity and maintain:
    - yes_price + no_price = 1.00
    - Prices reflect recent trading volume
    """
    if not trades:
        return
    
    # Calculate VWAP for YES and NO
    yes_total_value = Decimal('0.00')
    yes_total_quantity = Decimal('0.00')
    no_total_value = Decimal('0.00')
    no_total_quantity = Decimal('0.00')
    
    # Get recent trades for this market (last 100 trades)
    recent_trades = Trade.objects.filter(
        market=market
    ).order_by('-executed_at')[:100]
    
    for trade in recent_trades:
        if trade.side == 'yes':
            yes_total_value += trade.total_value
            yes_total_quantity += trade.quantity
        else:  # trade.side == 'no'
            no_total_value += trade.total_value
            no_total_quantity += trade.quantity
    
    # Calculate VWAP
    if yes_total_quantity > 0:
        yes_vwap = yes_total_value / yes_total_quantity
    else:
        yes_vwap = market.yes_price  # Keep current if no trades
    
    if no_total_quantity > 0:
        no_vwap = no_total_value / no_total_quantity
    else:
        no_vwap = market.no_price
    
    # Normalize to ensure yes_price + no_price = 1.00
    # Use weighted average: 70% new VWAP, 30% current price (smoothing)
    smoothing_factor = Decimal('0.7')
    new_yes_price = (yes_vwap * smoothing_factor) + (market.yes_price * (Decimal('1') - smoothing_factor))
    new_no_price = (no_vwap * smoothing_factor) + (market.no_price * (Decimal('1') - smoothing_factor))
    
    # Normalize
    total = new_yes_price + new_no_price
    if total > 0:
        market.yes_price = (new_yes_price / total).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
        market.no_price = (new_no_price / total).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)
    else:
        # Fallback to 50/50 if something goes wrong
        market.yes_price = Decimal('0.5000')
        market.no_price = Decimal('0.5000')
    
    # Ensure they sum to 1.00 exactly
    market.no_price = Decimal('1.0000') - market.yes_price
    
    market.save(update_fields=['yes_price', 'no_price'])

