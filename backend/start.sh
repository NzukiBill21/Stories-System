#!/bin/bash
# Quick start script for backend services

echo "Starting Story Intelligence Dashboard Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one from .env.example"
    exit 1
fi

# Start API server in background
echo "Starting API server..."
python main.py &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A celery_app worker --loglevel=info &
WORKER_PID=$!

# Start Celery beat in background
echo "Starting Celery beat scheduler..."
celery -A celery_app beat --loglevel=info &
BEAT_PID=$!

echo "Backend services started!"
echo "API Server PID: $API_PID"
echo "Celery Worker PID: $WORKER_PID"
echo "Celery Beat PID: $BEAT_PID"
echo ""
echo "API available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "To stop all services, run: kill $API_PID $WORKER_PID $BEAT_PID"

# Wait for user interrupt
trap "kill $API_PID $WORKER_PID $BEAT_PID; exit" INT TERM
wait
