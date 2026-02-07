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
    """Handle the Google OAuth callback and then send user back to the frontend."""

    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')
        frontend_url = get_frontend_url()

        if error or not code:
            return self._redirect_response(f"{frontend_url}/login?google_auth=error")

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
                timeout=10,
            )

            if token_response.status_code != 200:
                return self._redirect_response(f"{frontend_url}/login?google_auth=error")

            tokens = token_response.json()
            access_token = tokens.get('access_token')

            # Get user info from Google
            userinfo_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10,
            )

            if userinfo_response.status_code != 200:
                return self._redirect_response(f"{frontend_url}/login?google_auth=error")

            userinfo = userinfo_response.json()
            google_id = userinfo.get('id')
            email = userinfo.get('email')
            name = userinfo.get('name', '')

            logger.info(f"Google user info: id={google_id}, email={email}")

            # Find or create user
            user = self._get_or_create_user(google_id, email, name, access_token, tokens)
            if not user:
                logger.error("Failed to get or create user")
                return self._redirect_response(f"{frontend_url}/login?google_auth=error")
            
            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            logger.info(f"User {user.username} logged in successfully, session key: {request.session.session_key}")
            
            # Force session save
            request.session.save()
            
            return self._redirect_response(f"{frontend_url}/login?google_auth=success")

        except Exception as e:
            logger.exception(f"OAuth error: {e}")
            return self._redirect_response(f"{frontend_url}/login?google_auth=error")
    
    def _get_or_create_user(self, google_id, email, name, access_token, tokens):
        """Get existing user or create new one."""
        try:
            # Get or create SocialApp first (required for tokens)
            try:
                app = SocialApp.objects.get(provider='google')
            except SocialApp.DoesNotExist:
                logger.warning("SocialApp for google not found, creating it")
                client_id, client_secret = get_google_credentials()
                if not client_id:
                    logger.error("Cannot create SocialApp: no credentials")
                    return None
                from django.contrib.sites.models import Site
                site = Site.objects.get_current()
                app = SocialApp.objects.create(
                    provider='google',
                    name='Google',
                    client_id=client_id,
                    secret=client_secret,
                )
                app.sites.add(site)
                logger.info("Created SocialApp for google")
            
            # Check if we have a social account for this Google ID (most common case - existing Google login)
            try:
                social_account = SocialAccount.objects.get(provider='google', uid=google_id)
                user = social_account.user
                logger.info(f"Found existing user for Google ID: {user.username}")
                
                # Update token
                SocialToken.objects.update_or_create(
                    account=social_account,
                    app=app,
                    defaults={
                        'token': access_token,
                        'token_secret': tokens.get('refresh_token', ''),
                    }
                )
                return user
            except SocialAccount.DoesNotExist:
                pass
            
            # Check if user exists with this email (link Google to existing email account)
            if email:
                try:
                    user = User.objects.get(email=email)
                    logger.info(f"Found existing user by email: {user.username}, linking Google account")
                    
                    # Use get_or_create to avoid duplicate SocialAccount errors
                    social_account, created = SocialAccount.objects.get_or_create(
                        provider='google',
                        uid=google_id,
                        defaults={
                            'user': user,
                            'extra_data': {'email': email, 'name': name}
                        }
                    )
                    
                    # If it already existed but was linked to different user, update it
                    if not created and social_account.user != user:
                        logger.warning(f"SocialAccount for Google ID {google_id} was linked to different user, updating")
                        social_account.user = user
                        social_account.extra_data = {'email': email, 'name': name}
                        social_account.save()
                    
                    # Update or create token
                    SocialToken.objects.update_or_create(
                        account=social_account,
                        app=app,
                        defaults={
                            'token': access_token,
                            'token_secret': tokens.get('refresh_token', ''),
                        }
                    )
                    
                    return user
                except User.DoesNotExist:
                    pass
                except User.MultipleObjectsReturned:
                    # Multiple users with same email - take the first one
                    logger.warning(f"Multiple users with email {email}, using first one")
                    user = User.objects.filter(email=email).first()
                    social_account, _ = SocialAccount.objects.get_or_create(
                        provider='google',
                        uid=google_id,
                        defaults={
                            'user': user,
                            'extra_data': {'email': email, 'name': name}
                        }
                    )
                    if social_account.user != user:
                        social_account.user = user
                        social_account.save()
                    SocialToken.objects.update_or_create(
                        account=social_account,
                        app=app,
                        defaults={
                            'token': access_token,
                            'token_secret': tokens.get('refresh_token', ''),
                        }
                    )
                    return user
            
            # Create new user (first time Google login)
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
            
            # Create token
            SocialToken.objects.create(
                account=social_account,
                app=app,
                token=access_token,
                token_secret=tokens.get('refresh_token', ''),
            )
            
            return user
            
        except Exception as e:
            logger.exception(f"Error creating/getting user: {e}")
            return None
    
    def _redirect_response(self, url):
        """Return a tiny HTML page that immediately redirects via JavaScript.

        We use this instead of an HTTP 302 to avoid the corrupted-content issue
        we've seen with redirects through the Railway proxy.
        """
        import html as html_module
        import json

        url_html = html_module.escape(url)
        url_js = json.dumps(url)

        html = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="0;url={url_html}" />
    <title>Redirecting…</title>
    <script>
      // Immediate redirect - try multiple methods
      (function() {{
        var target = {url_js};
        // Try replace first (doesn't add to history)
        try {{
          window.location.replace(target);
        }} catch (e) {{
          // Fallback to href
          window.location.href = target;
        }}
        // Backup: if still here after 100ms, force redirect
        setTimeout(function() {{
          window.location.href = target;
        }}, 100);
        // Last resort: if still here after 500ms, use top-level
        setTimeout(function() {{
          if (window.top) {{
            window.top.location = target;
          }} else {{
            window.location = target;
          }}
        }}, 500);
      }})();
    </script>
  </head>
  <body style="background:#0a0a0a;color:#fff;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;">
    <div style="text-align:center;">
      <p>Login successful! Redirecting…</p>
      <p style="margin-top:20px;">
        <a href="{url_html}" style="color:#3b82f6;text-decoration:underline;font-size:16px;font-weight:500;">Click here if you're not redirected automatically</a>
      </p>
    </div>
  </body>
</html>"""

        response = HttpResponse(html, content_type="text/html; charset=utf-8")
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response
    


