from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    credits = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    current_credits = serializers.SerializerMethodField()
    credit_status = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'credits', 'current_credits', 'credit_status',
            'total_points', 'weekly_points', 'monthly_points',
            'win_streak', 'best_win_streak', 'markets_predicted_correctly',
            'total_markets_traded', 'accuracy_percentage', 'roi_percentage',
            'date_joined', 'rank'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_current_credits(self, obj):
        """Spendable credits = raw stored (matches order deduct/check)."""
        return float(obj.credits)
    
    def get_credit_status(self, obj):
        """Get detailed credit status including decay and regeneration info."""
        now = timezone.now()
        current = obj.get_current_credits()
        stored = obj.credits
        
        # Calculate decay info
        days_inactive = 0
        next_decay = None
        if obj.last_activity_at:
            days_inactive = (now - obj.last_activity_at).total_seconds() / 86400
            
            if days_inactive > 0:
                # Next decay happens after 24 hours of inactivity
                next_decay = obj.last_activity_at + timedelta(days=1)
        
        # Calculate regeneration info
        regen_rate = Decimal('100.00')  # 100 credits per hour
        hours_to_full = None
        if current < obj.max_credits:
            credits_needed = obj.max_credits - current
            hours_to_full = float(credits_needed / regen_rate)
        
        return {
            'current': float(current),
            'stored': float(stored),
            'max': float(obj.max_credits),
            'days_inactive': round(days_inactive, 2),
            'next_decay_at': next_decay.isoformat() if next_decay else None,
            'regenerating': current < obj.base_credits,
            'hours_to_full_regen': round(hours_to_full, 2) if hours_to_full else None,
            'regen_rate_per_hour': float(regen_rate),
        }
    
    def get_rank(self, obj):
        """Calculate user's rank based on total_points."""
        if obj.total_points <= 0:
            return None
        rank = User.objects.filter(total_points__gt=obj.total_points).count() + 1
        return rank


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'phone_number', 'mpesa_number', 'total_volume_traded', 'total_profit_loss']



