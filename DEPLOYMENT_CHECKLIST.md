# Railway Deployment Checklist ✅

## ✅ Configuration Files Ready

All deployment files are set up and ready to go:

### Backend Configuration
- ✅ `Procfile` - Gunicorn startup command
- ✅ `railway.json` - Railway deployment config
- ✅ `requirements.txt` - Includes gunicorn, whitenoise, dj-database-url
- ✅ `backend/config/settings.py` - Production-ready settings

### Frontend Configuration
- ✅ `frontend/package.json` - Next.js config (already exists)
- ✅ `frontend/next.config.js` - Next.js settings (already exists)

### Documentation
- ✅ `RAILWAY_DEPLOYMENT.md` - Full deployment guide
- ✅ `DEPLOYMENT_CHECKLIST.md` - This file

---

## 🚀 Quick Deployment Steps

When you're ready to deploy:

### 1. Backend Service Setup
- **Root Directory**: Leave empty (or `/`)
- **Build Command**: Auto-detected by Railway
- **Start Command**: Already in `Procfile` ✅

### 2. Frontend Service Setup
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`

### 3. Environment Variables to Set

#### Backend Service:
```
SECRET_KEY=<generate-random-key>
DEBUG=False
ALLOWED_HOSTS=your-backend.railway.app,*.railway.app
FRONTEND_URL=https://your-frontend.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app
DATABASE_URL=<auto-set-by-railway-postgres>
```

#### Frontend Service:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
NODE_ENV=production
```

### 4. Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- [ ] Code is committed and pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added to Railway project
- [ ] Backend service created (points to repo root)
- [ ] Frontend service created (points to `frontend/` directory)
- [ ] Environment variables set (see above)
- [ ] Backend URL obtained from Railway
- [ ] Frontend URL obtained from Railway
- [ ] CORS settings updated with frontend URL
- [ ] Admin superuser created (via Railway CLI or shell)

---

## 🎯 What's Already Configured

### Backend (Django)
- ✅ Gunicorn for production server
- ✅ WhiteNoise for static files
- ✅ PostgreSQL support (via dj-database-url)
- ✅ CORS configuration
- ✅ Security settings for production
- ✅ Environment-based configuration

### Frontend (Next.js)
- ✅ Production build configuration
- ✅ API URL environment variable support
- ✅ Increment buttons (10, 100, 1000, Max) ✅

---

## 🔗 After Deployment

1. **Get URLs**:
   - Backend: `https://your-backend.railway.app`
   - Frontend: `https://your-frontend.railway.app`

2. **Update Environment Variables**:
   - Update `FRONTEND_URL` in backend with actual frontend URL
   - Update `CORS_ALLOWED_ORIGINS` in backend with actual frontend URL
   - Update `NEXT_PUBLIC_API_URL` in frontend with actual backend URL

3. **Create Admin User**:
   ```bash
   railway run python backend/manage.py createsuperuser
   ```

4. **Access Admin Panel**:
   - `https://your-backend.railway.app/admin/`

---

## 📝 Notes

- Railway will automatically detect Python (backend) and Node.js (frontend)
- Database migrations run automatically via `Procfile`
- Static files are served via WhiteNoise (no Nginx needed)
- Both services can run on the base tier (within usage limits)

---

## 🆘 Troubleshooting

If something doesn't work:
1. Check Railway logs (Deployments → View Logs)
2. Verify environment variables are set correctly
3. Ensure CORS includes your frontend URL
4. Check that `DATABASE_URL` is auto-set by Railway
5. Verify both services are running (not paused)

---

**Everything is ready! Just follow `RAILWAY_DEPLOYMENT.md` when you deploy.** 🚀


























