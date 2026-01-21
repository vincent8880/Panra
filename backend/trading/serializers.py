from rest_framework import serializers
from .models import Order, Trade, Position


class OrderSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    market_title = serializers.CharField(source='market.title', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'market', 'market_title', 'user', 'user_username',
            'side', 'order_type', 'price', 'quantity', 'status',
            'filled_quantity', 'created_at', 'updated_at', 'filled_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'filled_quantity', 'created_at', 'updated_at', 'filled_at']
    
    def validate(self, data):
        """Validate order data."""
        price = data.get('price', 0)
        quantity = data.get('quantity', 0)
        
        if price <= 0 or price > 1:
            raise serializers.ValidationError({
                'price': 'Price must be between 0 and 1'
            })
        
        if quantity <= 0:
            raise serializers.ValidationError({
                'quantity': 'Quantity must be greater than 0'
            })
        
        return data


class TradeSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    market_title = serializers.CharField(source='market.title', read_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'market', 'market_title', 'buyer', 'buyer_username',
            'seller', 'seller_username', 'side', 'price', 'quantity',
            'total_value', 'executed_at'
        ]
        read_only_fields = ['id', 'executed_at']


class PositionSerializer(serializers.ModelSerializer):
    market_title = serializers.CharField(source='market.title', read_only=True)
    
    class Meta:
        model = Position
        fields = [
            'id', 'market', 'market_title', 'yes_shares', 'no_shares',
            'yes_avg_cost', 'no_avg_cost', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']



