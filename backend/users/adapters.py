"""
Custom allauth adapters to handle OAuth redirects to frontend.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from .utils import get_frontend_url
import logging

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter to redirect to frontend.
    """
    
    def get_login_redirect_url(self, request):
        """Redirect after login."""
        url = get_frontend_url(request)
        logger.info(f"AccountAdapter get_login_redirect_url returning: {url}")
        return url
    
    def get_logout_redirect_url(self, request):
        """Redirect after logout."""
        url = get_frontend_url(request)
        logger.info(f"AccountAdapter get_logout_redirect_url returning: {url}")
        return url
    
    def get_signup_redirect_url(self, request):
        """Redirect after signup."""
        url = f"{get_frontend_url(request)}/?signup=success"
        logger.info(f"AccountAdapter get_signup_redirect_url returning: {url}")
        return url


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to redirect to frontend after social login.
    """
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting a social account."""
        url = self._get_redirect_url(request)
        logger.info(f"get_connect_redirect_url returning: {url}")
        return url
    
    def get_login_redirect_url(self, request):
        """Redirect after successful social login."""
        url = self._get_redirect_url(request)
        logger.info(f"get_login_redirect_url returning: {url}")
        return url
    
    def get_signup_redirect_url(self, request):
        """Redirect after social signup."""
        url = self._get_redirect_url(request)
        logger.info(f"get_signup_redirect_url returning: {url}")
        return url
    
    def _get_redirect_url(self, request):
        """Build the redirect URL to frontend."""
        frontend = get_frontend_url(request)
        # Ensure clean URL construction
        redirect_url = f"{frontend}/?google_auth=success"
        return redirect_url
    
    def pre_social_login(self, request, sociallogin):
        """Called before social login completes."""
        logger.info(f"pre_social_login called for user: {sociallogin.user}")
        # If user is already logged in, connect the account
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """Handle authentication errors gracefully."""
        logger.warning(f"Social authentication error for {provider_id}: {error}, exception: {exception}")
        # Return None to let allauth handle the error display
        return None
    
    def save_user(self, request, sociallogin, form=None):
        """Save user after social login."""
        logger.info(f"save_user called")
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
            logger.info(f"Created username: {username}")
        return user

