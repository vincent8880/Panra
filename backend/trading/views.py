from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Order, Trade, Position
from .serializers import OrderSerializer, TradeSerializer, PositionSerializer
from markets.models import Market


class OrderViewSet(viewsets.ModelViewSet):
    """Order viewset for creating and managing orders."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Validate data first before saving
        validated_data = serializer.validated_data
        price = validated_data['price']
        quantity = validated_data['quantity']
        
        # Calculate cost: price * quantity
        cost = price * quantity
        
        # Check if user has enough credits BEFORE creating the order
        user = self.request.user
        current_credits = user.get_current_credits()
        
        if current_credits < cost:
            raise ValidationError({
                'non_field_errors': [f'Insufficient credits. You have {current_credits:.2f}, need {cost:.2f}']
            })
        
        # Save the order
        order = serializer.save(user=self.request.user)
        
        # Deduct credits when order is placed
        # Note: Credits will be adjusted when order is filled/cancelled
        user.update_credits_from_trade(-cost)
    
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



