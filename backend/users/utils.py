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
    
    Priority:
    1. FRONTEND_URL environment variable (explicitly set)
    2. Railway detection (if on Railway and not explicitly set)
    3. Default to localhost (development)
    """
    frontend = config('FRONTEND_URL', default=None)
    
    # If explicitly set, use it
    if frontend and frontend != 'http://localhost:3000':
        return frontend
    
    # Check if we're on Railway
    is_railway = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID')
    
    if is_railway:
        # Try multiple methods to detect frontend URL on Railway
        # Method 1: Check for explicit Railway frontend URL env var
        railway_frontend = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        
        # Method 2: Infer from backend domain in request
        if request:
            try:
                backend_domain = request.build_absolute_uri('/').split('/')[2]
                # If backend is panra.up.railway.app, frontend is likely panra-ke.up.railway.app
                if 'panra.up.railway.app' in backend_domain:
                    return 'https://panra-ke.up.railway.app'
                # If backend has a pattern, try to infer frontend
                elif '.up.railway.app' in backend_domain:
                    # Common pattern: backend might be panra.up.railway.app, frontend might be panra-ke.up.railway.app
                    # Or they might share the same base
                    parts = backend_domain.split('.')
                    if len(parts) >= 3:
                        # Try common frontend patterns
                        base = parts[0]  # e.g., 'panra'
                        possible_frontends = [
                            f'https://{base}-ke.up.railway.app',  # panra-ke
                            f'https://{base}-frontend.up.railway.app',  # panra-frontend
                            f'https://{base}-web.up.railway.app',  # panra-web
                        ]
                        # Return first one (most common pattern)
                        return possible_frontends[0]
            except Exception:
                pass
        
        # Method 3: Use railway_frontend if found
        if railway_frontend:
            if 'panra.up.railway.app' in railway_frontend:
                return 'https://panra-ke.up.railway.app'
            elif not railway_frontend.startswith('http'):
                return f'https://{railway_frontend}'
            else:
                return railway_frontend
        
        # Method 4: Hardcoded fallback for known Railway deployment
        # This is a safety net - should be overridden by env var
        return 'https://panra-ke.up.railway.app'
    
    # Development fallback
    return frontend or 'http://localhost:3000'

