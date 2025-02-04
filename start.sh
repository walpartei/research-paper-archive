#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Kill any existing processes on the ports
lsof -i :3001,8001 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null || true

# Start the backend server
echo "Starting backend server..."
uvicorn backend.main:app --reload --port 8001 &

# Start the frontend server (using python's built-in server)
echo "Starting frontend server..."
python -m http.server 3001 &

echo "Servers started!"
echo "Frontend: http://localhost:3001"
echo "Backend: http://localhost:8001"
echo "Press Ctrl+C to stop both servers"

# Wait for both background processes
wait
