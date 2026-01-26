# Verify Frontend → Backend → Database Connections

## Step 1: Verify Frontend → Backend Connection

### Test in Browser:
1. Open your **frontend URL** (e.g., `https://panra-frontend.up.railway.app`)
2. Open browser **Developer Tools** (F12)
3. Go to **Network** tab
4. Refresh the page
5. Look for API calls to `/api/markets/` or similar
6. Check if they return data or errors

### Expected Results:
- ✅ **Success**: You see API calls returning market data (or empty array `[]`)
- ❌ **Failure**: You see CORS errors or 404/500 errors

### If CORS errors:
- Check backend `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check backend `FRONTEND_URL` is set correctly

### If 404/500 errors:
- Check `NEXT_PUBLIC_API_URL` in frontend service points to your backend
- Format should be: `https://your-backend-url.railway.app/api`

---

## Step 2: Verify Backend → Database Connection

### Test via API:
1. Visit: `https://your-backend-url.railway.app/api/markets/`
2. You should see JSON response (even if empty `[]`)
3. If you see database errors, the connection is broken

### Test via Admin Panel:
1. Visit: `https://your-backend-url.railway.app/admin/`
2. If you can log in → Database is connected ✅
3. If you see database errors → Connection issue ❌

---

## Step 3: Create Admin User

### Option A: Using Railway CLI (Recommended)
```bash
cd ~/PolyMarket
railway link  # Select your backend service
railway run python backend/manage.py createsuperuser
```

### Option B: Using Railway Shell
1. Go to backend service → **Deployments** → Latest → **View Logs**
2. Click **"Shell"** tab
3. Run:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```
4. Follow prompts (username, email, password)

### Option C: Using Local Machine (if DATABASE_URL is accessible)
```bash
cd ~/PolyMarket/backend
source venv/bin/activate
export DATABASE_URL='your-railway-postgres-url'
python manage.py createsuperuser
```

---

## Step 4: Create Markets

### Option A: Via Django Admin
1. Log in to: `https://your-backend-url.railway.app/admin/`
2. Go to **Markets** section
3. Click **"Add Market"**
4. Fill in the form and save

### Option B: Via Management Command
```bash
railway run python backend/manage.py create_sample_markets
```

### Option C: Via API (if you have API endpoint for creating markets)
- Use Postman or curl to POST to `/api/markets/`

---

## Quick Connection Checklist

- [ ] Frontend loads (no blank page)
- [ ] Frontend shows markets list (even if empty)
- [ ] Browser Network tab shows API calls to backend
- [ ] Backend `/api/markets/` returns JSON
- [ ] Backend `/admin/` loads (login page)
- [ ] Can create admin user
- [ ] Can log in to admin panel
- [ ] Can see database tables in admin
- [ ] Can create markets

---

## Troubleshooting

### Frontend shows blank/errors:
- Check `NEXT_PUBLIC_API_URL` environment variable
- Check browser console for errors
- Check Network tab for failed API calls

### Backend returns errors:
- Check `DATABASE_URL` is set (should be auto-set by Railway)
- Check backend logs for database connection errors
- Verify PostgreSQL service is running

### Can't create admin user:
- Make sure migrations ran successfully
- Check backend logs for errors
- Try using Railway CLI method





