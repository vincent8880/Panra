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
        Positive amount = gain, Negative = loss
        """
        
        # Get current effective credits
        current = self.get_current_credits()
        
        # Apply the trade
        new_credits = current + Decimal(str(amount_change))
        
        # Update stored credits
        self.credits = max(Decimal('0.00'), new_credits)
        self.base_credits = self.credits  # Update base for regeneration calculation
        self.last_activity_at = timezone.now()  # Reset decay timer
        self.save()
        
        return self.credits


class UserProfile(models.Model):
    """Extended user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    mpesa_number = models.CharField(max_length=20, blank=True, help_text="M-Pesa phone number (for future use)")
    total_volume_traded = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_profit_loss = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"



