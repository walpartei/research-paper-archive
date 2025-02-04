#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Start the backend server
echo "Starting backend server..."
uvicorn backend.main:app --reload &

# Start the frontend server (using python's built-in server)
echo "Starting frontend server..."
python -m http.server 3000 &

echo "Servers started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Press Ctrl+C to stop both servers"

# Wait for both background processes
wait
