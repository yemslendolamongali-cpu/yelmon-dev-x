# auto_deploy.py - Téléchargement et installation automatique
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YELMON Dev X - Auto Deploy
Télécharge et installe automatiquement YELMON Dev X
"""

import os
import sys
import subprocess
import shutil
import json
import urllib.request
import zipfile
import tarfile
from pathlib import Path
import platform
import logging

# Configuration
REPO_URL = "https://github.com/yelmon/yelmon-dev-x/releases/latest"
APP_NAME = "YELMON_Dev_X"
APP_VERSION = "1.0.0"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [YELMON Deploy] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoDeployYELMON:
    """Téléchargement et déploiement automatique"""

    def __init__(self):
        self.install_dir = Path.home() / "YELMON_Dev_X"
        self.temp_dir = Path.home() / ".yelmon_temp"
        self.platform = platform.system().lower()

    def get_download_url(self):
        """Récupère l'URL de téléchargement"""
        if self.platform == 'windows':
            return f"https://github.com/yelmon/yelmon-dev-x/releases/download/v{APP_VERSION}/YELMON_Dev_X_v{APP_VERSION}_Setup.exe"
        elif self.platform == 'darwin':
            return f"https://github.com/yelmon/yelmon-dev-x/releases/download/v{APP_VERSION}/YELMON_Dev_X_v{APP_VERSION}.dmg"
        else:
            return f"https://github.com/yelmon/yelmon-dev-x/releases/download/v{APP_VERSION}/YELMON_Dev_X_v{APP_VERSION}.AppImage"

    def download(self):
        """Télécharge l'installateur"""
        logger.info(" Téléchargement de YELMON Dev X...")

        url = self.get_download_url()
        filename = url.split('/')[-1]
        download_path = self.temp_dir / filename

        self.temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f" Téléchargement depuis: {url}")
            urllib.request.urlretrieve(url, download_path)
            logger.info(f" Téléchargement terminé: {download_path}")
            return download_path
        except Exception as e:
            logger.error(f" Erreur de téléchargement: {e}")
            return None

    def install(self, file_path):
        """Installe l'application"""
        logger.info(" Installation de YELMON Dev X...")

        if self.platform == 'windows':
            # Exécuter l'installateur Windows
            subprocess.run([str(file_path), '/S'], check=True)
        elif self.platform == 'darwin':
            # Mac - monter le DMG et copier
            subprocess.run(['hdiutil', 'attach', str(file_path)], check=True)
            # Copier vers /Applications
            subprocess.run(['cp', '-R', '/Volumes/YELMON Dev X/YELMON Dev X.app', '/Applications/'], check=True)
            subprocess.run(['hdiutil', 'detach', '/Volumes/YELMON Dev X'], check=True)
        else:
            # Linux - rendre exécutable et lancer
            os.chmod(file_path, 0o755)
            subprocess.run([str(file_path), '--appimage-extract'], check=True)

            # Copier vers /opt
            if not (Path('/opt') / 'YELMON_Dev_X').exists():
                subprocess.run(['sudo', 'mkdir', '-p', '/opt/YELMON_Dev_X'], check=True)
                subprocess.run(['sudo', 'cp', '-r', 'squashfs-root/*', '/opt/YELMON_Dev_X/'], check=True)
                subprocess.run(['sudo', 'ln', '-sf', '/opt/YELMON_Dev_X/yelmon', '/usr/local/bin/yelmon'], check=True)

        logger.info(" Installation terminée!")
        return True

def main():
    """Point d'entrée"""
    logger.info(" YELMON Dev X - Auto Deploy")
    logger.info("=" * 50)

    deployer = AutoDeployYELMON()

    # Télécharger
    file_path = deployer.download()
    if not file_path:
        logger.error(" Échec du téléchargement")
        return

    # Installer
    if deployer.install(file_path):
        logger.info(" Installation terminée!")
if __name__ == '__main__':
    main()
