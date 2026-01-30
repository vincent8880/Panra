# Railway Deployment Guide

This guide will help you deploy both the backend (Django) and frontend (Next.js) to Railway.

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub repository with your code
- Railway CLI (optional, but helpful)

## Deployment Strategy

You have two options:

### Option 1: Two Separate Services (Recommended)
- **Backend Service**: Django API
- **Frontend Service**: Next.js app

### Option 2: Monorepo with Single Service
- Deploy backend only, serve frontend from another platform (Vercel, Netlify, etc.)

We'll use **Option 1** for this guide.

---

## Step 1: Deploy Backend (Django)

### 1.1 Create New Project on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 1.2 Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

### 1.3 Configure Backend Service

1. In your Railway project, click "New" → "GitHub Repo"
2. Select your repository again (this creates a service)
3. Railway will detect it's a Python project

### 1.4 Set Environment Variables

Go to your backend service → Settings → Variables, and add:

```
SECRET_KEY=your-secret-key-here-generate-a-random-one
DEBUG=False
ALLOWED_HOSTS=your-backend-url.railway.app,*.railway.app
FRONTEND_URL=https://your-frontend-url.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend-url.railway.app,https://your-frontend-domain.com
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 1.5 Configure Build Settings

In your backend service → Settings → Deploy:

- **Root Directory**: Leave empty (or set to `/` if needed)
- **Build Command**: Railway will auto-detect (uses Nixpacks)
- **Start Command**: Already set in `Procfile`

The `Procfile` contains:
```
web: cd backend && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### 1.6 Deploy

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Run migrations (via Procfile)
3. Start the Django server with Gunicorn

### 1.7 Get Backend URL

After deployment:
1. Go to your backend service → Settings → Networking
2. Generate a domain (or use the default Railway domain)
3. Copy the URL (e.g., `https://your-backend.railway.app`)

---

## Step 2: Deploy Frontend (Next.js)

### 2.1 Create Frontend Service

1. In the same Railway project, click "New" → "GitHub Repo"
2. Select your repository again
3. Railway will detect it's a Node.js project

### 2.2 Configure Frontend Service

Go to Settings → Deploy:

- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`

### 2.3 Set Environment Variables

Go to Settings → Variables, and add:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api
NODE_ENV=production
```

**Important**: Replace `your-backend-url.railway.app` with your actual backend URL from Step 1.7.

### 2.4 Deploy

Railway will:
1. Install npm dependencies
2. Build the Next.js app
3. Start the production server

### 2.5 Get Frontend URL

1. Go to your frontend service → Settings → Networking
2. Generate a domain
3. Copy the URL (e.g., `https://your-frontend.railway.app`)

---

## Step 3: Update CORS Settings

After both services are deployed:

1. Go back to your **backend service** → Settings → Variables
2. Update `CORS_ALLOWED_ORIGINS` to include your frontend URL:
   ```
   CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app,https://your-frontend-domain.com
   ```
3. Update `FRONTEND_URL`:
   ```
   FRONTEND_URL=https://your-frontend.railway.app
   ```
4. Railway will automatically redeploy when you save

---

## Step 4: Create Superuser (Admin)

You need to create an admin user for Django:

### Option A: Using Railway CLI

```bash
railway login
railway link  # Link to your project
railway run python backend/manage.py createsuperuser
```

### Option B: Using Railway Shell

1. Go to your backend service
2. Click "Deployments" → Latest deployment → "View Logs"
3. Click "Shell" tab
4. Run:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

---

## Step 5: Create Sample Markets (Optional)

If you have a management command to create sample markets:

```bash
railway run python backend/manage.py create_sample_markets
```

Or via Railway Shell (same as above).

---

## Environment Variables Summary

### Backend Service
```
SECRET_KEY=<generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-backend.railway.app,*.railway.app
FRONTEND_URL=https://your-frontend.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app
DATABASE_URL=<automatically-set-by-railway>
```

### Frontend Service
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
NODE_ENV=production
```

---

## Troubleshooting

### Backend Issues

**Database connection errors:**
- Make sure PostgreSQL service is running
- Check that `DATABASE_URL` is set automatically by Railway

**Static files not loading:**
- WhiteNoise is configured in settings.py
- Make sure `STATIC_ROOT` is set correctly

**CORS errors:**
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check that `FRONTEND_URL` matches your frontend domain

### Frontend Issues

**API connection errors:**
- Verify `NEXT_PUBLIC_API_URL` points to your backend
- Check backend logs for errors
- Ensure CORS is configured correctly

**Build errors:**
- Check that all dependencies are in `package.json`
- Review build logs in Railway

---

## Custom Domains (Optional)

### Backend Custom Domain
1. Go to backend service → Settings → Networking
2. Click "Custom Domain"
3. Add your domain (e.g., `api.yourdomain.com`)
4. Follow Railway's DNS instructions

### Frontend Custom Domain
1. Go to frontend service → Settings → Networking
2. Click "Custom Domain"
3. Add your domain (e.g., `yourdomain.com`)
4. Update `NEXT_PUBLIC_API_URL` and `CORS_ALLOWED_ORIGINS` accordingly

---

## Monitoring & Logs

- **View Logs**: Go to any service → "Deployments" → Click a deployment → "View Logs"
- **Metrics**: Railway provides CPU, memory, and network metrics
- **Alerts**: Set up alerts for deployment failures

---

## Cost Considerations

Railway offers:
- **Free tier**: $5 credit/month
- **Hobby plan**: $20/month (includes more resources)
- **Pro plan**: $100/month (for production workloads)

For a small project, the free tier should be sufficient initially.

---

## Next Steps

1. ✅ Deploy backend
2. ✅ Deploy frontend
3. ✅ Configure CORS
4. ✅ Create admin user
5. ✅ Test the application
6. ✅ Set up custom domains (optional)
7. ✅ Configure monitoring/alerts

---

## Quick Reference

**Backend URL**: `https://your-backend.railway.app`  
**Frontend URL**: `https://your-frontend.railway.app`  
**Admin Panel**: `https://your-backend.railway.app/admin/`

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app




















