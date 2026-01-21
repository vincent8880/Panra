from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'credits', 'current_credits_display', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'date_joined']
    readonly_fields = ['current_credits_display', 'last_activity_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Practice Credits', {
            'fields': ('credits', 'current_credits_display', 'base_credits', 'max_credits', 'last_activity_at'),
            'description': 'Practice credits system (not real money)'
        }),
    )
    
    def current_credits_display(self, obj):
        """Display current credits after decay/regeneration calculation."""
        return f"{obj.get_current_credits():.2f}"
    current_credits_display.short_description = 'Current Credits'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'mpesa_number', 'total_volume_traded']
    search_fields = ['user__username', 'phone_number', 'mpesa_number']



