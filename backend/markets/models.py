from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Market(models.Model):
    """Prediction market model."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ]
    
    RESOLUTION_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('pending', 'Pending'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    slug = models.SlugField(unique=True, max_length=500)
    
    # Market details
    question = models.CharField(max_length=500, help_text="The prediction question")
    resolution_criteria = models.TextField(
        blank=True,
        help_text="When does this market resolve to YES? e.g. 'Resolves to YES when Kenya wins AFCON 2024.'"
    )
    category = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(blank=True, null=True)
    
    # Market status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, default='pending')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(help_text="When the market closes for trading")
    resolution_date = models.DateTimeField(null=True, blank=True, help_text="When the market was resolved")
    
    # Creator
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_markets')
    
    # Market stats
    total_volume = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    total_liquidity = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    # Outcome prices (0.00 to 1.00)
    yes_price = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.5000,
        validators=[MinValueValidator(0.0000), MaxValueValidator(1.0000)]
    )
    no_price = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.5000,
        validators=[MinValueValidator(0.0000), MaxValueValidator(1.0000)]
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Ensure yes_price + no_price = 1.00
        if self.yes_price + self.no_price != 1.00:
            self.no_price = 1.00 - self.yes_price
        super().save(*args, **kwargs)


class MarketOutcome(models.Model):
    """Individual outcome for a market (for markets with multiple outcomes)."""
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='outcomes')
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.0000,
        validators=[MinValueValidator(0.0000), MaxValueValidator(1.0000)]
    )
    volume = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.market.title} - {self.name}"



