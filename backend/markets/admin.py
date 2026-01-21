from django.contrib import admin
from .models import Market, MarketOutcome


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'yes_price', 'no_price', 'total_volume', 'created_at', 'end_date']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'question', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['yes_price', 'no_price', 'total_volume', 'total_liquidity']


@admin.register(MarketOutcome)
class MarketOutcomeAdmin(admin.ModelAdmin):
    list_display = ['market', 'name', 'price', 'volume']
    list_filter = ['market']



