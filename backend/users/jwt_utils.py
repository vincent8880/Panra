"""
JWT token utilities for token-based authentication.
"""
import jwt
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_jwt_token(user):
    """
    Generate a JWT token for a user.
    
    Args:
        user: Django User instance
        
    Returns:
        str: JWT token string
    """
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7),  # 7 days expiry
    }
    
    secret_key = settings.SECRET_KEY
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    # jwt.encode returns bytes in older versions, string in newer
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    logger.info(f"Generated JWT token for user {user.username}")
    return token


def verify_jwt_token(token):
    """
    Verify a JWT token and return the user.
    
    Args:
        token: JWT token string
        
    Returns:
        User instance if valid, None otherwise
    """
    try:
        secret_key = settings.SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        user = User.objects.get(id=user_id, is_active=True)
        return user
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except User.DoesNotExist:
        logger.warning(f"User from JWT token does not exist: {user_id}")
        return None
    except Exception as e:
        logger.exception(f"Error verifying JWT token: {e}")
        return None


