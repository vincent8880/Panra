# Frontend URL Setup

## Step 1: Get Your Frontend URL

1. In Railway, go to your **frontend service**
2. Go to **Settings → Networking**
3. You should see a Railway domain like: `https://your-frontend-name.up.railway.app`
4. **Copy this URL** - this is your frontend URL!

## Step 2: Make It the Default

### Option A: Use Railway's Default Domain (Easiest)
- Railway already gives you a domain
- Just use that URL as your main site
- No additional setup needed

### Option B: Add a Custom Domain
1. In your frontend service → **Settings → Networking**
2. Click **"Custom Domain"** or **"Add Domain"**
3. Enter your domain (e.g., `panra.com` or `www.panra.com`)
4. Railway will give you DNS instructions
5. Update your DNS records as instructed
6. Wait for DNS propagation (usually 5-30 minutes)

## Step 3: Update Environment Variables

Make sure your frontend has:
- `NEXT_PUBLIC_API_URL` = your backend URL (e.g., `https://panra.up.railway.app/api`)

And your backend has:
- `FRONTEND_URL` = your frontend URL
- `CORS_ALLOWED_ORIGINS` = your frontend URL

## Step 4: Test It!

Visit your frontend URL in a browser - it should load your Panra app!







