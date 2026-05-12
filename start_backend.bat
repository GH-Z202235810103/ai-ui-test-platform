@echo off
echo Starting AI UI Test Platform Backend...
echo.

:restart
echo [%time%] Starting backend server...
cd /d D:\毕设git\ai-ui-test-platform\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

echo [%time%] Backend server stopped. Restarting in 3 seconds...
timeout /t 3 /nobreak >nul
goto restart
