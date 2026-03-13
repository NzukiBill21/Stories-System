@echo off
REM Stops MySQL from closing itself by replacing corrupted/unstable data with a clean copy.
REM You will LOSE all existing databases. Run setup_database.bat afterward to recreate story_intelligence.

set XAMPP_MYSQL=c:\xampp\mysql
set DATA=%XAMPP_MYSQL%\data
set BACKUP=%XAMPP_MYSQL%\backup
set DATA_OLD=%XAMPP_MYSQL%\data_old

echo.
echo ============================================================
echo   MySQL/MariaDB Data Reset (fixes "closes itself" issue)
echo ============================================================
echo.
echo 1. Close XAMPP Control Panel completely.
echo 2. Make sure MySQL is NOT running (red/stopped).
echo 3. This will: rename "data" to "data_old", copy "backup" to "data"
echo    You will lose all current databases. story_intelligence will need to be recreated.
echo.
set /p CONFIRM=Type YES and press Enter to continue: 
if /i not "%CONFIRM%"=="YES" (
    echo Cancelled.
    pause
    exit /b 0
)

if not exist "%DATA%" (
    echo Error: Folder not found: %DATA%
    pause
    exit /b 1
)
if not exist "%BACKUP%" (
    echo Error: Backup folder not found: %BACKUP%
    echo XAMPP may be installed elsewhere. Edit this script and set XAMPP_MYSQL.
    pause
    exit /b 1
)

echo.
echo Renaming data to data_old...
if exist "%DATA_OLD%" (
    echo Removing old backup folder data_old...
    rmdir /s /q "%DATA_OLD%"
)
ren "%DATA%" "data_old"
if %ERRORLEVEL% neq 0 (
    echo Failed to rename. Is MySQL or another program using the folder? Close XAMPP and try again.
    pause
    exit /b 1
)

echo Copying backup to data...
xcopy "%BACKUP%" "%DATA%" /E /I /H /Y
if %ERRORLEVEL% neq 0 (
    echo Copy failed. Restoring original: ren data_old data
    ren "%DATA_OLD%" "data"
    pause
    exit /b 1
)

echo.
echo Done. Data folder is now a clean copy.
echo.
echo Next steps:
echo   1. Open XAMPP Control Panel and Start MySQL (do NOT click Admin).
echo   2. Run setup_database.bat to create story_intelligence database and tables.
echo   3. Start the app: python main.py
echo.
pause
