# installer.py - Installateur final pour l'utilisateur
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YELMON Dev X - Installateur Automatique
Télécharge, installe et configure YELMON Dev X
"""

import os
import sys
import subprocess
import shutil
import zipfile
import tarfile
import platform
from pathlib import Path
import json
import urllib.request
import tempfile
import time

APP_NAME = "YELMON Dev X"
APP_VERSION = "1.0.0"
APP_AUTHOR = "YELMON Team"

class YELMONInstaller:
    """Installateur principal"""

    def __init__(self):
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()
        self.home = Path.home()
        self.install_dir = self.home / "YELMON_Dev_X"
        self.temp_dir = Path(tempfile.gettempdir()) / "yelmon_install"

        # Créer les dossiers
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.steps = []
        self.current_step = 0

    def log(self, message, type="info"):
        """Affiche un message formaté"""
        icon = {
            "info": "ℹ",
            "success": "",
            "error": "",
            "warning": "",
            "step": ""
        }.get(type, "ℹ")
        print(f"{icon} {message}")

    def check_requirements(self):
        """Vérifie les prérequis"""
        self.log("Vérification des prérequis...", "step")

        requirements = []

        # Vérifier Python
        try:
            python_version = sys.version_info
            if python_version.major >= 3 and python_version.minor >= 8:
                requirements.append(("Python", True, f"{python_version.major}.{python_version.minor}"))
            else:
                requirements.append(("Python", False, "Python 3.8+ requis"))
        except:
            requirements.append(("Python", False, "Python non trouvé"))

        # Vérifier pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, check=True)
            requirements.append(("pip", True, "Installé"))
        except:
            requirements.append(("pip", False, "pip non trouvé"))

        # Afficher les résultats
        all_ok = True
        for name, status, version in requirements:
            if status:
                self.log(f"  {name}:  {version}", "success")
            else:
                self.log(f"  {name}:  {version}", "error")
                all_ok = False

        return all_ok

    def download_files(self):
        """Télécharge les fichiers"""
        self.log("Téléchargement des fichiers...", "step")

        # URLs des fichiers (à adapter)
        urls = {
            "backend": "https://github.com/yelmon/yelmon-dev-x/releases/download/v1.0.0/backend.zip",
            "frontend": "https://github.com/yelmon/yelmon-dev-x/releases/download/v1.0.0/frontend.zip",
            "scripts": "https://github.com/yelmon/yelmon-dev-x/releases/download/v1.0.0/scripts.zip"
        }

        downloaded = []

        for name, url in urls.items():
            try:
                self.log(f"  Téléchargement de {name}...")
                file_path = self.temp_dir / f"{name}.zip"
                urllib.request.urlretrieve(url, file_path)
                downloaded.append(file_path)
                self.log(f"   {name} téléchargé", "success")
            except Exception as e:
                self.log(f"   Erreur téléchargement {name}: {e}", "error")
                return None

        return downloaded

    def extract_files(self, files):
        """Extrait les fichiers"""
        self.log("Extraction des fichiers...", "step")

        extract_dir = self.temp_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)

        for file_path in files:
            try:
                self.log(f"  Extraction de {file_path.name}...")
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                self.log(f"   {file_path.name} extrait", "success")
            except Exception as e:
                self.log(f"   Erreur extraction {file_path}: {e}", "error")
                return None

        return extract_dir

    def install_files(self, source_dir):
        """Installe les fichiers"""
        self.log("Installation des fichiers...", "step")

        # Créer le dossier d'installation
        self.install_dir.mkdir(parents=True, exist_ok=True)

        # Copier les fichiers
        for item in source_dir.iterdir():
            dest = self.install_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        self.log(f" Fichiers installés dans {self.install_dir}", "success")
        return True

    def install_dependencies(self):
        """Installe les dépendances"""
        self.log("Installation des dépendances...", "step")

        # Créer l'environnement virtuel
        venv_dir = self.install_dir / "venv"

        if not venv_dir.exists():
            self.log("  Création de l'environnement virtuel...")
            subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)

        # Installer les dépendances
        self.log("  Installation des dépendances Python...")

        if self.platform == 'win32':
            pip_path = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = venv_dir / "bin" / "pip3"

        requirements = self.install_dir / "requirements.txt"
        if requirements.exists():
            subprocess.run([str(pip_path), 'install', '-r', str(requirements)], check=True)

        self.log(" Dépendances installées", "success")
        return True

    def create_shortcuts(self):
        """Crée les raccourcis"""
        self.log("Création des raccourcis...", "step")

        if self.platform == 'win32':
            # Raccourci Windows
            shortcut_path = self.home / "Desktop" / f"{APP_NAME}.lnk"
            target = str(self.install_dir / "YELMON_Launcher.py")

            # Créer le raccourci avec PowerShell
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "python.exe"
$Shortcut.Arguments = '"{target}"'
$Shortcut.WorkingDirectory = "{self.install_dir}"
$Shortcut.Save()
            '''
            subprocess.run(['powershell', '-Command', ps_script], check=True)

        elif self.platform == 'darwin':
            # Raccourci Mac
            shortcut_path = self.home / "Desktop" / f"{APP_NAME}.command"
            content = f'''#!/bin/bash
cd "{self.install_dir}"
./venv/bin/python3 YELMON_Launcher.py
            '''
            with open(shortcut_path, 'w') as f:
                f.write(content)
                os.chmod(shortcut_path, 0o755)

        else:
            # Raccourci Linux
            shortcut_path = self.home / "Desktop" / f"{APP_NAME}.desktop"
            content = f'''[Desktop Entry]
                                                                    Name={APP_NAME}
                                                                    Comment=Assistant de codage IA
                                                                    Exec={self.install_dir}/venv/bin/python3 {self.install_dir}/YELMON_Launcher.py
                                                                    Icon={self.install_dir}/assets/icon.png
                                                                    Terminal=true
                                                                    Type=Application
                                                                    Categories=Development;
            '''
            with open(shortcut_path, 'w') as f:
                f.write(content)
                os.chmod(shortcut_path, 0o755)

        self.log(f" Raccourcis créés", "success")
        return True

    def install(self):
        """Exécute l'installation complète"""
        print("=" * 60)
        print(f"  {APP_NAME} - Installateur Automatique")
        print(f"  Version {APP_VERSION}")
        print("=" * 60)
        print()

        # Vérifier les prérequis
        if not self.check_requirements():
            self.log("Prérequis non satisfaits. Installation annulée.", "error")
            return False

        # Télécharger
        files = self.download_files()
        if not files:
            self.log("Échec du téléchargement", "error")
            return False

        # Extraire
        extracted = self.extract_files(files)
        if not extracted:
            self.log("Échec de l'extraction", "error")
            return False

        # Installer
        if not self.install_files(extracted):
            self.log("Échec de l'installation", "error")
            return False

        # Dépendances
        if not self.install_dependencies():
            self.log("Échec de l'installation des dépendances", "error")
            return False

        # Raccourcis
        if not self.create_shortcuts():
            self.log("Échec de la création des raccourcis", "error")
            return False

        # Nettoyage
        shutil.rmtree(self.temp_dir)

        print()
        print("=" * 60)
        self.log(" Installation terminée avec succès!", "success")
        print(f" Emplacement: {self.install_dir}")
        print(" Lancez YELMON Dev X depuis le raccourci sur votre bureau!")
        print("=" * 60)

        return True

def main():
    installer = YELMONInstaller()
    installer.install()

if __name__ == '__main__':
                    main()
