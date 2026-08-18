"""YELMON Dev X - Local Launcher

© 2026 Yems junior lendola — All Rights Reserved.
Proprietary — do not distribute.

Fusion de : YELMON_Launcher.py, installer.py, auto_deploy.py,
build.bat, build.sh, launch.bat — en une interface web unifiée.

Permet : setup local complet, lancement, logs en temps réel,
raccourcis bureau, mise à jour depuis GitHub.
"""

import os
import sys
import platform
import subprocess
import shutil
import json
import threading
import time
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
VENV_DIR = ROOT_DIR / "venv"
DESKTOP_DIR = Path.home() / "Desktop"
LOCAL_APP_DATA = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "YELMON_Dev_X"

# Global log buffer for real-time streaming
_log_buffer = []
_log_lock = threading.Lock()
MAX_LOG_LINES = 200


def _log(msg: str):
    """Append to log buffer."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with _log_lock:
        _log_buffer.append(line)
        if len(_log_buffer) > MAX_LOG_LINES:
            _log_buffer.pop(0)
    logger.info(msg)


# ---------------------------------------------------------------------------
# Status — from YELMON_Launcher.py check_installation
# ---------------------------------------------------------------------------

def get_status() -> dict:
    """Statut complet du launcher local."""
    venv_exists = VENV_DIR.exists()
    pip_path = VENV_DIR / "Scripts" / "pip.exe" if platform.system() == "Windows" else VENV_DIR / "bin" / "pip3"
    pip_exists = pip_path.exists() if venv_exists else False

    build_dir = FRONTEND_DIR / "build"
    build_exists = build_dir.exists()
    index_html = (build_dir / "index.html").exists() if build_dir else False

    req_file = ROOT_DIR / "requirements.txt"
    req_exists = req_file.exists()

    # Check if backend is running
    backend_running = False
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            backend_running = s.connect_ex(("127.0.0.1", 5001)) == 0
    except Exception:
        pass

    return {
        "venv_exists": venv_exists,
        "pip_exists": pip_exists,
        "build_exists": build_exists,
        "index_html_exists": index_html,
        "requirements_exists": req_exists,
        "backend_running": backend_running,
        "python_executable": sys.executable,
        "venv_python": str(VENV_DIR / "Scripts" / "python.exe" if platform.system() == "Windows" else VENV_DIR / "bin" / "python3"),
        "platform": platform.system(),
        "install_dir": str(ROOT_DIR),
        "timestamp": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Setup — from installer.py + yelmon.py YELMONInstaller
# ---------------------------------------------------------------------------

def setup_venv() -> dict:
    """Crée l'environnement virtuel (depuis installer.py)."""
    _log("Création de l'environnement virtuel...")
    if VENV_DIR.exists():
        _log("Environnement virtuel déjà existant")
        return {"ok": True, "msg": "venv déjà existant"}

    try:
        import venv
        venv.create(VENV_DIR, with_pip=True)
        _log("Environnement virtuel créé avec succès")
        return {"ok": True, "msg": "venv créé"}
    except Exception as e:
        _log(f"Erreur création venv: {e}")
        return {"ok": False, "error": str(e)}


def setup_requirements() -> dict:
    """Installe les dépendances Python (depuis build.py PythonInstaller)."""
    _log("Installation des dépendances Python...")
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        # Create default requirements
        req_file.write_text("""flask>=3.0.0
flask-cors>=4.0.0
flask-socketio>=5.3.0
python-socketio>=5.9.0
pyjwt>=2.8.0
psutil>=5.9.0
gunicorn>=21.2.0
eventlet>=0.35.0
werkzeug>=3.0.0
""")
        _log("requirements.txt créé")

    pip_path = VENV_DIR / "Scripts" / "pip.exe" if platform.system() == "Windows" else VENV_DIR / "bin" / "pip3"
    if not pip_path.exists():
        return {"ok": False, "error": "pip non trouvé dans le venv"}

    try:
        r = subprocess.run(
            [str(pip_path), "install", "-r", str(req_file)],
            capture_output=True, text=True, timeout=300,
        )
        if r.returncode == 0:
            _log("Dépendances Python installées")
            return {"ok": True, "msg": "Dépendances installées"}
        else:
            _log(f"Erreur installation: {r.stderr[-200:]}")
            return {"ok": False, "error": r.stderr[-300:]}
    except Exception as e:
        _log(f"Erreur: {e}")
        return {"ok": False, "error": str(e)}


def setup_frontend() -> dict:
    """Build le frontend React (depuis build.py FrontendBuilder)."""
    _log("Build du frontend React...")
    if not FRONTEND_DIR.exists():
        return {"ok": False, "error": "Dossier frontend introuvable"}

    try:
        r = subprocess.run(
            ["npm", "install"],
            cwd=str(FRONTEND_DIR), capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            return {"ok": False, "error": f"npm install: {r.stderr[:200]}"}

        r2 = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(FRONTEND_DIR), capture_output=True, text=True, timeout=120,
        )
        if r2.returncode == 0:
            _log("Frontend buildé avec succès")
            return {"ok": True, "msg": "Frontend buildé"}
        else:
            return {"ok": False, "error": f"npm build: {r2.stderr[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def setup_shortcut() -> dict:
    """Crée un raccourci sur le bureau (depuis installer.py create_shortcuts)."""
    _log("Création du raccourci bureau...")
    try:
        if platform.system() == "Windows":
            shortcut_path = DESKTOP_DIR / "YELMON Dev X.bat"
            bat_content = f"""@echo off
echo  YELMON Dev X v1.0.0
echo Demarrage de l'application...
cd /d "{ROOT_DIR}"
"{sys.executable}" backend/app.py
pause
"""
            shortcut_path.write_text(bat_content)
            _log(f"Raccourci créé: {shortcut_path}")
            return {"ok": True, "msg": f"Raccourci créé: {shortcut_path}"}
        else:
            shortcut_path = DESKTOP_DIR / "yelmon-dev-x.sh"
            shortcut_path.write_text(f"""#!/bin/bash
echo "YELMON Dev X v1.0.0"
cd "{ROOT_DIR}"
python3 backend/app.py
""")
            os.chmod(shortcut_path, 0o755)
            _log(f"Raccourci créé: {shortcut_path}")
            return {"ok": True, "msg": f"Raccourci créé: {shortcut_path}"}
    except Exception as e:
        _log(f"Erreur raccourci: {e}")
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Launch — from YELMON_Launcher.py + yelmon.py YELMONLauncher
# ---------------------------------------------------------------------------

_backend_proc = None


def launch_backend() -> dict:
    """Lance le backend Flask en arrière-plan (depuis YELMON_Launcher.py)."""
    global _backend_proc
    _log("Démarrage du backend YELMON...")

    if _backend_proc and _backend_proc.poll() is None:
        return {"ok": True, "msg": "Backend déjà en cours d'exécution"}

    backend_script = BACKEND_DIR / "app.py"
    if not backend_script.exists():
        return {"ok": False, "error": "app.py non trouvé"}

    python_exe = sys.executable
    venv_python = VENV_DIR / "Scripts" / "python.exe" if platform.system() == "Windows" else VENV_DIR / "bin" / "python3"
    if venv_python.exists():
        python_exe = str(venv_python)

    try:
        env = os.environ.copy()
        env["YELMON_PORT"] = "5001"
        _backend_proc = subprocess.Popen(
            [python_exe, str(backend_script)],
            cwd=str(BACKEND_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Stream logs in background
        def _stream():
            for line in _backend_proc.stdout:
                _log(line.strip())
        threading.Thread(target=_stream, daemon=True).start()

        time.sleep(2)
        if _backend_proc.poll() is not None:
            return {"ok": False, "error": "Backend crash au démarrage"}

        _log("Backend démarré sur le port 5001")
        return {"ok": True, "msg": "Backend démarré", "pid": _backend_proc.pid}
    except Exception as e:
        _log(f"Erreur démarrage: {e}")
        return {"ok": False, "error": str(e)}


def stop_backend() -> dict:
    """Arrête le backend."""
    global _backend_proc
    if _backend_proc and _backend_proc.poll() is None:
        _backend_proc.terminate()
        try:
            _backend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _backend_proc.kill()
        _log("Backend arrêté")
        return {"ok": True, "msg": "Backend arrêté"}
    _log("Aucun backend en cours")
    return {"ok": True, "msg": "Aucun backend en cours"}


# ---------------------------------------------------------------------------
# Logs — from YELMON_Launcher.py log display
# ---------------------------------------------------------------------------

def get_logs(lines: int = 100) -> list:
    """Retourne les dernières lignes de log."""
    with _log_lock:
        return _log_buffer[-lines:]


def clear_logs():
    """Vide le buffer de logs."""
    with _log_lock:
        _log_buffer.clear()


# ---------------------------------------------------------------------------
# Full setup — one click from all scripts
# ---------------------------------------------------------------------------

def full_setup() -> dict:
    """Setup complet en un clic : venv + deps + frontend + shortcut."""
    _log("=== SETUP COMPLET YELMON DEV X ===")
    results = []

    r1 = setup_venv()
    results.append(("venv", r1))

    r2 = setup_requirements()
    results.append(("deps", r2))

    r3 = setup_frontend()
    results.append(("frontend", r3))

    r4 = setup_shortcut()
    results.append(("shortcut", r4))

    all_ok = all(r.get("ok") for _, r in results)
    _log(f"Setup {'terminé avec succès' if all_ok else 'terminé avec erreurs'}")
    return {"ok": all_ok, "results": {k: v for k, v in results}}
