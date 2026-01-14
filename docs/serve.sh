#!/bin/bash

# PhishScope Website Server Script
# Serves the website on port 8060 and handles port conflicts

PORT=8060
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🔍 PhishScope Website Server"
echo "=============================="
echo ""

# Function to check if port is in use
check_port() {
    lsof -ti:$PORT > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    echo "⚠️  Port $PORT is already in use"
    PID=$(lsof -ti:$PORT)
    if [ ! -z "$PID" ]; then
        echo "🔪 Killing process $PID on port $PORT..."
        kill -9 $PID
        sleep 1
        echo "✅ Process killed"
    fi
}

# Check if port is in use and kill if necessary
if check_port; then
    kill_port
fi

# Verify port is now free
if check_port; then
    echo "❌ Failed to free port $PORT"
    echo "Please manually kill the process using port $PORT"
    exit 1
fi

# Start the server
echo "🚀 Starting web server on port $PORT..."
echo "📁 Serving from: $SCRIPT_DIR"
echo ""
echo "🌐 Open your browser to:"
echo "   http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    python -m http.server $PORT
else
    echo "❌ Python is not installed"
    echo "Please install Python to run the web server"
    exit 1
fi

# Made with Bob
