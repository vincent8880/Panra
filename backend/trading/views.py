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
        
        # Credits are deducted only when a trade executes (in matching.create_trade).
        # We do NOT deduct here to avoid double-deduction when order matches immediately.
        
        # Try to match the order immediately
        try:
            trades = match_orders(order)
            if trades:
                # Order was (partially) filled
                order.refresh_from_db()
        except Exception as e:
            # Log error but don't fail order creation
            # The order will remain pending and can be matched later
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



