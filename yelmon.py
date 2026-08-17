# yelmon.py - Point d'entrée principal de YELMON Dev X
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YELMON Dev X - Assistant de codage IA
Version: 1.0.0
Auteur: YELMON Team
Description: Point d'entrée principal de l'application
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
import signal
import logging
from pathlib import Path
from typing import Optional
import json
import socket
import psutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [YELMON Dev X] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================
# CONSTANTES
# ============================================

APP_NAME = "YELMON Dev X"
APP_VERSION = "1.0.0"
APP_AUTHOR = "YELMON Team"

# Ports
BACKEND_PORT = 5001
FRONTEND_PORT = 3000

# Chemins
ROOT_DIR = Path(__file__).parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
VENV_DIR = ROOT_DIR / "venv"
LOG_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"

# ============================================
# UTILITAIRES
# ============================================

def check_port_available(port: int) -> bool:
    """Vérifie si un port est disponible"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

def find_free_port(start_port: int) -> int:
    """Trouve un port libre"""
    port = start_port
    while not check_port_available(port):
        port += 1
        return port

def kill_process_on_port(port: int):
    """Tue les processus utilisant un port"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    logger.info(f"Kill process {proc.pid} using port {port}")
                    proc.terminate()
                    proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass

def get_python_path() -> str:
    """Retourne le chemin de l'exécutable Python"""
    if sys.platform == 'win32':
        return str(VENV_DIR / "Scripts" / "python.exe")
        return str(VENV_DIR / "bin" / "python3")

def get_pip_path() -> str:
    """Retourne le chemin de pip"""
    if sys.platform == 'win32':
        return str(VENV_DIR / "Scripts" / "pip.exe")
        return str(VENV_DIR / "bin" / "pip3")

def get_node_path() -> str:
    """Retourne le chemin de node"""
    try:
        import shutil
        return shutil.which('node') or 'node'
    except:
        return 'node'

def get_npm_path() -> str:
    """Retourne le chemin de npm"""
    try:
        import shutil
        return shutil.which('npm') or 'npm'
    except:
        return 'npm'

# ============================================
# INSTALLATION
# ============================================

class YELMONInstaller:
    """Installateur de YELMON Dev X"""

    def __init__(self):
        self.venv_created = False
        self.deps_installed = False
        self.node_deps_installed = False
        self.frontend_built = False

    def check_requirements(self) -> bool:
        """Vérifie les prérequis"""
        logger.info(" Vérification des prérequis...")

        # Vérifier Python
        try:
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                logger.error(" Python 3.8+ requis")
                return False
            logger.info(f" Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        except:
            logger.error(" Python non trouvé")
            return False

        # Vérifier Node.js
        try:
            result = subprocess.run([get_node_path(), '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f" Node.js {result.stdout.strip()}")
            else:
                logger.error(" Node.js non trouvé")
                return False
        except:
            logger.error(" Node.js non trouvé")
            return False

        # Vérifier npm
        try:
            result = subprocess.run([get_npm_path(), '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f" npm {result.stdout.strip()}")
            else:
                logger.error(" npm non trouvé")
                return False
        except:
            logger.error(" npm non trouvé")
            return False

        # Vérifier CUDA pour GPU
        try:
            import torch
            if torch.cuda.is_available():
                logger.info(f" GPU disponible (CUDA {torch.version.cuda})")
            else:
                logger.info("ℹ GPU non disponible - utilisation CPU")
        except:
            logger.info("ℹ PyTorch non installé - installation en cours...")

        return True

    def create_venv(self) -> bool:
        """Crée l'environnement virtuel"""
        logger.info(" Création de l'environnement virtuel...")

        if VENV_DIR.exists():
            logger.info(" Environnement virtuel déjà existant")
            self.venv_created = True
            return True

        try:
            import venv
            venv.create(VENV_DIR, with_pip=True)
            self.venv_created = True
            logger.info(f" Environnement virtuel créé: {VENV_DIR}")
            return True
        except Exception as e:
            logger.error(f" Erreur création venv: {e}")
            return False

    def install_backend_deps(self) -> bool:
        """Installe les dépendances backend"""
        logger.info(" Installation des dépendances Python...")

        pip_path = get_pip_path()
        req_file = ROOT_DIR / "requirements.txt"

        if not req_file.exists():
            logger.warning(" requirements.txt non trouvé")
            # Créer un requirements.txt par défaut
            with open(req_file, 'w') as f:
                f.write("""
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
                """.strip())

                try:
                    subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
                    subprocess.run([pip_path, 'install', '-r', str(req_file)], check=True)
                    self.deps_installed = True
                    logger.info(" Dépendances Python installées")
                    return True
                except Exception as e:
                    logger.error(f" Erreur installation dépendances: {e}")
                    return False

                    def install_frontend_deps(self) -> bool:
                        """Installe les dépendances frontend"""
                        logger.info(" Installation des dépendances Node...")

        if not FRONTEND_DIR.exists():
            logger.warning(" Dossier frontend non trouvé")
            return False

        package_json = FRONTEND_DIR / "package.json"
        if not package_json.exists():
            logger.warning(" package.json non trouvé")
            return False

        try:
            # Installer les dépendances
            subprocess.run([get_npm_path(), 'install'], cwd=str(FRONTEND_DIR), check=True)
            self.node_deps_installed = True
            logger.info(" Dépendances Node installées")

            # Build du frontend
            logger.info(" Build du frontend...")
            subprocess.run([get_npm_path(), 'run', 'build'], cwd=str(FRONTEND_DIR), check=True)
            self.frontend_built = True
            logger.info(" Frontend build terminé")
            return True
        except Exception as e:
            logger.error(f" Erreur installation frontend: {e}")
            return False

    def install(self) -> bool:
        """Installation complète"""
        logger.info(f" Installation de {APP_NAME} v{APP_VERSION}")

        steps = [
            ("Vérification des prérequis", self.check_requirements),
            ("Création de l'environnement virtuel", self.create_venv),
            ("Installation des dépendances backend", self.install_backend_deps),
            ("Installation des dépendances frontend", self.install_frontend_deps),
        ]

        for step_name, step_func in steps:
            logger.info(f" {step_name}...")
            if not step_func():
                logger.error(f" Échec: {step_name}")
                return False

        logger.info(" Installation terminée avec succès!")
        return True

# ============================================
# LAUNCHER
# ============================================

class YELMONLauncher:
    """Launcher de YELMON Dev X"""

    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.electron_process = None
        self.is_running = False

        # Créer les dossiers nécessaires
        LOG_DIR.mkdir(exist_ok=True)
        DATA_DIR.mkdir(exist_ok=True)

    def start_backend(self) -> bool:
        """Démarre le backend Flask"""
        logger.info(" Démarrage du backend YELMON...")

        # Vérifier si le port est disponible
        if not check_port_available(BACKEND_PORT):
            logger.warning(f" Port {BACKEND_PORT} occupé, recherche d'un port libre...")
            port = find_free_port(BACKEND_PORT)
        else:
            port = BACKEND_PORT

        # Kill les processus existants sur le port
        kill_process_on_port(port)

        # Démarrer le backend
        python_path = get_python_path()
        backend_script = BACKEND_DIR / "app.py"

        if not backend_script.exists():
            logger.error(f" app.py non trouvé: {backend_script}")
            return False

        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = str(BACKEND_DIR)
            env['FLASK_APP'] = str(backend_script)
            env['PORT'] = str(port)

            self.backend_process = subprocess.Popen(
                [python_path, str(backend_script)],
                cwd=str(BACKEND_DIR),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Attendre que le backend soit prêt
            time.sleep(3)

            # Vérifier si le processus est en vie
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                logger.error(f" Backend échoué: {stderr}")
                return False

            logger.info(f" Backend démarré sur le port {port}")
            return True

        except Exception as e:
            logger.error(f" Erreur démarrage backend: {e}")
            return False

    def start_frontend(self) -> bool:
        """Démarre le frontend React en mode développement"""
        logger.info(" Démarrage du frontend YELMON...")

        if not FRONTEND_DIR.exists():
            logger.error(" Dossier frontend non trouvé")
            return False

        try:
            # En mode développement, on utilise le serveur de dev React
            if (FRONTEND_DIR / "build").exists():
                # Mode production
                logger.info(" Mode production - utilisation des fichiers build")
                self.start_electron()
                return True

            # Mode développement
            self.frontend_process = subprocess.Popen(
                [get_npm_path(), 'start'],
                cwd=str(FRONTEND_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            time.sleep(5)

            if self.frontend_process.poll() is not None:
                stdout, stderr = self.frontend_process.communicate()
                logger.error(f" Frontend échoué: {stderr}")
                return False

            logger.info(f" Frontend démarré sur le port {FRONTEND_PORT}")
            return True

        except Exception as e:
            logger.error(f" Erreur démarrage frontend: {e}")
            return False

    def start_electron(self) -> bool:
        """Démarre l'application Electron"""
        logger.info(" Démarrage d'Electron...")

        try:
            # Vérifier si les fichiers build existent
            build_dir = ROOT_DIR / "frontend" / "build"
            if not build_dir.exists():
                logger.warning(" Build frontend non trouvé, construction en cours...")
                subprocess.run([get_npm_path(), 'run', 'build'], cwd=str(FRONTEND_DIR), check=True)

            # Démarrer Electron
            self.electron_process = subprocess.Popen(
                [get_npm_path(), 'start'],
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            time.sleep(3)

            if self.electron_process.poll() is not None:
                stdout, stderr = self.electron_process.communicate()
                logger.error(f" Electron échoué: {stderr}")
                return False

            logger.info(" Electron démarré")
            return True

        except Exception as e:
            logger.error(f" Erreur démarrage Electron: {e}")
            return False

    def start(self, mode: str = 'full') -> bool:
        """Démarre YELMON Dev X"""
        logger.info(f" Démarrage de {APP_NAME} v{APP_VERSION}")

        # Vérifier l'installation
        if not self.check_installation():
            logger.warning(" Installation incomplète, lancement de l'installateur...")
            installer = YELMONInstaller()
            if not installer.install():
                logger.error(" Installation échouée")
                return False

        # Démarrer en fonction du mode
        if mode in ['full', 'backend']:
            if not self.start_backend():
                return False

        if mode in ['full', 'frontend']:
            if not self.start_frontend():
                return False

        if mode == 'electron':
            if not self.start_electron():
                return False

        self.is_running = True
        logger.info(f" {APP_NAME} démarré avec succès!")
        return True

    def check_installation(self) -> bool:
        """Vérifie si l'installation est complète"""
        # Vérifier l'environnement virtuel
        if not VENV_DIR.exists():
            return False

        # Vérifier les dépendances backend
        python_path = get_python_path()
        try:
            result = subprocess.run(
                [python_path, '-c', 'import flask, torch, flask_cors, flask_socketio'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                return False
        except:
            return False

        # Vérifier le frontend
        if not (FRONTEND_DIR / "build").exists():
            return False

        return True

    def stop(self):
        """Arrête YELMON Dev X"""
        logger.info(" Arrêt de YELMON Dev X...")

        processes = [
            (self.backend_process, "Backend"),
            (self.frontend_process, "Frontend"),
            (self.electron_process, "Electron")
        ]

        for proc, name in processes:
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                    logger.info(f" {name} arrêté")
                except Exception as e:
                    logger.warning(f" Erreur arrêt {name}: {e}")

        self.is_running = False
        logger.info(" YELMON Dev X arrêté")

    def get_status(self) -> dict:
        """Retourne le statut de l'application"""
        return {
            'app_name': APP_NAME,
            'version': APP_VERSION,
            'is_running': self.is_running,
            'backend': self.backend_process is not None and self.backend_process.poll() is None,
            'frontend': self.frontend_process is not None and self.frontend_process.poll() is None,
            'electron': self.electron_process is not None and self.electron_process.poll() is None,
        }

# ============================================
# INTERFACE CLI
# ============================================

class YELMONCLI:
    """Interface en ligne de commande YELMON"""

    def __init__(self):
        self.launcher = YELMONLauncher()

    def show_banner(self):
        """Affiche la bannière YELMON"""
        banner = """
















              YELMON Dev X - v1.0.0
         Assistant de Codage IA Nouvelle Génération

              "Codez plus vite, codez mieux"


        """
        print(banner)

    def show_help(self):
        """Affiche l'aide"""
        help_text = """

                       AIDE YELMON


  COMMANDES DISPONIBLES :

  start    - Démarrer YELMON Dev X
  stop     - Arrêter YELMON Dev X
  status   - Afficher le statut
  install  - Installer ou réinstaller
  help     - Afficher cette aide
  exit     - Quitter le CLI

  OPTIONS :
  --mode=full    - Démarrer tout (défaut)
  --mode=backend - Démarrer seulement le backend
  --mode=frontend - Démarrer seulement le frontend
  --mode=electron - Démarrer seulement Electron

  EXEMPLES :
  yelmon start --mode=full
  yelmon status
  yelmon install


        """
        print(help_text)

    def run(self, args=None):
        """Exécute le CLI"""
        self.show_banner()

        if args is None:
            args = sys.argv[1:]

        if not args:
            self.show_help()
            return

        command = args[0].lower()
        options = {}

        for arg in args[1:]:
            if arg.startswith('--'):
                if '=' in arg:
                    key, value = arg[2:].split('=', 1)
                    options[key] = value
                else:
                    options[arg[2:]] = True

        if command == 'start':
            mode = options.get('mode', 'full')
            if self.launcher.start(mode):
                print(f"\n {APP_NAME} démarré avec succès!")
                print(f" Backend: http://localhost:{BACKEND_PORT}")
                print(" Logs disponibles dans ./logs/")
                print("\n Appuyez sur Ctrl+C pour arrêter")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n Arrêt en cours...")
                    self.launcher.stop()
            else:
                print(" Échec du démarrage")
                sys.exit(1)

        elif command == 'stop':
            self.launcher.stop()

        elif command == 'status':
            status = self.launcher.get_status()
            print(f"\n Statut de {APP_NAME}:")
            print(f"  Version: {status['version']}")
            print(f"  En cours: {' Oui' if status['is_running'] else ' Non'}")
            print(f"  Backend: {' Actif' if status['backend'] else ' Inactif'}")
            print(f"  Frontend: {' Actif' if status['frontend'] else ' Inactif'}")
            print(f"  Electron: {' Actif' if status['electron'] else ' Inactif'}")

        elif command == 'install':
            installer = YELMONInstaller()
            if installer.install():
                print("\n Installation terminée avec succès!")
                print(" Lancez 'yelmon start' pour démarrer")
            else:
                print("\n Échec de l'installation")
                sys.exit(1)

        elif command == 'help':
            self.show_help()

        elif command == 'exit':
            print(" Au revoir!")
            sys.exit(0)

        else:
            print(f" Commande inconnue: {command}")
            self.show_help()
            sys.exit(1)

# ============================================
# POINT D'ENTRÉE
# ============================================

def main():
    """Point d'entrée principal"""
    cli = YELMONCLI()
    cli.run()

if __name__ == '__main__':
                        main()
