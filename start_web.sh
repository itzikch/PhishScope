#!/bin/bash

# PhishScope Web Application Startup Script

echo "🔍 PhishScope Web Application"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if Playwright is installed
if ! python -c "import playwright" 2>/dev/null; then
    echo "Installing Playwright browsers..."
    playwright install chromium
fi

echo ""
echo "Starting PhishScope Web Server..."
echo "=================================="
echo ""
echo "🌐 Web Interface: http://localhost:8070"
echo "📡 API Endpoint: http://localhost:8070/api/analyze"
echo ""
echo "⚠️  WARNING: This will load potentially malicious URLs!"
echo "   Only use in an isolated environment."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the web application
python web_app.py

# Made with Bob
