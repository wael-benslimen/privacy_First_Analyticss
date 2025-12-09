@echo off
echo ========================================
echo Starting Differential Privacy Backend
echo ========================================
echo.

echo Step 1: Running migrations...
python manage.py migrate

echo.
echo Step 2: Creating admin user (if needed)...
python create_user.py

echo.
echo Step 3: Starting server...
echo Backend will be available at: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver
