"""YELMON Dev X - System Admin Module

© 2026 Yems junior lendola — All Rights Reserved.
Proprietary — do not distribute.

Fusion des scripts de reconstruction (yelmon.py, build.py, installer.py,
auto_deploy.py, YELMON_Launcher.py) avec le code du site web.
Fournit : health check, vérif. environnement, surveillance ports,
build local, backup/restore, install dependencies.
"""

import os
import sys
import platform
import subprocess
import shutil
import socket
import json
import zipfile
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DATA_DIR = ROOT_DIR / "data"
BACKUP_DIR = ROOT_DIR / "backups"
LOG_DIR = ROOT_DIR / "logs"

MONPROJET_DIR = Path(r"C:\Users\chris\OneDrive\Documents\Monprojet")
RECONSTRUCTION_DIR = MONPROJET_DIR / "reconstruction"


# ---------------------------------------------------------------------------
# Health check — from yelmon.py check_port_available + kill_process_on_port
# ---------------------------------------------------------------------------

def check_port(port: int) -> dict:
    """Vérifie si un port est ouvert."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            result = s.connect_ex(("127.0.0.1", port))
            return {"port": port, "open": result == 0, "status": "listening" if result == 0 else "closed"}
    except Exception as e:
        return {"port": port, "open": False, "status": "error", "error": str(e)}


def get_listening_ports() -> list:
    """Liste les ports en écoute."""
    common_ports = [5000, 5001, 3000, 3001, 8000, 8080, 8443, 443, 80, 22]
    return [check_port(p) for p in common_ports]


# ---------------------------------------------------------------------------
# Environment check — from yelmon.py check_requirements + build.py PythonInstaller
# ---------------------------------------------------------------------------

def get_environment() -> dict:
    """Vérifie l'environnement complet : Python, Node, npm, OS, disque, mémoire."""
    info = {
        "python": _check_python(),
        "node": _check_node(),
        "npm": _check_npm(),
        "os": _check_os(),
        "disk": _check_disk(),
        "memory": _check_memory(),
        "git": _check_git(),
        "timestamp": datetime.now().isoformat(),
    }
    return info


def _check_python() -> dict:
    v = sys.version_info
    pip_ok = False
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, timeout=10)
        pip_ok = True
    except Exception:
        pass
    return {
        "version": f"{v.major}.{v.minor}.{v.micro}",
        "executable": sys.executable,
        "pip": pip_ok,
        "ok": v.major >= 3 and v.minor >= 8,
    }


def _check_node() -> dict:
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10)
        return {"version": r.stdout.strip(), "ok": r.returncode == 0, "path": shutil.which("node") or "N/A"}
    except Exception:
        return {"version": "N/A", "ok": False, "path": "N/A"}


def _check_npm() -> dict:
    try:
        r = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=10)
        return {"version": r.stdout.strip(), "ok": r.returncode == 0, "path": shutil.which("npm") or "N/A"}
    except Exception:
        return {"version": "N/A", "ok": False, "path": "N/A"}


def _check_os() -> dict:
    import psutil
    mem = psutil.virtual_memory()
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor()[:60],
        "ram_total_gb": round(mem.total / (1024**3), 1),
        "ram_used_pct": mem.percent,
    }


def _check_disk() -> dict:
    usage = shutil.disk_usage("/")
    return {
        "total_gb": round(usage.total / (1024**3), 1),
        "used_gb": round(usage.used / (1024**3), 1),
        "free_gb": round(usage.free / (1024**3), 1),
        "used_pct": round(usage.used / usage.total * 100, 1),
    }


def _check_memory() -> dict:
    import psutil
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "ram_total_gb": round(mem.total / (1024**3), 1),
        "ram_available_gb": round(mem.available / (1024**3), 1),
        "ram_used_pct": mem.percent,
        "swap_total_gb": round(swap.total / (1024**3), 1),
        "swap_used_pct": swap.percent,
    }


def _check_git() -> dict:
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
        return {"version": r.stdout.strip(), "ok": r.returncode == 0}
    except Exception:
        return {"version": "N/A", "ok": False}


# ---------------------------------------------------------------------------
# Process monitor — from yelmon.py kill_process_on_port
# ---------------------------------------------------------------------------

def get_processes() -> list:
    """Liste les processus Python et Node actifs."""
    import psutil
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "create_time"]):
        try:
            name = p.info["name"].lower()
            if any(k in name for k in ("python", "node", "npm", "flask", "vite")):
                procs.append({
                    "pid": p.info["pid"],
                    "name": p.info["name"],
                    "cpu_pct": round(p.info["cpu_percent"] or 0, 1),
                    "mem_mb": round((p.memory_info().rss / 1024 / 1024) if p.memory_info() else 0, 1),
                    "uptime_sec": int(datetime.now().timestamp() - (p.info["create_time"] or 0)),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(procs, key=lambda x: -x["mem_mb"])


# ---------------------------------------------------------------------------
# Local build — merged from build.py YELMONBuilder + FrontendBuilder
# ---------------------------------------------------------------------------

def build_frontend_local() -> dict:
    """Build le frontend React en local (depuis build.py FrontendBuilder)."""
    if not FRONTEND_DIR.exists():
        return {"ok": False, "error": "Dossier frontend introuvable"}

    try:
        r = subprocess.run(
            ["npm", "install"],
            cwd=str(FRONTEND_DIR), capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            return {"ok": False, "error": f"npm install failed: {r.stderr[:300]}"}

        r2 = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(FRONTEND_DIR), capture_output=True, text=True, timeout=120,
        )
        if r2.returncode != 0:
            return {"ok": False, "error": f"npm build failed: {r2.stderr[:300]}"}

        build_dir = FRONTEND_DIR / "build"
        return {
            "ok": True,
            "build_exists": build_dir.exists(),
            "output": r2.stdout[-300:] if r2.stdout else "Build OK",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def install_deps_local() -> dict:
    """Installe les dépendances Python (depuis build.py PythonInstaller)."""
    req_file = ROOT_DIR / "requirements.txt"
    if not req_file.exists():
        return {"ok": False, "error": "requirements.txt introuvable"}

    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            capture_output=True, text=True, timeout=300,
        )
        return {"ok": r.returncode == 0, "output": r.stdout[-500:] if r.returncode == 0 else r.stderr[-500:]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Backup — merged from build.py InstallerCreator + updater.py
# ---------------------------------------------------------------------------

def create_full_backup() -> dict:
    """Crée un backup complet du projet (depuis build.py create_portable_zip)."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = BACKUP_DIR / f"yelmon_full_{ts}.zip"

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            exclude = {"dist", "build", "temp_build", "__pycache__", "venv", "node_modules", ".git", "backups"}
            for root, dirs, files in os.walk(ROOT_DIR):
                dirs[:] = [d for d in dirs if d not in exclude]
                for f in files:
                    if f.endswith((".pyc", ".pyo")):
                        continue
                    fp = Path(root) / f
                    arcname = fp.relative_to(ROOT_DIR)
                    zf.write(fp, arcname)
        size_mb = round(zip_path.stat().st_size / 1024 / 1024, 2)
        return {"ok": True, "path": str(zip_path), "size_mb": size_mb, "filename": zip_path.name}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def list_backups_local() -> list:
    """Liste les backups existants."""
    if not BACKUP_DIR.exists():
        return []
    backups = []
    for f in sorted(BACKUP_DIR.glob("yelmon_full_*.zip"), reverse=True):
        backups.append({
            "filename": f.name,
            "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
            "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
        })
    return backups


# ---------------------------------------------------------------------------
# Reconstruction scripts info — from Monprojet/reconstruction/
# ---------------------------------------------------------------------------

def get_reconstruction_scripts() -> list:
    """Liste les scripts de reconstruction disponibles."""
    if not RECONSTRUCTION_DIR.exists():
        return []
    scripts = []
    for f in sorted(RECONSTRUCTION_DIR.glob("*.py")):
        scripts.append({
            "name": f.name,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return scripts


# ---------------------------------------------------------------------------
# System summary
# ---------------------------------------------------------------------------

def get_system_summary() -> dict:
    """Résumé complet du système pour le dashboard admin."""
    env = get_environment()
    ports = get_listening_ports()
    procs = get_processes()
    backups = list_backups_local()
    scripts = get_reconstruction_scripts()

    open_ports = [p["port"] for p in ports if p["open"]]

    return {
        "environment": env,
        "ports": ports,
        "open_ports": open_ports,
        "processes": procs,
        "process_count": len(procs),
        "backups": backups,
        "backup_count": len(backups),
        "reconstruction_scripts": scripts,
        "app_version": "1.0.0",
        "root_dir": str(ROOT_DIR),
        "timestamp": datetime.now().isoformat(),
    }
