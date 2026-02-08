# Fix: Localhost Redirects After Login

## Problem
After logging in (especially with Google OAuth), users are being redirected to `http://localhost:3000` instead of the deployed frontend URL.

## Root Cause
The `FRONTEND_URL` environment variable is not set in Railway, so the application defaults to `http://localhost:3000`.

## Solution

### Step 1: Set FRONTEND_URL in Railway (REQUIRED)

1. Go to your **Railway dashboard**
2. Select your **backend service** (the Django one)
3. Go to **Settings** → **Variables**
4. Click **"+ New Variable"**
5. Add:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://panra-ke.up.railway.app` (or your actual frontend URL)
6. Click **"Add"**
7. Railway will automatically redeploy

### Step 2: Verify Your Frontend URL

To find your frontend URL:
1. Go to your **frontend service** in Railway
2. Go to **Settings** → **Networking**
3. Copy the domain (e.g., `https://panra-ke.up.railway.app`)

### Step 3: Test

After Railway redeploys (1-2 minutes):
1. Try logging in with Google
2. You should be redirected to your deployed frontend URL, not localhost

## What I've Fixed in Code

I've improved the Railway detection logic to:
1. Check for Railway environment variables
2. Infer frontend URL from backend domain (if backend is `panra.up.railway.app`, frontend is `panra-ke.up.railway.app`)
3. Use hardcoded fallback for known deployments

However, **the most reliable solution is to set the `FRONTEND_URL` environment variable** in Railway.

## Quick Checklist

- [ ] Set `FRONTEND_URL` environment variable in Railway backend service
- [ ] Value should be your frontend URL (e.g., `https://panra-ke.up.railway.app`)
- [ ] Wait for Railway to redeploy
- [ ] Test login - should redirect to deployed URL, not localhost

## Why This Happens

The code has a fallback to `http://localhost:3000` for local development. When `FRONTEND_URL` isn't set in Railway, it uses this default. Setting the environment variable ensures the correct URL is used in production.









