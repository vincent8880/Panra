"""
Custom context processors for Django templates.
"""
from users.utils import get_frontend_url


def frontend_url(request):
    """Add FRONTEND_URL to template context."""
    # Use the same function as the adapter to ensure consistency
    frontend = get_frontend_url(request)
    return {
        'FRONTEND_URL': frontend,
    }

