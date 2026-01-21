# Quick Setup Guide

## Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

## Backend Setup (5 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Create sample markets (optional)
python manage.py create_sample_markets

# Start server
python manage.py runserver
```

Backend will run on `http://localhost:8000`

## Frontend Setup (3 minutes)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:3000`

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

## Default Test User

After running `create_sample_markets`, you can login with:
- Username: `admin`
- Password: `admin123` (if you created it with createsuperuser)

## Next Steps

1. Visit http://localhost:3000 to see the markets
2. Create markets via Django admin at http://localhost:8000/admin/
3. Start trading (payment integration coming soon)

## Troubleshooting

### Backend Issues
- Make sure port 8000 is not in use
- Check that all migrations are applied: `python manage.py migrate`
- Verify virtual environment is activated

### Frontend Issues
- Make sure port 3000 is not in use
- Clear `.next` folder if build errors occur: `rm -rf .next`
- Check that backend is running on port 8000

### CORS Issues
- Ensure `CORS_ALLOWED_ORIGINS` in `backend/config/settings.py` includes `http://localhost:3000`








