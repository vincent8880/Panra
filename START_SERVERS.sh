#!/bin/bash

# Start Django backend on port 8001
echo "Starting Django backend on port 8001..."
cd backend
source venv/bin/activate
python manage.py runserver 8001 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 2

# Start Next.js frontend
echo "Starting Next.js frontend on port 3000..."
cd ../frontend
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "=========================================="
echo "Servers are running:"
echo "  Backend:  http://localhost:8001"
echo "  Frontend: http://localhost:3000"
echo ""
echo "To stop servers, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "=========================================="

# Wait for user interrupt
wait




