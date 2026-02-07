# Railway Services Configuration

This project has **2 services** that Railway needs to deploy from the same GitHub repo.

## Service 1: Backend (Django)

**In Railway UI:**
- **Root Directory**: `/` (or leave empty)
- **Build Command**: (auto-detected - uses Nixpacks)
- **Start Command**: (auto-detected from `Procfile`)

**What Railway sees:**
- `requirements.txt` in root → Detects Python
- `Procfile` in root → Uses that for startup
- Runs Django from `backend/` folder

## Service 2: Frontend (Next.js)

**In Railway UI:**
- **Root Directory**: `frontend` ⚠️ **MUST SET THIS**
- **Build Command**: `npm install && npm run build`
- **Start Command**: `npm start`

**What Railway sees:**
- `package.json` in `frontend/` folder → Detects Node.js
- Builds and runs Next.js

## How to Configure in Railway

1. **Backend Service:**
   - Settings → Deploy → Root Directory: `/` or empty
   - That's it! Railway auto-detects Python.

2. **Frontend Service:**
   - Settings → Deploy → Root Directory: `frontend` ← **This is the key!**
   - Settings → Deploy → Build Command: `npm install && npm run build`
   - Settings → Deploy → Start Command: `npm start`

## Why This Works

- **Backend**: Root = `/` → Railway looks at repo root, finds Python files
- **Frontend**: Root = `frontend/` → Railway looks inside `frontend/` folder, finds Node.js files

Same repo, different "starting points" for each service.
























