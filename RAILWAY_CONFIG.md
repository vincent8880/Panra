# Railway Configuration Reference

This document explains the Railway-specific configuration patterns used in this project.

## Railway Environment Patterns

### 1. Automatic Environment Variables

Railway automatically provides these environment variables:

- **`PORT`**: The port your service should listen on (Railway assigns this)
- **`DATABASE_URL`**: Automatically set when you add PostgreSQL (format: `postgresql://user:pass@host:port/db`)
- **`RAILWAY_ENVIRONMENT`**: Set to `production` when deployed
- **`RAILWAY_PROJECT_ID`**: Your project ID
- **`RAILWAY_SERVICE_ID`**: Your service ID

### 2. Service Configuration

#### Backend Service (Django)
- **Detector**: Railway auto-detects Python from `requirements.txt`
- **Build**: Uses Nixpacks (auto-detected)
- **Start**: Uses `Procfile` or `railway.json` startCommand
- **Port**: Must bind to `$PORT` (Railway provides this)

#### Frontend Service (Next.js)
- **Detector**: Railway auto-detects Node.js from `package.json`
- **Build**: Runs `npm install && npm run build` (auto-detected)
- **Start**: Runs `npm start` (auto-detected)
- **Root Directory**: Must be set to `frontend/` in Railway UI

### 3. Database Connection

Railway automatically:
1. Creates PostgreSQL database
2. Sets `DATABASE_URL` environment variable
3. Links it to your backend service

Our `settings.py` handles this:
```python
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}
```

### 4. Static Files

Railway doesn't provide Nginx, so we use **WhiteNoise**:
- Configured in `settings.py` middleware
- Serves static files directly from Django
- Works automatically on Railway

### 5. CORS Configuration

Railway services get dynamic URLs, so we:
- Use environment variables for frontend URL
- Allow multiple origins (comma-separated)
- Support both Railway domains and custom domains

## File Structure for Railway

```
PolyMarket/
├── Procfile                    # Backend startup command
├── railway.json                # Railway deployment config
├── requirements.txt            # Python dependencies (includes gunicorn, whitenoise)
├── backend/
│   ├── config/
│   │   └── settings.py        # Production-ready settings
│   └── manage.py
└── frontend/
    ├── package.json           # Node.js dependencies
    └── next.config.js
```

## Railway Service Setup

### Backend Service
- **Type**: Python Service
- **Root Directory**: `/` (project root)
- **Build Command**: Auto-detected (Nixpacks)
- **Start Command**: From `Procfile` or `railway.json`
- **Environment Variables**:
  - `SECRET_KEY` (required)
  - `DEBUG=False`
  - `ALLOWED_HOSTS` (Railway domain)
  - `FRONTEND_URL` (frontend Railway URL)
  - `CORS_ALLOWED_ORIGINS` (frontend Railway URL)
  - `DATABASE_URL` (auto-set by Railway)

### Frontend Service
- **Type**: Node.js Service
- **Root Directory**: `frontend/`
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL` (backend Railway URL)
  - `NODE_ENV=production`

### Database Service
- **Type**: PostgreSQL
- **Connection**: Auto-linked via `DATABASE_URL`
- **No configuration needed** - Railway handles it

## Railway-Specific Settings

### Port Binding
```python
# Procfile uses $PORT (Railway provides this)
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### Database URL Parsing
```python
# Railway provides DATABASE_URL in format:
# postgresql://user:password@host:port/dbname
# dj-database-url handles parsing automatically
```

### Static Files
```python
# WhiteNoise serves static files (no Nginx needed)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### CORS with Dynamic URLs
```python
# Support multiple origins (Railway + custom domains)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)
```

## Deployment Flow

1. **Railway detects** Python/Node.js from project files
2. **Builds** using Nixpacks (auto-detected)
3. **Runs** start command from `Procfile` or `railway.json`
4. **Exposes** service on Railway domain
5. **Links** database automatically via `DATABASE_URL`

## Best Practices Used

✅ **Environment-based configuration** - Uses env vars for all settings  
✅ **Auto-database detection** - Detects `DATABASE_URL` automatically  
✅ **Port binding** - Uses `$PORT` from Railway  
✅ **Static file serving** - WhiteNoise (no external web server needed)  
✅ **CORS flexibility** - Supports multiple origins  
✅ **Security** - Production security settings when `DEBUG=False`  
✅ **Migration automation** - Runs migrations in `Procfile`  

## Comparison with nestquest (if similar)

If your nestquest project uses similar patterns:
- ✅ Same `DATABASE_URL` handling
- ✅ Same `$PORT` binding
- ✅ Same environment variable patterns
- ✅ Same static file serving (WhiteNoise)
- ✅ Same CORS configuration approach

This setup follows Railway's standard patterns and should work seamlessly.















