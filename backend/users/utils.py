"""
Shared utility functions for user-related operations.
"""
from decouple import config
import os
import logging

logger = logging.getLogger(__name__)


def get_frontend_url(request=None):
    """
    Get the frontend URL, with Railway detection fallback.
    
    Priority:
    1. FRONTEND_URL environment variable (explicitly set)
    2. Hardcoded Railway frontend (if on Railway)
    3. Default to localhost (development)
    """
    # Check environment variable first
    frontend = config('FRONTEND_URL', default=None)
    
    # If explicitly set and not localhost, use it
    if frontend and frontend != 'http://localhost:3000':
        logger.info(f"Using FRONTEND_URL from env: {frontend}")
        return frontend.rstrip('/')  # Remove trailing slash
    
    # Check if we're on Railway
    is_railway = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID')
    
    if is_railway:
        # Hardcoded for your deployment - CHANGE THIS to your actual frontend URL
        frontend_url = 'https://panra-ke.up.railway.app'
        logger.info(f"On Railway, using hardcoded frontend: {frontend_url}")
        return frontend_url
    
    # Development fallback
    dev_url = 'http://localhost:3000'
    logger.info(f"Using development frontend: {dev_url}")
    return dev_url

