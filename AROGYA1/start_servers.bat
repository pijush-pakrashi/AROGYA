@echo off
title Arogya Hospital Management System
color 0A

echo ===================================================
echo     AROGYA Hospital Management System
echo ===================================================
echo.

:: Get the folder where this BAT file lives
set "ROOT=%~dp0"

echo [1/2] Starting Python Flask Backend (Port 5000)...
start "Arogya Backend" cmd /k "cd /d "%ROOT%arogya" && python app.py"

:: Wait 3 seconds for backend to boot
timeout /t 3 /nobreak >nul

echo [2/2] Starting React Frontend (Port 3000)...
start "Arogya Frontend" cmd /k "cd /d "%ROOT%frontend" && npm start"

echo.
echo ===================================================
echo  Both servers starting in separate windows!
echo  Backend  -> http://localhost:5000
echo  Frontend -> http://localhost:3000
echo  Admin    -> http://localhost:5000/admin/dashboard
echo ===================================================
echo.
timeout /t 5 /nobreak >nul

:: Open browser automatically
start "" "http://localhost:3000"

exit
