from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from markets.models import Market

User = get_user_model()


class Order(models.Model):
    """Trading order model."""
    
    SIDE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    TYPE_CHOICES = [
        ('limit', 'Limit'),
        ('market', 'Market'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
        ('partial', 'Partially Filled'),
    ]
    
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)  # 'yes' or 'no'
    order_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='limit')
    price = models.DecimalField(
        max_digits=5, 
        decimal_places=4,
        validators=[MinValueValidator(0.0000)],
        help_text="Price per share (0.00 to 1.00)"
    )
    quantity = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Number of shares"
    )
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    filled_quantity = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    filled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['market', 'status', 'side', 'price']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.side.upper()} {self.quantity} @ {self.price}"


class Trade(models.Model):
    """Executed trade model."""
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='trades')
    buy_order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='buy_trades'
    )
    sell_order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='sell_trades'
    )
    
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='buy_trades')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sell_trades')
    
    # Trade details
    side = models.CharField(max_length=10)  # 'yes' or 'no'
    price = models.DecimalField(max_digits=5, decimal_places=4)
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    total_value = models.DecimalField(max_digits=20, decimal_places=2)
    
    # Timestamp
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['market', '-executed_at']),
            models.Index(fields=['buyer', '-executed_at']),
            models.Index(fields=['seller', '-executed_at']),
        ]
    
    def __str__(self):
        return f"Trade: {self.quantity} @ {self.price} on {self.market.title}"


class Position(models.Model):
    """User's position in a market."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='positions')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='positions')
    
    # Position details
    yes_shares = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    no_shares = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    # Average cost
    yes_avg_cost = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    no_avg_cost = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    
    # Updated timestamp
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'market']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['market']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.market.title}: YES={self.yes_shares}, NO={self.no_shares}"



