"""
Custom context processors for Django templates.
"""
from django.conf import settings
from decouple import config


def frontend_url(request):
    """Add FRONTEND_URL to template context."""
    # Use the same logic as settings.py to get FRONTEND_URL
    # This ensures consistency and respects environment variables
    frontend = config('FRONTEND_URL', default='http://localhost:3000')
    return {
        'FRONTEND_URL': frontend,
    }

