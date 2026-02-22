from django.contrib import admin
from .models import Market, MarketOutcome


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'yes_price', 'no_price', 'total_volume', 'created_at', 'end_date']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'question', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['yes_price', 'no_price', 'total_volume', 'total_liquidity']
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'question', 'resolution_criteria', 'description', 'category', 'image_url')}),
        ('Status', {'fields': ('status', 'resolution', 'end_date', 'resolution_date')}),
        ('Stats', {'fields': ('yes_price', 'no_price', 'total_volume', 'total_liquidity')}),
        ('Creator', {'fields': ('created_by',)}),
    )


@admin.register(MarketOutcome)
class MarketOutcomeAdmin(admin.ModelAdmin):
    list_display = ['market', 'name', 'price', 'volume']
    list_filter = ['market']



