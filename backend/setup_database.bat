@echo off
REM Create story_intelligence database and tables WITHOUT opening phpMyAdmin.
REM Use this when clicking "Admin" in XAMPP causes MySQL to stop.

set MYSQL=c:\xampp\mysql\bin\mysql.exe
set SCHEMA=%~dp0schema.sql

if not exist "%MYSQL%" (
    echo MySQL not found at %MYSQL%
    echo Adjust MYSQL path in this script if XAMPP is installed elsewhere.
    pause
    exit /b 1
)

echo.
echo 1. Make sure MySQL is RUNNING in XAMPP (do NOT click Admin).
echo 2. This script will create database and tables using the command line.
echo.
pause

echo Running schema...
"%MYSQL%" -u root < "%SCHEMA%"
if %ERRORLEVEL% neq 0 (
    echo.
    echo If it asked for a password, run this instead in Command Prompt:
    echo   "%MYSQL%" -u root -p ^< "%SCHEMA%"
    echo.
    pause
    exit /b 1
)

echo.
echo Adding sample sources (BBC, CNN, Reuters, Facebook, Instagram, TikTok)...
cd /d "%~dp0"
python init_db.py
if %ERRORLEVEL% neq 0 (
    echo Schema is OK but adding sources failed. Run manually: cd backend ^&^& python init_db.py
) else (
    echo Sources added. Refresh the app Sources page to see them.
)
echo.
echo Done. Start the backend: python main.py
echo.
pause
