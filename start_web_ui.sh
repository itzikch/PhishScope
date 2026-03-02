#!/bin/bash

# PhishScope Web UI Startup Script
# This script starts both the backend API and frontend dev server

set -e

echo "🔍 PhishScope Web UI Startup"
echo "=============================="
echo ""

# Kill any existing processes on ports first
echo "🧹 Cleaning up existing processes..."
lsof -ti:8070 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Ports cleaned"
echo ""

# Check if package is installed
if ! python -c "import phishscope" 2>/dev/null; then
    echo "⚠️  PhishScope package not installed!"
    echo "📦 Installing package in editable mode..."
    pip install -e .
    echo "✅ Package installed"
    echo ""
fi

# Check if Playwright is installed
if ! python -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "⚠️  Playwright not installed!"
    echo "📦 Installing Playwright..."
    pip install playwright
    playwright install chromium
    echo "✅ Playwright installed"
    echo ""
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Frontend dependencies not installed!"
    echo "📦 Installing npm packages..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
    echo ""
fi

# Check if ports are already in use and kill processes
echo "🔍 Checking for existing processes..."
BACKEND_PORT=8070
FRONTEND_PORT=3000

# Kill process on backend port if exists
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $BACKEND_PORT is in use. Killing existing process..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    sleep 2
    # Verify it's killed
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Failed to kill process on port $BACKEND_PORT"
        echo "Please manually kill it with: lsof -ti:$BACKEND_PORT | xargs kill -9"
        exit 1
    fi
    echo "✅ Port $BACKEND_PORT is now free"
fi

# Kill process on frontend port if exists
if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $FRONTEND_PORT is in use. Killing existing process..."
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    sleep 2
    # Verify it's killed
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Failed to kill process on port $FRONTEND_PORT"
        echo "Please manually kill it with: lsof -ti:$FRONTEND_PORT | xargs kill -9"
        exit 1
    fi
    echo "✅ Port $FRONTEND_PORT is now free"
fi

echo ""
echo "🚀 Starting PhishScope Web UI..."
echo ""
echo "Backend API will run on: http://localhost:$BACKEND_PORT"
echo "Frontend will run on: http://localhost:$FRONTEND_PORT"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

# Start backend in background
echo "▶️  Starting backend API..."
uvicorn src.phishscope.api.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo "▶️  Starting frontend dev server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers started!"
echo ""
echo "📊 Open your browser to: http://localhost:3000"
echo "📚 API documentation: http://localhost:8070/docs"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID