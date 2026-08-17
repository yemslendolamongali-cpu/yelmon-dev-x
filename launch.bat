@echo off
REM launch.bat - Lancement rapide de YELMON Dev X
echo  YELMON Dev X v1.0.0
echo ========================================
echo.

cd /d "%~dp0"

REM Vérifier si l'installation existe
if not exist "YELMON_Dev_X" (
    echo  YELMON Dev X non installé
    echo  Lancement de l'installateur...
    python installer.py
    if errorlevel 1 (
        echo  Échec de l'installation
        pause
        exit /b 1
    )
)

echo  Lancement de YELMON Dev X...
cd YELMON_Dev_X

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe yelmon.py start
) else (
    python yelmon.py start
)

pause
