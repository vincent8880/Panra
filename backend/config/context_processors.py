"""
Custom context processors for Django templates.
"""
from django.conf import settings


def frontend_url(request):
    """Add FRONTEND_URL to template context."""
    return {
        'FRONTEND_URL': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
    }

