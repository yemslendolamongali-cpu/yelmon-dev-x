@echo off
title YELMON Dev X
cd /d "%~dp0"

REM Attendre que le backend soit prêt
echo  YELMON Dev X v1.0
echo  Demarrage du serveur...
start /B "" "%~dp0venv\Scripts\python.exe" "%~dp0backend\app.py" > "%~dp0logs\backend.log" 2>&1

REM Attendre 5 secondes
timeout /t 5 /nobreak >nul

REM Lancer Electron
echo  Ouverture de l'application...
"%~dp0node_modules\electron\dist\electron.exe" "%~dp0frontend\src\main.js"

REM Si Electron ferme, arrêter le backend
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *" >nul 2>&1
