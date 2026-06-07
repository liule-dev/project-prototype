@echo off
chcp 65001 >nul
echo ========================================
echo Starting Celery Workers
echo ========================================
echo.

cd /d "%~dp0"

echo Setting PYTHONPATH...
set PYTHONPATH=%CD%
echo Current directory: %CD%
echo.

echo Checking Redis connection...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis is not running!
    echo Please start Redis first: redis-server
    echo.
) else (
    echo [OK] Redis is running
    echo.
)

echo Starting Celery Workers for all queues...
echo - ai_queue (AI tasks)
echo - file_queue (File processing)
echo - data_queue (Data operations)
echo.
echo Press Ctrl+C to stop all workers
echo ========================================
echo.

celery -A celery_worker:celery_app worker --queues=ai_queue,file_queue,data_queue --loglevel=info --pool=solo --hostname=main_worker

pause
