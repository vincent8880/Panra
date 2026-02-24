# Railway Services Config

**Important:** Config files do NOT follow Root Directory. Set Config File Path explicitly for each service in Service Settings.

---

## Panra (Frontend - Next.js)

| Setting | Value |
|---------|-------|
| Root Directory | `frontend` |
| Config File Path | `/frontend/railway.json` |
| Custom Start Command | **Leave empty** |
| Start command in config | `npm start` |

---

## Web (Backend - Django)

| Setting | Value |
|---------|-------|
| Root Directory | `backend` |
| Config File Path | `/backend/railway.json` |
| Custom Start Command | **Leave empty** |
| Start command in config | `python manage.py migrate && ...` (no `cd backend`) |
