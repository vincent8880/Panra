# Google OAuth Fix - Step by Step

## The Problem

You're seeing "Third-Party Login Failure" because Google is redirecting to the **wrong URL**. 

Our custom OAuth handler is at: `/auth/google/callback/`
But Google Console is configured to redirect to: `/accounts/google/login/callback/` (allauth's URL)

When Google redirects to the allauth URL, allauth tries to handle it but fails, showing the error template.

## The Fix

### Step 1: Update Google Console Redirect URIs

Go to: https://console.cloud.google.com/apis/credentials

1. Find your OAuth 2.0 Client ID
2. Click Edit
3. Under "Authorized redirect URIs", **REMOVE** these old URLs:
   - `http://localhost:8001/accounts/google/login/callback/`
   - `https://panra.up.railway.app/accounts/google/login/callback/`

4. **ADD** these new URLs (our custom handler):
   - `http://localhost:8001/auth/google/callback/` (for local dev)
   - `https://panra.up.railway.app/auth/google/callback/` (for production)

5. Save the changes

### Step 2: Verify Backend Configuration

The backend code is already set up correctly at `/auth/google/callback/`. No changes needed.

### Step 3: Test

1. Try logging in with Google
2. Check Railway logs to see detailed error messages if it still fails
3. The logs will now show exactly what step failed

## Why This Will Work

- Our custom handler (`/auth/google/callback/`) properly processes the OAuth flow
- It creates users, logs them in, and redirects to the frontend
- It has comprehensive error handling and logging
- It bypasses allauth's redirect mechanism that was causing issues

## If It Still Fails

Check Railway logs for messages starting with "GoogleOAuthCallbackView" - they will show exactly where it's failing.


