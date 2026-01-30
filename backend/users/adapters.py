"""
Custom allauth adapter to handle Google OAuth redirects to frontend.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpResponseRedirect
from decouple import config
import os


def get_frontend_url(request=None):
    """Get the frontend URL, with Railway detection fallback."""
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
            backend_domain = request.build_absolute_uri('/').split('/')[2]
            if 'panra.up.railway.app' in backend_domain:
                frontend = 'https://panra-ke.up.railway.app'
    
    return frontend


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to redirect to frontend after social login.
    """
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting a social account."""
        frontend = get_frontend_url(request)
        return f"{frontend}/?google_auth=success"
    
    def get_login_redirect_url(self, request):
        """Redirect after successful social login."""
        frontend = get_frontend_url(request)
        return f"{frontend}/?google_auth=success"
    
    def get_signup_redirect_url(self, request):
        """Redirect after social signup."""
        frontend = get_frontend_url(request)
        return f"{frontend}/?google_auth=success"
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login completes."""
        # If user is already logged in, connect the account
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
    
    def save_user(self, request, sociallogin, form=None):
        """Save user after social login."""
        user = super().save_user(request, sociallogin, form)
        # Ensure user has a username if not provided
        if not user.username:
            email = user.email or ''
            username = email.split('@')[0] if email else f"google_{sociallogin.account.uid[:8]}"
            # Make username unique
            base_username = username
            counter = 1
            from .models import User
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
            user.save()
        return user

