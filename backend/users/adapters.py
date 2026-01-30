"""
Custom allauth adapter to handle Google OAuth redirects to frontend.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .utils import get_frontend_url


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
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """Handle authentication errors gracefully."""
        # Log the error but don't raise - let the error template handle it
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Social authentication error for {provider_id}: {error}")
        # Return None to let allauth handle the error display
        return None
    
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

