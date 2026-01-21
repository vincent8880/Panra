from django.contrib import admin
from .models import Order, Trade, Position


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'market', 'side', 'order_type', 'price', 'quantity', 'status', 'created_at']
    list_filter = ['status', 'side', 'order_type', 'created_at']
    search_fields = ['user__username', 'market__title']
    readonly_fields = ['filled_quantity', 'filled_at']


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'market', 'buyer', 'seller', 'side', 'price', 'quantity', 'executed_at']
    list_filter = ['side', 'executed_at']
    search_fields = ['market__title', 'buyer__username', 'seller__username']
    readonly_fields = ['executed_at']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['user', 'market', 'yes_shares', 'no_shares', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'market__title']



