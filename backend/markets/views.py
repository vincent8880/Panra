from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Market
from .serializers import MarketSerializer, MarketDetailSerializer


class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    """Market viewset for listing and viewing markets."""
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['title', 'question', 'description', 'slug']
    ordering_fields = ['created_at', 'total_volume', 'end_date']
    ordering = ['-created_at']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MarketDetailSerializer
        return MarketSerializer
    
    def get_object(self):
        """Override to support slug lookup."""
        lookup_value = self.kwargs[self.lookup_field]
        queryset = self.get_queryset()
        return get_object_or_404(queryset, slug=lookup_value)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, slug=None):
        """Get market statistics."""
        market = self.get_object()
        return Response({
            'total_volume': market.total_volume,
            'total_liquidity': market.total_liquidity,
            'yes_price': market.yes_price,
            'no_price': market.no_price,
            'status': market.status,
        })



