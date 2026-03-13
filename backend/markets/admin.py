from django.contrib import admin, messages
from .models import Market, MarketOutcome
from .settlement import settle_market


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'yes_price', 'no_price', 'total_volume', 'created_at', 'end_date']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'question', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['yes_price', 'no_price', 'total_volume', 'total_liquidity']
    actions = ['settle_as_yes', 'settle_as_no']

    def settle_as_yes(self, request, queryset):
        settled = 0
        for market in queryset:
            try:
                summary = settle_market(market, 'yes')
                settled += 1
            except ValueError as e:
                self.message_user(request, f"Could not settle '{market.slug}': {e}", level=messages.ERROR)
        if settled:
            self.message_user(request, f"Settled {settled} market(s) as YES.", level=messages.SUCCESS)

    settle_as_yes.short_description = "Settle selected markets as YES"

    def settle_as_no(self, request, queryset):
        settled = 0
        for market in queryset:
            try:
                summary = settle_market(market, 'no')
                settled += 1
            except ValueError as e:
                self.message_user(request, f"Could not settle '{market.slug}': {e}", level=messages.ERROR)
        if settled:
            self.message_user(request, f"Settled {settled} market(s) as NO.", level=messages.SUCCESS)

    settle_as_no.short_description = "Settle selected markets as NO"


@admin.register(MarketOutcome)
class MarketOutcomeAdmin(admin.ModelAdmin):
    list_display = ['market', 'name', 'price', 'volume']
    list_filter = ['market']



