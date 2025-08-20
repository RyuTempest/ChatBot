@echo off
echo Starting Discord AI Chatbot Web Interface...
echo.
echo Make sure you have:
echo 1. Created a .env file with your tokens
echo 2. Installed dependencies with: pip install -r requirements.txt
echo.
echo The web interface will be available at: http://localhost:5000
echo.
echo Press any key to start the web server...
pause >nul
python web_server.py
pause
