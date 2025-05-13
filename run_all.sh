#!/bin/bash

# Ensure script exits on any error
set -e

# Activate your Python virtual environment
source .venv/bin/activate

# Start FastAPI backend
echo "🔌 Starting FastAPI backend..."
uvicorn backend.app:app --reload &
BACKEND_PID=$!

# Start file watcher (optional, kill this later if not needed)
echo "👀 Starting file watcher..."
python backend/watcher.py &
WATCHER_PID=$!

# Start Vue frontend
echo "🌐 Starting Vue frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Trap Ctrl+C to kill all background processes
trap "echo '🧹 Cleaning up...'; kill $BACKEND_PID $WATCHER_PID $FRONTEND_PID" INT

# Wait to keep the script running
wait
