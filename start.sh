#!/bin/bash

# Quick start script for PE Ratio Dashboard
echo "🚀 Starting PE Ratio Dashboard..."

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Using Docker Compose..."
    docker-compose up --build
else
    echo "📦 Starting services manually..."
    
    # Start backend in background
    echo "Starting backend server..."
    cd backend
    python -m pip install -r requirements.txt
    python main.py &
    BACKEND_PID=$!
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend
    echo "Starting frontend server..."
    cd ../frontend
    npm install
    npm run dev &
    FRONTEND_PID=$!
    
    echo "✅ Services started!"
    echo "📊 Backend API: http://localhost:8000"
    echo "🖥️  Frontend Dashboard: http://localhost:3000"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Wait for user interrupt
    trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
fi