@echo off
echo Starting React Frontend...
cd /d "%~dp0..\frontend"

REM Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies...
    npm install
)

REM Start the development server
npm run dev

pause
