@echo off
echo ========================================
echo Starting Frontend Dashboard
echo ========================================
echo.

cd frontend

echo Installing dependencies (if needed)...
call npm install

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
