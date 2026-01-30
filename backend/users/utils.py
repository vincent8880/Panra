"""
Shared utility functions for user-related operations.
"""
from decouple import config
import os


def get_frontend_url(request=None):
    """
    Get the frontend URL, with Railway detection fallback.
    
    This function is used by both the adapter and context processors to ensure
    consistent frontend URL detection across the application.
    """
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
        elif request:
            # Fallback: try to infer from request
            try:
                backend_domain = request.build_absolute_uri('/').split('/')[2]
                if 'panra.up.railway.app' in backend_domain:
                    frontend = 'https://panra-ke.up.railway.app'
            except:
                pass
    
    return frontend

