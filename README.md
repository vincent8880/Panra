# Panra

A Polymarket-inspired prediction market platform built with Django and Next.js.

## Features

- 🎯 Create and trade on prediction markets
- 💰 Real-time price updates
- 📊 Market statistics and volume tracking
- 🔐 User authentication and wallet management
- 📱 Responsive design

## Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- SQLite (development) / PostgreSQL (production)
- Django CORS Headers

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- SWR for data fetching

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r ../requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
PolyMarket/
├── backend/
│   ├── config/          # Django settings
│   ├── markets/         # Market app
│   ├── users/           # User app
│   ├── trading/         # Trading app
│   └── manage.py
├── frontend/
│   ├── app/             # Next.js app directory
│   ├── components/      # React components
│   └── lib/             # API utilities
└── requirements.txt
```

## API Endpoints

### Markets
- `GET /api/markets/` - List all markets
- `GET /api/markets/{id}/` - Get market details
- `GET /api/markets/?status=open` - Filter markets by status

### Trading
- `POST /api/trading/orders/` - Create an order
- `GET /api/trading/orders/` - List user orders
- `POST /api/trading/orders/{id}/cancel/` - Cancel an order
- `GET /api/trading/trades/` - List trades
- `GET /api/trading/positions/` - List user positions

### Users
- `GET /api/auth/users/me/` - Get current user

## Next Steps

- [ ] Implement order matching engine
- [ ] Add M-Pesa payment integration
- [ ] Implement market resolution system
- [ ] Add order book visualization
- [ ] Add trade history display
- [ ] Implement user positions tracking
- [ ] Add market creation interface
- [ ] Implement admin market resolution

## License

MIT








