from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from decimal import Decimal
import math


class User(AbstractUser):
    """Custom user model with practice credits."""
    # Practice credits (not real money)
    credits = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=10000.00,
        help_text="Practice credits balance (starts at 10,000)"
    )
    
    # Track last activity for decay calculation
    last_activity_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        help_text="Last time user made a trade (used for decay calculation)"
    )
    
    # Track base credits (before decay/regeneration) for regeneration calculation
    base_credits = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=10000.00,
        help_text="Base credits amount (used to calculate regeneration)"
    )
    
    # Maximum credits cap
    max_credits = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=10000.00,
        help_text="Maximum credits this user can have"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Points and Leaderboard System
    total_points = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Total points for leaderboard ranking"
    )
    weekly_points = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Points earned this week (resets weekly)"
    )
    monthly_points = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0.00,
        help_text="Points earned this month (resets monthly)"
    )
    
    # Trading Performance Stats
    win_streak = models.IntegerField(
        default=0,
        help_text="Current consecutive correct predictions"
    )
    best_win_streak = models.IntegerField(
        default=0,
        help_text="All-time best win streak"
    )
    markets_predicted_correctly = models.IntegerField(
        default=0,
        help_text="Total markets where prediction was correct"
    )
    total_markets_traded = models.IntegerField(
        default=0,
        help_text="Total markets user has traded in"
    )
    accuracy_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Win rate percentage (0-100)"
    )
    roi_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Return on investment percentage"
    )
    
    def __str__(self):
        return self.username
    
    def get_current_credits(self):
        """
        Calculate current credits based on decay and regeneration.
        This is the actual balance the user sees.
        """
        from datetime import timedelta
        
        now = timezone.now()
        current = self.credits
        
        # DECAY: If user hasn't been active, credits decay
        # Decay: 1% per day (or 100 credits per day, whichever is higher)
        if self.last_activity_at:
            days_inactive = (now - self.last_activity_at).total_seconds() / 86400
            
            if days_inactive > 0:
                # Decay: 1% per day, minimum 100 credits per day
                daily_decay_rate = Decimal('0.01')  # 1% per day
                daily_decay_min = Decimal('100.00')  # Minimum 100 credits per day
                
                # Calculate decay
                decay_amount = max(
                    current * daily_decay_rate * Decimal(str(days_inactive)),
                    daily_decay_min * Decimal(str(min(days_inactive, 1)))  # At least 100 per day
                )
                
                current = max(Decimal('0.00'), current - decay_amount)
        
        # REGENERATION: If credits are below base, regenerate slowly
        # Regeneration: 100 credits per hour (or 2,400 per day)
        if current < self.base_credits:
            hours_since_last_activity = (now - self.last_activity_at).total_seconds() / 3600 if self.last_activity_at else 0
            
            if hours_since_last_activity > 0:
                # Regenerate 100 credits per hour
                regen_rate = Decimal('100.00')  # 100 credits per hour
                regen_amount = regen_rate * Decimal(str(min(hours_since_last_activity, 24)))  # Max 24 hours at once
                
                current = min(self.max_credits, current + regen_amount)
        
        return current
    
    def update_credits_from_trade(self, amount_change):
        """
        Update credits when a trade happens.
        Uses raw stored credits (not decay/regen) so deductions are correct.
        """
        # Use raw stored credits - regeneration/decay are display-only
        current = self.credits
        
        # Apply the trade
        new_credits = current + Decimal(str(amount_change))
        
        # Update stored credits
        self.credits = max(Decimal('0.00'), new_credits)
        self.base_credits = self.credits  # Update base for regeneration calculation
        self.last_activity_at = timezone.now()  # Reset decay timer
        self.save()
        
        return self.credits
    
    def calculate_points(self):
        """
        Calculate total points based on performance.
        
        Formula:
        - Base: 100 points per correct prediction + 50 per market traded
        - ROI Bonus: (ROI% / 10) * base_points
        - Accuracy Bonus: (accuracy% / 10) * base_points
        - Streak Bonus: win_streak * 50 (capped at 500)
        - Volume Bonus: 1 point per 100 credits traded
        """
        base = (self.markets_predicted_correctly * 100) + (self.total_markets_traded * 50)
        
        roi_bonus = Decimal('0.00')
        if self.roi_percentage > 0:
            roi_bonus = (self.roi_percentage / Decimal('10')) * base
        
        accuracy_bonus = Decimal('0.00')
        if self.accuracy_percentage > 0:
            accuracy_bonus = (self.accuracy_percentage / Decimal('10')) * base
        
        streak_bonus = min(self.win_streak * 50, 500)
        
        # Get volume from profile
        volume_bonus = Decimal('0.00')
        if hasattr(self, 'profile'):
            volume_bonus = self.profile.total_volume_traded / Decimal('100')
        
        total = base + roi_bonus + accuracy_bonus + Decimal(str(streak_bonus)) + volume_bonus
        return total.quantize(Decimal('0.01'))
    
    def update_points(self):
        """Recalculate and update total points."""
        self.total_points = self.calculate_points()
        self.save(update_fields=['total_points'])
    
    def update_stats_after_market_resolution(self, market, was_correct):
        """
        Update user stats when a market is resolved.
        Called when a market the user traded in gets resolved.
        """
        self.total_markets_traded += 1
        
        if was_correct:
            self.markets_predicted_correctly += 1
            self.win_streak += 1
            if self.win_streak > self.best_win_streak:
                self.best_win_streak = self.win_streak
        else:
            self.win_streak = 0  # Reset streak on loss
        
        # Update accuracy
        if self.total_markets_traded > 0:
            self.accuracy_percentage = (
                Decimal(str(self.markets_predicted_correctly)) / 
                Decimal(str(self.total_markets_traded)) * 
                Decimal('100')
            ).quantize(Decimal('0.01'))
        
        # Update ROI (simplified - can be enhanced)
        if hasattr(self, 'profile'):
            initial_credits = Decimal('10000.00')
            current_credits = self.get_current_credits()
            if initial_credits > 0:
                self.roi_percentage = (
                    ((current_credits - initial_credits) / initial_credits) * 
                    Decimal('100')
                ).quantize(Decimal('0.01'))
        
        self.update_points()
        self.save()


class UserProfile(models.Model):
    """Extended user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    mpesa_number = models.CharField(max_length=20, blank=True, help_text="M-Pesa phone number (for future use)")
    total_volume_traded = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_profit_loss = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"



