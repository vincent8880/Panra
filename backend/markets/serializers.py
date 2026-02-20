from rest_framework import serializers
from .models import Market, MarketOutcome


class MarketOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketOutcome
        fields = ['id', 'name', 'price', 'volume']


class MarketSerializer(serializers.ModelSerializer):
    """Market serializer with computed fields."""
    yes_price = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)
    no_price = serializers.DecimalField(max_digits=5, decimal_places=4, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Market
        fields = [
            'id', 'title', 'description', 'slug', 'question', 'resolution_criteria',
            'category', 'image_url', 'status', 'resolution', 'created_at', 'end_date',
            'resolution_date', 'created_by_username', 'total_volume',
            'total_liquidity', 'yes_price', 'no_price'
        ]
        read_only_fields = ['id', 'created_at', 'yes_price', 'no_price']


class MarketDetailSerializer(MarketSerializer):
    """Detailed market serializer with outcomes."""
    outcomes = MarketOutcomeSerializer(many=True, read_only=True)
    
    class Meta(MarketSerializer.Meta):
        fields = MarketSerializer.Meta.fields + ['outcomes']



