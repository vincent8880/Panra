"""
Token-based authentication for REST API.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_utils import verify_jwt_token
import logging

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    JWT token authentication.
    Looks for token in Authorization header: "Bearer <token>"
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split('Bearer ')[1].strip()
        
        if not token:
            return None
        
        user = verify_jwt_token(token)
        
        if not user:
            raise AuthenticationFailed('Invalid or expired token')
        
        return (user, None)  # (user, auth) tuple

