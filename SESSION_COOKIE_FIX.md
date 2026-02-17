# Session Cookie Fix for Cross-Domain Authentication

## Problem
Backend and frontend are on different domains (e.g., `panra.up.railway.app` vs `panra-ke.up.railway.app`). Django session cookies weren't being sent with cross-domain requests.

## Solution Applied

### 1. Session Cookie Settings (settings.py)
- **Production (Railway)**: `SESSION_COOKIE_SAMESITE = 'None'` with `SESSION_COOKIE_SECURE = True`
  - Allows cookies to be sent cross-domain
  - Requires HTTPS (which Railway provides)
- **Development**: `SESSION_COOKIE_SAMESITE = 'Lax'` with `SESSION_COOKIE_SECURE = False`
  - Works for same-origin or localhost

### 2. CSRF Cookie Settings
- Same pattern: `None` + `Secure=True` in production, `Lax` in dev
- Allows CSRF tokens to work cross-domain

### 3. CORS Configuration
- `CORS_ALLOW_CREDENTIALS = True` (already set)
- Frontend uses `withCredentials: true` in axios (already set)
- Explicit CORS headers configured

## How It Works Now

1. User logs in via Google OAuth on backend domain
2. Backend sets session cookie with `SameSite=None; Secure`
3. Browser stores cookie for backend domain
4. Frontend makes API calls with `withCredentials: true`
5. Browser includes session cookie in cross-domain requests
6. Backend authenticates user via session

## Testing

After deployment, check:
1. Browser DevTools → Application → Cookies
2. Should see session cookie for backend domain with `SameSite=None`
3. Network tab → API requests should include `Cookie` header
4. User should be authenticated after Google login

## Railway Environment Variables

Make sure these are set:
- `FRONTEND_URL=https://panra-ke.up.railway.app` (or your frontend URL)
- `CORS_ALLOWED_ORIGINS` (optional, auto-detected from FRONTEND_URL)





