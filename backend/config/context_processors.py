"""
Custom context processors for Django templates.
"""
from django.conf import settings
from decouple import config
import os


def frontend_url(request):
    """Add FRONTEND_URL to template context."""
    # Use the same logic as settings.py to get FRONTEND_URL
    # This ensures consistency and respects environment variables
    frontend = config('FRONTEND_URL', default='http://localhost:3000')
    
    # If on Railway and FRONTEND_URL not explicitly set, try to detect it
    if (os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID')) and frontend == 'http://localhost:3000':
        # Try to get from Railway environment variable or use common Railway frontend pattern
        railway_frontend = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_frontend:
            # If it's the backend domain, try to infer frontend domain
            if 'panra.up.railway.app' in railway_frontend:
                frontend = 'https://panra-ke.up.railway.app'
            else:
                frontend = f'https://{railway_frontend}'
    
    return {
        'FRONTEND_URL': frontend,
    }

