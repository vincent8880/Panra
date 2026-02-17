# Fix Google Auth - One Step

## The Problem
Google Console has the wrong redirect URI.

## The Fix (30 seconds)

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", change:
   - FROM: `https://panra.up.railway.app/accounts/google/login/callback/`
   - TO: `https://panra.up.railway.app/auth/google/callback/`
4. Save

That's it. Try logging in again.






