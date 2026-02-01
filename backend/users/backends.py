"""
Custom authentication backends to support email/username login.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows login with either email or username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username first
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                # If not found, try email
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                # User doesn't exist
                return None
            except User.MultipleObjectsReturned:
                # Multiple users with same email (shouldn't happen, but handle it)
                return None
        
        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None


