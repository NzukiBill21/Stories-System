@echo off
REM Quick start script for backend services on Windows

echo Starting Story Intelligence Dashboard Backend...

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found. Please create one from .env.example
    exit /b 1
)

REM Start API server
echo Starting API server...
start "API Server" cmd /k "python main.py"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Celery worker
echo Starting Celery worker...
start "Celery Worker" cmd /k "celery -A celery_app worker --loglevel=info"

REM Start Celery beat
echo Starting Celery beat scheduler...
start "Celery Beat" cmd /k "celery -A celery_app beat --loglevel=info"

echo.
echo Backend services started in separate windows!
echo API available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Close the windows to stop the services.

pause
