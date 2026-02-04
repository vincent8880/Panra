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
        import html as html_module
        import json
        from urllib.parse import urlencode, quote
        
        client_id, _ = get_google_credentials()
        
        if not client_id:
            return self._error_response("Google OAuth not configured")
        
        # Build the callback URL
        callback_url = request.build_absolute_uri('/auth/google/callback/')
        
        logger.info(f"Google OAuth start - callback URL: {callback_url}")
        
        # Build Google OAuth URL using proper URL encoding
        params = {
            'client_id': client_id,
            'redirect_uri': callback_url,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'online',
        }
        google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        
        # Properly escape for HTML and JS
        url_html = html_module.escape(google_auth_url)
        url_js = json.dumps(google_auth_url)
        
        # Return HTML that redirects - avoids HTTP redirect issues
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting to Google...</title>
</head>
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="text-align:center;">
        <div style="width:40px;height:40px;border:3px solid #333;border-top-color:#4285F4;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 20px;"></div>
        <p>Redirecting to Google...</p>
        <p style="margin-top:20px;font-size:12px;"><a href="{url_html}" id="google-link" style="color:#3b82f6;">Click here if not redirected</a></p>
    </div>
    <style>@keyframes spin {{ to {{ transform: rotate(360deg); }} }}</style>
    <script type="text/javascript">
        (function() {{
            var targetUrl = {url_js};
            console.log("Redirecting to Google:", targetUrl);
            window.location.replace(targetUrl);
        }})();
    </script>
</body>
</html>'''
        response = HttpResponse(html, content_type='text/html; charset=utf-8')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return response
    
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
        """
        TEMPORARY: minimal response to debug 'Corrupted Content Error'.
        
        If this simple HTML still triggers corruption, the problem is at the
        HTTP/proxy level, not in our view logic.
        """
        logger.info("GoogleOAuthCallbackView hit with query params: %s", request.GET.dict())
        html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Google OAuth Callback</title></head>
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
  <div style="text-align:center;">
    <h1>Google OAuth Callback Reached</h1>
    <p>This is a temporary debug page. The backend is reachable.</p>
    <p>You can close this tab and go back to the app.</p>
  </div>
</body>
</html>"""
        return HttpResponse(html, content_type="text/html; charset=utf-8")
    
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
        """Return an HTTP redirect response."""
        from django.http import HttpResponseRedirect
        
        logger.info(f"Redirecting to: {url}")
        
        # Try a simple HTTP redirect - our custom OAuth flow should work
        return HttpResponseRedirect(url)


