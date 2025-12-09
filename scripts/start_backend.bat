@echo off
echo Starting Django Backend...
cd /d "%~dp0..\backend"

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Run migrations
python manage.py migrate

REM Start the development server
python manage.py runserver

pause
