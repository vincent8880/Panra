"""
Custom Google OAuth implementation that bypasses allauth's redirect mechanism.
This avoids the "Corrupted Content Error" by returning clean HTML responses.
"""
import requests
import logging
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse
from django.views import View
from decouple import config
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from allauth.socialaccount.providers.google.provider import GoogleProvider
from users.models import User

logger = logging.getLogger(__name__)


def get_frontend_url():
    """Get the frontend URL."""
    import os
    frontend = config('FRONTEND_URL', default=None)
    if frontend and frontend != 'http://localhost:3000':
        return frontend
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID'):
        return 'https://panra-ke.up.railway.app'
    return 'http://localhost:3000'


def get_google_credentials():
    """Get Google OAuth credentials from database or env."""
    try:
        app = SocialApp.objects.get(provider='google')
        return app.client_id, app.secret
    except SocialApp.DoesNotExist:
        client_id = config('GOOGLE_OAUTH_CLIENT_ID', default='')
        secret = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')
        return client_id, secret


class GoogleOAuthStartView(View):
    """Start the Google OAuth flow."""
    
    def get(self, request):
        client_id, _ = get_google_credentials()
        
        if not client_id:
            return self._error_response("Google OAuth not configured")
        
        # Build the callback URL
        callback_url = request.build_absolute_uri('/auth/google/callback/')
        
        # Build Google OAuth URL
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={callback_url}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"access_type=online"
        )
        
        # Return HTML that redirects - avoids HTTP redirect issues
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting to Google...</title>
    <meta http-equiv="refresh" content="0;url={google_auth_url}">
</head>
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="text-align:center;">
        <p>Redirecting to Google...</p>
        <p><a href="{google_auth_url}" style="color:#3b82f6;">Click here if not redirected</a></p>
    </div>
</body>
</html>'''
        return HttpResponse(html, content_type='text/html; charset=utf-8')
    
    def _error_response(self, message):
        frontend_url = get_frontend_url()
        html = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Error</title></head>
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="text-align:center;">
        <h1>Error</h1>
        <p>{message}</p>
        <p><a href="{frontend_url}/login" style="color:#3b82f6;">Back to Login</a></p>
    </div>
</body>
</html>'''
        return HttpResponse(html, content_type='text/html; charset=utf-8')


class GoogleOAuthCallbackView(View):
    """Handle the Google OAuth callback."""
    
    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')
        
        frontend_url = get_frontend_url()
        
        if error:
            logger.warning(f"Google OAuth error: {error}")
            return self._redirect_response(f"{frontend_url}/?google_auth=error&reason={error}")
        
        if not code:
            logger.warning("No code in Google callback")
            return self._redirect_response(f"{frontend_url}/?google_auth=error&reason=no_code")
        
        try:
            # Exchange code for tokens
            client_id, client_secret = get_google_credentials()
            callback_url = request.build_absolute_uri('/auth/google/callback/')
            
            token_response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'code': code,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': callback_url,
                    'grant_type': 'authorization_code',
                },
                timeout=10
            )
            
            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.text}")
                return self._redirect_response(f"{frontend_url}/?google_auth=error&reason=token_exchange_failed")
            
            tokens = token_response.json()
            access_token = tokens.get('access_token')
            
            # Get user info from Google
            userinfo_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if userinfo_response.status_code != 200:
                logger.error(f"Failed to get user info: {userinfo_response.text}")
                return self._redirect_response(f"{frontend_url}/?google_auth=error&reason=userinfo_failed")
            
            userinfo = userinfo_response.json()
            google_id = userinfo.get('id')
            email = userinfo.get('email')
            name = userinfo.get('name', '')
            
            logger.info(f"Google user info: id={google_id}, email={email}")
            
            # Find or create user
            user = self._get_or_create_user(google_id, email, name, access_token, tokens)
            
            if user:
                # Log the user in
                login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
                logger.info(f"User {user.username} logged in via Google")
                return self._redirect_response(f"{frontend_url}/?google_auth=success")
            else:
                return self._redirect_response(f"{frontend_url}/?google_auth=error&reason=user_creation_failed")
                
        except Exception as e:
            logger.exception(f"Error in Google OAuth callback: {e}")
            return self._redirect_response(f"{frontend_url}/?google_auth=error&reason=exception")
    
    def _get_or_create_user(self, google_id, email, name, access_token, tokens):
        """Get existing user or create new one."""
        try:
            # Check if we have a social account for this Google ID
            try:
                social_account = SocialAccount.objects.get(provider='google', uid=google_id)
                user = social_account.user
                logger.info(f"Found existing user for Google ID: {user.username}")
                
                # Update token
                SocialToken.objects.update_or_create(
                    account=social_account,
                    defaults={
                        'token': access_token,
                        'token_secret': tokens.get('refresh_token', ''),
                    }
                )
                return user
            except SocialAccount.DoesNotExist:
                pass
            
            # Check if user exists with this email
            if email:
                try:
                    user = User.objects.get(email=email)
                    logger.info(f"Found existing user by email: {user.username}")
                    
                    # Link Google account to existing user
                    social_account = SocialAccount.objects.create(
                        user=user,
                        provider='google',
                        uid=google_id,
                        extra_data={'email': email, 'name': name}
                    )
                    
                    # Get or create SocialApp
                    try:
                        app = SocialApp.objects.get(provider='google')
                    except SocialApp.DoesNotExist:
                        app = None
                    
                    if app:
                        SocialToken.objects.create(
                            account=social_account,
                            app=app,
                            token=access_token,
                            token_secret=tokens.get('refresh_token', ''),
                        )
                    
                    return user
                except User.DoesNotExist:
                    pass
            
            # Create new user
            username = email.split('@')[0] if email else f"google_{google_id[:8]}"
            
            # Make username unique
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email or f"{google_id}@google.oauth",
            )
            logger.info(f"Created new user: {user.username}")
            
            # Create social account
            social_account = SocialAccount.objects.create(
                user=user,
                provider='google',
                uid=google_id,
                extra_data={'email': email, 'name': name}
            )
            
            # Get or create SocialApp and token
            try:
                app = SocialApp.objects.get(provider='google')
                SocialToken.objects.create(
                    account=social_account,
                    app=app,
                    token=access_token,
                    token_secret=tokens.get('refresh_token', ''),
                )
            except SocialApp.DoesNotExist:
                pass
            
            return user
            
        except Exception as e:
            logger.exception(f"Error creating/getting user: {e}")
            return None
    
    def _redirect_response(self, url):
        """Return an HTML page that redirects via meta refresh and JavaScript."""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <meta http-equiv="refresh" content="0;url={url}">
    <script>window.location.href = "{url}";</script>
</head>
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="text-align:center;">
        <div style="width:40px;height:40px;border:3px solid #333;border-top-color:#3b82f6;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 20px;"></div>
        <p>Completing login...</p>
        <p style="margin-top:20px;font-size:12px;"><a href="{url}" style="color:#3b82f6;">Click here if not redirected</a></p>
    </div>
    <style>@keyframes spin {{ to {{ transform: rotate(360deg); }} }}</style>
</body>
</html>'''
        response = HttpResponse(html, content_type='text/html; charset=utf-8')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response['Pragma'] = 'no-cache'
        return response

