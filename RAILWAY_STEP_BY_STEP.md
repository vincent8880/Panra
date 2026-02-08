# Railway Deployment - Step by Step Guide

Follow these steps in order. Take your time!

## 🎯 Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"** (top right)
3. Select **"Deploy from GitHub repo"**
4. Choose your **PolyMarket repository**
5. Railway will create the project

---

## 🗄️ Step 2: Add PostgreSQL Database

1. In your new Railway project, click **"New"** button
2. Select **"Database"**
3. Click **"Add PostgreSQL"**
4. ✅ Railway automatically creates the database
5. ✅ Railway automatically sets `DATABASE_URL` (you don't need to do anything)

**Note:** You'll see a PostgreSQL service appear in your project. That's good!

---

## 🐍 Step 3: Deploy Backend (Django)

### 3.1 Create Backend Service

1. In your Railway project, click **"New"** button again
2. Select **"GitHub Repo"**
3. Choose your **PolyMarket repository** (same one)
4. Railway will detect it's Python and start building

### 3.2 Configure Backend Service

1. Click on the **backend service** (the one that just appeared)
2. Go to **"Settings"** tab
3. Scroll to **"Deploy"** section
4. **Root Directory**: Leave empty (or type `/`)
5. **Build Command**: Leave empty (Railway auto-detects)
6. **Start Command**: Leave empty (uses `Procfile` automatically)

### 3.3 Set Backend Environment Variables

1. Still in backend service **"Settings"**
2. Go to **"Variables"** tab
3. Click **"New Variable"** for each of these:

**Variable 1: SECRET_KEY**
- **Name**: `SECRET_KEY`
- **Value**: Generate one by running this in your terminal:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
  Copy the output and paste it as the value

**Variable 2: DEBUG**
- **Name**: `DEBUG`
- **Value**: `False`

**Variable 3: ALLOWED_HOSTS**
- **Name**: `ALLOWED_HOSTS`
- **Value**: `*.railway.app` (we'll update this later with your actual URL)

**Variable 4: FRONTEND_URL**
- **Name**: `FRONTEND_URL`
- **Value**: `http://localhost:3000` (we'll update this later)

**Variable 5: CORS_ALLOWED_ORIGINS**
- **Name**: `CORS_ALLOWED_ORIGINS`
- **Value**: `http://localhost:3000` (we'll update this later)

**Note:** `DATABASE_URL` is automatically set by Railway - you don't need to add it!

### 3.4 Get Backend URL

1. Still in backend service, go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"** (if not already generated)
4. Copy the URL (looks like: `https://your-backend-name.railway.app`)
5. **Save this URL** - you'll need it for the frontend!

---

## ⚛️ Step 4: Deploy Frontend (Next.js)

### 4.1 Create Frontend Service

1. In your Railway project, click **"New"** button again
2. Select **"GitHub Repo"**
3. Choose your **PolyMarket repository** (same one again)
4. Railway will detect it's Node.js

### 4.2 Configure Frontend Service

1. Click on the **frontend service** (the new one)
2. Go to **"Settings"** tab
3. Scroll to **"Deploy"** section
4. **Root Directory**: Type `frontend` (important!)
5. **Build Command**: `npm install && npm run build`
6. **Start Command**: `npm start`

### 4.3 Set Frontend Environment Variables

1. Still in frontend service **"Settings"**
2. Go to **"Variables"** tab
3. Click **"New Variable"** for each:

**Variable 1: NEXT_PUBLIC_API_URL**
- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://your-backend-url.railway.app/api`
  - Replace `your-backend-url.railway.app` with the backend URL you saved in Step 3.4!

**Variable 2: NODE_ENV**
- **Name**: `NODE_ENV`
- **Value**: `production`

### 4.4 Get Frontend URL

1. Still in frontend service, go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"** (if not already generated)
4. Copy the URL (looks like: `https://your-frontend-name.railway.app`)
5. **Save this URL** - you'll need it next!

---

## 🔗 Step 5: Connect Frontend and Backend

### 5.1 Update Backend CORS Settings

1. Go back to your **backend service**
2. Go to **"Settings"** → **"Variables"**
3. Find `FRONTEND_URL` variable
4. Click the **pencil icon** to edit
5. Change value to: `https://your-frontend-url.railway.app` (use the frontend URL from Step 4.4)
6. Click **"Update"**

4. Find `CORS_ALLOWED_ORIGINS` variable
5. Click the **pencil icon** to edit
6. Change value to: `https://your-frontend-url.railway.app` (same frontend URL)
7. Click **"Update"**

### 5.2 Update Backend ALLOWED_HOSTS

1. Still in backend **"Settings"** → **"Variables"**
2. Find `ALLOWED_HOSTS` variable
3. Click the **pencil icon** to edit
4. Change value to: `your-backend-url.railway.app,*.railway.app`
   - Replace `your-backend-url.railway.app` with your actual backend URL
5. Click **"Update"**

**Note:** Railway will automatically redeploy when you save variables!

---

## ✅ Step 6: Create Admin User

After both services are deployed:

1. Go to your **backend service**
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. Click **"View Logs"**
5. Click **"Shell"** tab (or use Railway CLI)
6. Run:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```
7. Follow the prompts to create your admin account

---

## 🎉 Step 7: Test It!

1. **Backend**: Visit `https://your-backend-url.railway.app/admin/`
   - Log in with your superuser account
   
2. **Frontend**: Visit `https://your-frontend-url.railway.app`
   - Should load your app!

3. **API**: Visit `https://your-backend-url.railway.app/api/markets/`
   - Should show markets (or empty list)

---

## 🆘 Troubleshooting

**Backend won't start?**
- Check logs: Backend service → Deployments → Latest → View Logs
- Make sure `SECRET_KEY` is set
- Make sure `DATABASE_URL` is auto-set (check Variables tab)

**Frontend can't connect to backend?**
- Check `NEXT_PUBLIC_API_URL` has correct backend URL
- Check backend `CORS_ALLOWED_ORIGINS` includes frontend URL
- Check both services are running (not paused)

**Database errors?**
- Make sure PostgreSQL service is running
- `DATABASE_URL` should be automatically set (don't add it manually)

---

## 📝 Quick Checklist

- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Backend service created
- [ ] Backend environment variables set
- [ ] Backend URL saved
- [ ] Frontend service created
- [ ] Frontend root directory set to `frontend`
- [ ] Frontend environment variables set
- [ ] Frontend URL saved
- [ ] Backend CORS updated with frontend URL
- [ ] Admin user created
- [ ] Both services tested

---

**You got this! Take it one step at a time.** 🚀



























