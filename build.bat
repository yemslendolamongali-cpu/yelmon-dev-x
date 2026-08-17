@echo off
REM build.bat - Build YELMON Dev X sur Windows
echo ========================================
echo     YELMON Dev X - Build Automatique
echo ========================================
echo.

echo  Vérification de l'environnement...
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python non trouve. Veuillez installer Python 3.8+
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo  Node.js non trouve. Veuillez installer Node.js 16+
    pause
    exit /b 1
)

echo  Environnement OK
echo.

echo  Lancement du build...
python build.py --all

if errorlevel 1 (
    echo  Build echoue
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build termine avec succes!
echo  Dossier de sortie: dist/
echo ========================================
pause
