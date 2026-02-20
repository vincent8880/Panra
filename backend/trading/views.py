from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from decimal import Decimal
# Lazy import - only import when needed (after package is installed)
from .models import Order, Trade, Position
from .serializers import OrderSerializer, TradeSerializer, PositionSerializer
from markets.models import Market
from .matching import match_orders


@method_decorator(csrf_exempt, name='dispatch')
class OrderViewSet(viewsets.ModelViewSet):
    """Order viewset for creating and managing orders.
    
    CSRF exempt because we use JWT token authentication for API requests.
    Only uses JWT authentication (no session auth) to avoid CSRF requirements.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_authenticators(self):
        """Lazy load JWT authentication to avoid import errors during deployment."""
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            return [JWTAuthentication()]
        except ImportError:
            # Fallback during deployment - but still exempt CSRF
            from rest_framework.authentication import SessionAuthentication
            return [SessionAuthentication()]
    
    def initial(self, request, *args, **kwargs):
        """Override initial to ensure CSRF is bypassed."""
        # Call parent initial
        super().initial(request, *args, **kwargs)
        # Explicitly mark request as CSRF exempt
        request.csrf_processing_done = True
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        price = validated_data['price']
        quantity = validated_data['quantity']
        cost = price * quantity
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        with transaction.atomic():
            # Lock user row to prevent race condition when placing multiple orders
            user = User.objects.select_for_update().get(pk=self.request.user.pk)
            current_credits = user.credits  # Raw stored credits (spendable balance)
            
            if current_credits < cost:
                raise ValidationError({
                    'non_field_errors': [f'Insufficient credits. You have {float(current_credits):.2f}, need {float(cost):.2f}']
                })
            
            order = serializer.save(user=user)
            user.update_credits_from_trade(-cost)
            
            # Update market volume/liquidity when order is placed
            market = order.market
            market.total_volume += cost
            market.total_liquidity += cost
            market.save(update_fields=['total_volume', 'total_liquidity'])
        
        try:
            trades = match_orders(order)
            if trades:
                order.refresh_from_db()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error matching order {order.id}: {str(e)}")
    
    @action(detail=False, methods=['get'])
    def open(self, request):
        """Get user's open orders."""
        open_orders = self.get_queryset().filter(status__in=['pending', 'partial'])
        serializer = self.get_serializer(open_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status not in ['pending', 'partial']:
            return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Refund credits for unfilled portion
        unfilled = order.quantity - order.filled_quantity
        if unfilled > 0:
            refund = unfilled * order.price
            order.user.update_credits_from_trade(refund)
            # Reduce market volume/liquidity by unfilled amount
            market = order.market
            market.total_volume = max(0, market.total_volume - refund)
            market.total_liquidity = max(0, market.total_liquidity - refund)
            market.save(update_fields=['total_volume', 'total_liquidity'])
        
        order.status = 'cancelled'
        order.save()
        return Response({'status': 'Order cancelled'})


class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    """Trade viewset for viewing executed trades."""
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        market_id = self.request.query_params.get('market', None)
        queryset = Trade.objects.all()
        
        if market_id:
            queryset = queryset.filter(market_id=market_id)
        
        return queryset.order_by('-executed_at')[:100]  # Last 100 trades


class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    """Position viewset for viewing user positions."""
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Position.objects.filter(user=self.request.user)



