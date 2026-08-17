# build.py - Script de build automatique pour YELMON Dev X
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YELMON Dev X - Build Automatique
Version: 1.0.0
Ce script construit et empaquète l'application automatiquement
"""

import os
import sys
import shutil
import subprocess
import json
import platform
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
import logging
import threading
import time

# Configuration
APP_NAME = "YELMON_Dev_X"
APP_VERSION = "1.0.0"
APP_AUTHOR = "YELMON Team"
APP_DESCRIPTION = "Assistant de codage IA nouvelle génération"

# Dossiers
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"
TEMP_DIR = ROOT_DIR / "temp_build"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [YELMON Build] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================
# UTILITAIRES
# ============================================

class BuildUtils:
    """Utilitaires pour le build"""

    @staticmethod
    def get_python_path():
        """Retourne le chemin de Python"""
        return sys.executable

    @staticmethod
    def get_platform():
        """Retourne la plateforme"""
        system = platform.system().lower()
        if system == 'windows':
            return 'win'
        elif system == 'darwin':
            return 'mac'
        else:
            return 'linux'

    @staticmethod
    def get_arch():
        """Retourne l'architecture"""
        return platform.machine().lower()

    @staticmethod
    def ensure_dir(path):
        """Crée un dossier s'il n'existe pas"""
        Path(path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def copy_dir(src, dst):
        """Copie un dossier"""
        if Path(dst).exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    @staticmethod
    def clean_dir(path):
        """Nettoie un dossier"""
        if Path(path).exists():
            shutil.rmtree(path)
        Path(path).mkdir(parents=True, exist_ok=True)

# ============================================
# INSTALLATEUR PYTHON
# ============================================

class PythonInstaller:
    """Installe les dépendances Python"""

    def __init__(self):
        self.venv_dir = ROOT_DIR / "venv"
        self.requirements = ROOT_DIR / "requirements.txt"

    def create_venv(self):
        """Crée l'environnement virtuel"""
        logger.info(" Création de l'environnement virtuel...")

        if self.venv_dir.exists():
            logger.info(" Environnement virtuel déjà existant")
            return True

        try:
            import venv
            venv.create(self.venv_dir, with_pip=True)
            logger.info(" Environnement virtuel créé")
            return True
        except Exception as e:
            logger.error(f" Erreur création venv: {e}")
            return False

    def install_dependencies(self):
        """Installe les dépendances"""
        logger.info(" Installation des dépendances Python...")

        if not self.venv_dir.exists():
            if not self.create_venv():
                return False

        # Chemin pip
        if sys.platform == 'win32':
            pip_path = self.venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = self.venv_dir / "bin" / "pip3"

        # Créer requirements.txt si inexistant
        if not self.requirements.exists():
            self.create_requirements()

        try:
            subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
            subprocess.run([str(pip_path), 'install', '-r', str(self.requirements)], check=True)
            logger.info(" Dépendances Python installées")
            return True
        except Exception as e:
            logger.error(f" Erreur installation dépendances: {e}")
            return False

    def create_requirements(self):
        """Crée le fichier requirements.txt"""
        requirements = """
torch>=2.0.0
flask>=2.3.0
flask-cors>=4.0.0
flask-socketio>=5.3.0
python-socketio>=5.9.0
python-dotenv>=1.0.0
pyjwt>=2.7.0
numpy>=1.24.0
scikit-learn>=1.3.0
psutil>=5.9.0
pandas>=2.0.0
requests>=2.31.0
pyinstaller>=5.13.0
        """.strip()

        with open(self.requirements, 'w') as f:
            f.write(requirements)
            logger.info(" requirements.txt créé")

            # ============================================
            # BUILD FRONTEND
            # ============================================

            class FrontendBuilder:
                """Construit le frontend React"""

    def __init__(self):
        self.frontend_dir = FRONTEND_DIR
        self.build_dir = FRONTEND_DIR / "build"

    def install_dependencies(self):
        """Installe les dépendances Node"""
        logger.info(" Installation des dépendances Node...")

        if not self.frontend_dir.exists():
            logger.error(" Dossier frontend non trouvé")
            return False

        try:
            # Vérifier si package.json existe
            package_json = self.frontend_dir / "package.json"
            if not package_json.exists():
                self.create_package_json()

            # Installer les dépendances
            subprocess.run(['npm', 'install'], cwd=str(self.frontend_dir), check=True)
            logger.info(" Dépendances Node installées")
            return True
        except Exception as e:
            logger.error(f" Erreur installation Node: {e}")
            return False

    def build(self):
        """Construit le frontend"""
        logger.info(" Build du frontend...")

        try:
            # Nettoyer l'ancien build
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)

            # Build
            subprocess.run(['npm', 'run', 'build'], cwd=str(self.frontend_dir), check=True)

            if not self.build_dir.exists():
                logger.error(" Build frontend échoué")
                return False

            logger.info(" Frontend build terminé")
            return True
        except Exception as e:
            logger.error(f" Erreur build frontend: {e}")
            return False

    def create_package_json(self):
        """Crée le package.json par défaut"""
        package_json = {
            "name": "yelmon-dev-x-frontend",
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "axios": "^1.4.0",
                "react-router-dom": "^6.14.0",
                "@codemirror/editor": "^6.0.0",
                "@codemirror/lang-python": "^6.0.0",
                "@codemirror/lang-javascript": "^6.0.0",
                "@codemirror/lang-java": "^6.0.0",
                "@codemirror/lang-cpp": "^6.0.0",
                "react-hot-toast": "^2.4.0",
                "socket.io-client": "^4.6.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }

        with open(self.frontend_dir / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)

# ============================================
# BUILD BACKEND
# ============================================

class BackendBuilder:
    """Construit le backend Python en exécutable"""

    def __init__(self):
        self.backend_dir = BACKEND_DIR
        self.dist_dir = DIST_DIR / "backend"

    def build_exe(self):
        """Construit l'exécutable backend avec PyInstaller"""
        logger.info(" Build du backend en exécutable...")

        # Créer le dossier de sortie
        self.dist_dir.mkdir(parents=True, exist_ok=True)

        # Vérifier PyInstaller
        try:
            import PyInstaller
        except ImportError:
            logger.info(" Installation de PyInstaller...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

        # Fichier d'entrée
        entry_point = self.backend_dir / "app.py"
        if not entry_point.exists():
            logger.error(f" app.py non trouvé: {entry_point}")
            return False

        # Commande PyInstaller
        cmd = [
            'pyinstaller',
            '--onefile',
            '--name', 'yelmon_backend',
            '--distpath', str(self.dist_dir),
            '--workpath', str(TEMP_DIR / "pyinstaller"),
            '--specpath', str(TEMP_DIR),
            '--add-data', f"{str(self.backend_dir / 'auth')}{os.pathsep}auth",
            '--add-data', f"{str(self.backend_dir / 'tokenizer')}{os.pathsep}tokenizer",
            '--add-data', f"{str(self.backend_dir / 'models')}{os.pathsep}models",
            '--add-data', f"{str(self.backend_dir / 'rag')}{os.pathsep}rag",
            '--add-data', f"{str(self.backend_dir / 'agent')}{os.pathsep}agent",
            '--hidden-import', 'torch',
            '--hidden-import', 'flask',
            '--hidden-import', 'flask_cors',
            '--hidden-import', 'flask_socketio',
            '--hidden-import', 'sklearn',
            '--hidden-import', 'numpy',
            str(entry_point)
        ]

        try:
            subprocess.run(cmd, check=True)
            logger.info(f" Backend exécutable créé: {self.dist_dir}")
            return True
        except Exception as e:
            logger.error(f" Erreur build backend: {e}")
            return False

# ============================================
# BUILD ELECTRON
# ============================================

class ElectronBuilder:
    """Construit l'application Electron"""

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.dist_dir = DIST_DIR

    def build(self):
        """Construit l'application Electron"""
        logger.info(" Build de l'application Electron...")

        # Vérifier que le build frontend existe
        frontend_build = FRONTEND_DIR / "build"
        if not frontend_build.exists():
            logger.error(" Build frontend non trouvé")
            return False

        try:
            # Installer electron-builder si nécessaire
            try:
                import electron_builder
            except ImportError:
                logger.info(" Installation de electron-builder...")
                subprocess.run(['npm', 'install', '-g', 'electron-builder'], check=True)

            # Build
            platform = BuildUtils.get_platform()

            if platform == 'win':
                cmd = ['npm', 'run', 'dist:win']
            elif platform == 'mac':
                cmd = ['npm', 'run', 'dist:mac']
            else:
                cmd = ['npm', 'run', 'dist:linux']

            subprocess.run(cmd, cwd=str(self.root_dir), check=True)
            logger.info(f" Application Electron construite")
            return True
        except Exception as e:
            logger.error(f" Erreur build Electron: {e}")
            return False

# ============================================
# CREATE INSTALLER
# ============================================

class InstallerCreator:
    """Crée l'installateur final"""

    def __init__(self):
        self.dist_dir = DIST_DIR
        self.installer_dir = DIST_DIR / "installer"

    def create_windows_installer(self):
        """Crée l'installateur Windows"""
        logger.info(" Création de l'installateur Windows...")

        installer_script = self.installer_dir / "create_installer.bat"

        # Créer le script d'installation
        installer_content = f"""@echo off
echo ========================================
echo     YELMON Dev X - Installateur
echo     Version {APP_VERSION}
echo ========================================
echo.

echo  Installation de YELMON Dev X...
echo.

REM Créer le dossier d'installation
set INSTALL_DIR=%USERPROFILE%\\AppData\\Local\\YELMON_Dev_X
echo  Dossier d'installation: %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo  Copie des fichiers...
xcopy /E /I /Y "%~dp0..\\*" "%INSTALL_DIR%\\"

echo  Installation des dépendances Python...
cd "%INSTALL_DIR%"
python -m venv venv
call venv\\Scripts\\activate
pip install -r requirements.txt

echo  Création du raccourci...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$env:USERPROFILE\\Desktop\\YELMON Dev X.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\YELMON_Launcher.py'; $Shortcut.Save()"

echo.
echo ========================================
echo  Installation terminée !
echo  Application installée dans: %INSTALL_DIR%
echo   Raccourci créé sur le bureau
echo ========================================
echo.
pause
        """

        self.installer_dir.mkdir(parents=True, exist_ok=True)
        with open(installer_script, 'w') as f:
            f.write(installer_content)

            logger.info(" Installateur Windows créé")
            return True

            def create_mac_installer(self):
                """Crée l'installateur Mac"""
                logger.info(" Création de l'installateur Mac...")

        installer_script = self.installer_dir / "create_installer.sh"

        installer_content = f"""#!/bin/bash
echo "========================================"
echo "    YELMON Dev X - Installateur"
echo "    Version {APP_VERSION}"
echo "========================================"
echo ""

echo " Installation de YELMON Dev X..."
echo ""

# Dossier d'installation
INSTALL_DIR="$HOME/.local/share/YELMON_Dev_X"
echo " Dossier d'installation: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"

echo " Copie des fichiers..."
cp -r "$(dirname "$0")/../*" "$INSTALL_DIR/"

echo " Installation des dépendances Python..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo " Création du raccourci..."
cat > "$HOME/Desktop/YELMON Dev X.command" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 yelmon.py
EOF
chmod +x "$HOME/Desktop/YELMON Dev X.command"

echo ""
echo "========================================"
echo " Installation terminée !"
echo " Application installée dans: $INSTALL_DIR"
echo "  Raccourci créé sur le bureau"
echo "========================================"
echo ""
        """

        self.installer_dir.mkdir(parents=True, exist_ok=True)
        with open(installer_script, 'w') as f:
            f.write(installer_content)
            os.chmod(installer_script, 0o755)

            logger.info(" Installateur Mac créé")
            return True

            def create_linux_installer(self):
                """Crée l'installateur Linux"""
                logger.info(" Création de l'installateur Linux...")

        installer_script = self.installer_dir / "create_installer.sh"

        installer_content = f"""#!/bin/bash
echo "========================================"
echo "    YELMON Dev X - Installateur"
echo "    Version {APP_VERSION}"
echo "========================================"
echo ""

echo " Installation de YELMON Dev X..."
echo ""

# Dossier d'installation
INSTALL_DIR="$HOME/.local/share/YELMON_Dev_X"
echo " Dossier d'installation: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"

echo " Copie des fichiers..."
cp -r "$(dirname "$0")/../*" "$INSTALL_DIR/"

echo " Installation des dépendances Python..."
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo " Création du raccourci..."
cat > "$HOME/Desktop/YELMON Dev X.desktop" << EOF
[Desktop Entry]
Name=YELMON Dev X
Comment=Assistant de codage IA
Exec=$INSTALL_DIR/yelmon.py
Icon=$INSTALL_DIR/assets/icon.png
Terminal=true
Type=Application
Categories=Development;
EOF
chmod +x "$HOME/Desktop/YELMON Dev X.desktop"

echo ""
echo "========================================"
echo " Installation terminée !"
echo " Application installée dans: $INSTALL_DIR"
echo "  Raccourci créé sur le bureau"
echo "========================================"
echo ""
        """

        self.installer_dir.mkdir(parents=True, exist_ok=True)
        with open(installer_script, 'w') as f:
            f.write(installer_content)
            os.chmod(installer_script, 0o755)

            logger.info(" Installateur Linux créé")
            return True

            def create_portable_zip(self):
                """Crée une version portable ZIP"""
                logger.info(" Création de la version portable...")

        zip_filename = DIST_DIR / f"{APP_NAME}_v{APP_VERSION}_portable.zip"

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Ajouter tous les fichiers
            for root, dirs, files in os.walk(ROOT_DIR):
                # Exclure certains dossiers
                exclude = ['dist', 'build', 'temp_build', '__pycache__', 'venv', 'node_modules']
                if any(e in root for e in exclude):
                    continue

                for file in files:
                    if file.endswith(('.pyc', '.pyo')):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(ROOT_DIR)
                    zipf.write(file_path, arcname)

        logger.info(f" Version portable créée: {zip_filename}")
        return True

# ============================================
# BUILD AUTOMATIQUE COMPLET
# ============================================

class YELMONBuilder:
    """Build complet de YELMON Dev X"""

    def __init__(self):
        self.start_time = datetime.now()
        self.success = True
        self.errors = []
        self.build_steps = []

    def log_step(self, name, func):
        """Exécute une étape de build"""
        logger.info(f" Étape: {name}")
        try:
            result = func()
            if result:
                logger.info(f" {name} - OK")
                self.build_steps.append({"name": name, "status": "success"})
            else:
                logger.error(f" {name} - ÉCHEC")
                self.errors.append(name)
                self.success = False
                self.build_steps.append({"name": name, "status": "failed"})
            return result
        except Exception as e:
            logger.error(f" {name} - Erreur: {e}")
            self.errors.append(name)
            self.success = False
            self.build_steps.append({"name": name, "status": "error", "error": str(e)})
            return False

    def build(self):
        """Exécute le build complet"""
        logger.info(" Démarrage du build YELMON Dev X")
        logger.info("=" * 50)

        # Créer les dossiers
        BuildUtils.ensure_dir(DIST_DIR)
        BuildUtils.ensure_dir(TEMP_DIR)
        BuildUtils.clean_dir(BUILD_DIR)

        # Étape 1: Installer les dépendances Python
        python_installer = PythonInstaller()
        self.log_step("Installation dépendances Python", python_installer.install_dependencies)

        # Étape 2: Installer les dépendances Node
        frontend_builder = FrontendBuilder()
        self.log_step("Installation dépendances Node", frontend_builder.install_dependencies)

        # Étape 3: Build frontend
        self.log_step("Build frontend", frontend_builder.build)

        # Étape 4: Build backend
        backend_builder = BackendBuilder()
        self.log_step("Build backend", backend_builder.build_exe)

        # Étape 5: Build Electron
        electron_builder = ElectronBuilder()
        self.log_step("Build Electron", electron_builder.build)

        # Étape 6: Créer les installateurs
        installer_creator = InstallerCreator()
        platform = BuildUtils.get_platform()

        if platform == 'win':
            self.log_step("Création installateur Windows", installer_creator.create_windows_installer)
        elif platform == 'mac':
            self.log_step("Création installateur Mac", installer_creator.create_mac_installer)
        elif platform == 'linux':
            self.log_step("Création installateur Linux", installer_creator.create_linux_installer)

        # Étape 7: Créer version portable
        self.log_step("Création version portable", installer_creator.create_portable_zip)

        # Résumé
        duration = datetime.now() - self.start_time
        logger.info("=" * 50)

        if self.success:
            logger.info(f" BUILD TERMINÉ AVEC SUCCÈS en {duration}")
            logger.info(f" Dossier de sortie: {DIST_DIR}")
            logger.info(" Installateurs disponibles:")

            platform = BuildUtils.get_platform()
            if platform == 'win':
                logger.info(f"   - {DIST_DIR}/installer/create_installer.bat")
                logger.info(f"   - {DIST_DIR}/{APP_NAME}_v{APP_VERSION}_portable.zip")
            elif platform == 'mac':
                logger.info(f"   - {DIST_DIR}/installer/create_installer.sh")
                logger.info(f"   - {DIST_DIR}/{APP_NAME}_v{APP_VERSION}_portable.zip")
            else:
                logger.info(f"   - {DIST_DIR}/installer/create_installer.sh")
                logger.info(f"   - {DIST_DIR}/{APP_NAME}_v{APP_VERSION}_portable.zip")
        else:
            logger.error(f" BUILD ÉCHOUÉ - {len(self.errors)} erreur(s)")
            for error in self.errors:
                logger.error(f"   - {error}")

        return self.success

# ============================================
# AUTO-DEPLOIEMENT
# ============================================

class AutoDeploy:
    """Déploiement automatique après build"""

    def __init__(self):
        self.dist_dir = DIST_DIR
        self.install_path = None

    def find_install_path(self):
        """Trouve le chemin d'installation"""
        if sys.platform == 'win32':
            return Path(os.environ.get('LOCALAPPDATA', '')) / "YELMON_Dev_X"
        elif sys.platform == 'darwin':
            return Path.home() / ".local" / "share" / "YELMON_Dev_X"
        else:
            return Path.home() / ".local" / "share" / "YELMON_Dev_X"

    def deploy(self):
        """Déploie l'application"""
        logger.info(" Déploiement automatique...")

        self.install_path = self.find_install_path()
        logger.info(f" Dossier d'installation: {self.install_path}")

        # Créer le dossier
        self.install_path.mkdir(parents=True, exist_ok=True)

        # Copier les fichiers
        logger.info(" Copie des fichiers...")

        # Copier le backend
        backend_src = self.dist_dir / "backend"
        if backend_src.exists():
            backend_dst = self.install_path / "backend"
            if backend_dst.exists():
                shutil.rmtree(backend_dst)
            shutil.copytree(backend_src, backend_dst)

        # Copier le frontend
        frontend_src = FRONTEND_DIR / "build"
        if frontend_src.exists():
            frontend_dst = self.install_path / "frontend" / "build"
            frontend_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(frontend_src, frontend_dst)

        # Copier les scripts
        shutil.copy(ROOT_DIR / "yelmon.py", self.install_path)
        shutil.copy(ROOT_DIR / "YELMON_Launcher.py", self.install_path)

        # Copier requirements.txt
        shutil.copy(ROOT_DIR / "requirements.txt", self.install_path)

        # Créer le script de lancement
        self.create_launcher_scripts()

        logger.info(f" Déploiement terminé dans: {self.install_path}")
        return True

    def create_launcher_scripts(self):
        """Crée les scripts de lancement"""

        if sys.platform == 'win32':
            # Batch file
            bat_path = self.install_path / "YELMON_Dev_X.bat"
            bat_content = f"""@echo off
echo  YELMON Dev X v{APP_VERSION}
echo Démarrage de l'application...
cd /d "{self.install_path}"
python yelmon.py start
pause
            """
            with open(bat_path, 'w') as f:
                f.write(bat_content)

                # PowerShell
                ps_path = self.install_path / "YELMON_Dev_X.ps1"
                ps_content = f"""Write-Host " YELMON Dev X v{APP_VERSION}" -ForegroundColor Cyan
                                    Write-Host "Démarrage de l'application..." -ForegroundColor Yellow
                                    Set-Location "{self.install_path}"
                                    & python yelmon.py start
                """
                with open(ps_path, 'w') as f:
                    f.write(ps_content)

        else:
            # Shell script
            sh_path = self.install_path / "YELMON_Dev_X.sh"
            sh_content = f"""#!/bin/bash
echo " YELMON Dev X v{APP_VERSION}"
echo "Démarrage de l'application..."
cd "{self.install_path}"
python3 yelmon.py start
            """
            with open(sh_path, 'w') as f:
                f.write(sh_content)
                os.chmod(sh_path, 0o755)

# INTERFACE CLI DE BUILD
# ============================================

def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description='YELMON Dev X - Build Automatique')
    parser.add_argument('--build', action='store_true', help='Construire l\'application')
    parser.add_argument('--deploy', action='store_true', help='Déployer après build')
    parser.add_argument('--clean', action='store_true', help='Nettoyer les fichiers de build')
    parser.add_argument('--installer', action='store_true', help='Créer l\'installateur')
    parser.add_argument('--portable', action='store_true', help='Créer la version portable')
    parser.add_argument('--all', action='store_true', help='Tout construire et déployer')

    args = parser.parse_args()

    if args.clean:
        logger.info(" Nettoyage des fichiers de build...")
        for dir_path in [DIST_DIR, BUILD_DIR, TEMP_DIR]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f" {dir_path} supprimé")
        return

    if args.all or args.build:
        builder = YELMONBuilder()
        if builder.build():
            logger.info(" Build terminé avec succès!")

            if args.deploy or args.all:
                deployer = AutoDeploy()
                deployer.deploy()

                logger.info("=" * 50)
                logger.info(" YELMON Dev X est maintenant installé sur votre PC!")
                logger.info(f" Emplacement: {deployer.install_path}")
                logger.info(" Lancez 'YELMON_Dev_X.bat' (Windows) ou 'YELMON_Dev_X.sh' (Mac/Linux)")
                logger.info("=" * 50)
        else:
            logger.error(" Build échoué")
            sys.exit(1)

if __name__ == '__main__':
    main()
