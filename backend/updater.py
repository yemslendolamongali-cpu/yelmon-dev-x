"""YELMON Dev X - Moteur de mise à jour automatique

© 2026 Yems junior lendola — All Rights Reserved.
Proprietary — do not distribute.

Gère le build, le déploiement et les mises à jour automatiques
de l'application et du site web depuis le panneau admin.
"""

import os
import sys
import json
import shutil
import subprocess
import platform
import time
import threading
import zipfile
from pathlib import Path
from datetime import datetime, timezone
import logging
import urllib.request

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
BUILD_DIR = FRONTEND_DIR / "build"
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
DIST_DIR = ROOT_DIR / "dist"

APP_VERSION = "1.0.0"
GITHUB_REPO = "yemslendolamongali-cpu/yelmon-dev-x"

_update_log = []
_update_lock = threading.Lock()
_current_task = {"status": "idle", "step": "", "progress": 0, "started_at": None}


def _log(message, level="info"):
    entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
    }
    with _update_lock:
        _update_log.append(entry)
        if len(_update_log) > 200:
            _update_log.pop(0)
    getattr(logger, level, logger.info)(message)
    return entry


def get_update_status():
    with _update_lock:
        return {
            "current_task": dict(_current_task),
            "recent_logs": list(_update_log[-50:]),
            "app_version": APP_VERSION,
            "platform": platform.system().lower(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "node_available": shutil.which("node") is not None,
            "npm_available": shutil.which("npm") is not None,
            "build_dir_exists": BUILD_DIR.exists(),
            "build_index_exists": (BUILD_DIR / "index.html").exists(),
            "dist_dir_exists": DIST_DIR.exists(),
            "git_available": shutil.which("git") is not None,
        }


def _set_task(status, step="", progress=0):
    with _update_lock:
        _current_task["status"] = status
        _current_task["step"] = step
        _current_task["progress"] = progress
        if status == "running" and not _current_task["started_at"]:
            _current_task["started_at"] = datetime.now(timezone.utc).isoformat()
        if status in ("idle", "error", "completed"):
            if status != "running":
                pass


def _run_cmd(cmd, cwd=None, timeout=300):
    _log(f"  CMD: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n")[-20:]:
                _log(f"    {line}")
        if result.returncode != 0:
            _log(f"  STDERR: {result.stderr.strip()[-500:]}", "warning")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        _log(f"  Timeout après {timeout}s", "error")
        return False, "", "Timeout"
    except Exception as e:
        _log(f"  Erreur: {e}", "error")
        return False, "", str(e)


def build_frontend():
    _log("=== BUILD FRONTEND ===")
    _set_task("running", "Vérification de l'environnement Node...", 10)

    if not FRONTEND_DIR.exists():
        _log("Dossier frontend introuvable", "error")
        return False, "Dossier frontend introuvable"

    package_json = FRONTEND_DIR / "package.json"
    if not package_json.exists():
        _log("package.json introuvable", "error")
        return False, "package.json introuvable"

    _set_task("running", "Installation des dépendances Node...", 20)
    ok, out, err = _run_cmd(["npm", "install", "--prefer-offline", "--no-audit", "--no-fund"], cwd=FRONTEND_DIR, timeout=180)
    if not ok:
        _log(f"npm install échoué: {err[:200]}", "error")
        return False, f"npm install échoué: {err[:200]}"

    _set_task("running", "Build du frontend React...", 50)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    ok, out, err = _run_cmd(["npm", "run", "build"], cwd=FRONTEND_DIR, timeout=180)
    if not ok:
        _log(f"npm run build échoué: {err[:200]}", "error")
        return False, f"npm run build échoué: {err[:200]}"

    if not (BUILD_DIR / "index.html").exists():
        _log("Build frontend échoué — index.html manquant", "error")
        return False, "Build frontend échoué"

    _set_task("running", "Frontend build terminé", 100)
    _log("✓ Frontend build terminé avec succès")
    return True, "Frontend buildé avec succès"


def deploy_render():
    _log("=== DÉPLOIEMENT RENDER ===")
    _set_task("running", "Vérification du dépôt Git...", 10)

    if not (ROOT_DIR / ".git").exists():
        _log("Pas de dépôt Git trouvé", "error")
        return False, "Pas de dépôt Git"

    _set_task("running", "Git add + commit + push...", 30)

    ok, out, err = _run_cmd(["git", "add", "-A"], cwd=ROOT_DIR)
    if not ok:
        _log(f"git add échoué: {err}", "error")
        return False, f"git add échoué: {err}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"auto-update: mise à jour automatique depuis admin ({timestamp})"
    ok, out, err = _run_cmd(["git", "commit", "-m", commit_msg, "--allow-empty"], cwd=ROOT_DIR)
    if not ok and "nothing to commit" not in (err or ""):
        _log(f"git commit: {err[:200]}", "warning")

    _set_task("running", "Push vers GitHub...", 60)
    ok, out, err = _run_cmd(["git", "push", "origin", "main"], cwd=ROOT_DIR, timeout=120)
    if not ok:
        _log(f"git push échoué: {err[:200]}", "error")
        return False, f"git push échoué: {err[:200]}"

    _set_task("running", "Push terminé — Render va se redéployer automatiquement", 100)
    _log("✓ Push vers GitHub terminé — Render auto-deploy déclenché")
    return True, "Push effectué — Render se redéploye automatiquement"


def pull_updates():
    _log("=== PULL MISES À JOUR ===")
    _set_task("running", "Récupération des mises à jour...", 20)

    ok, out, err = _run_cmd(["git", "fetch", "origin"], cwd=ROOT_DIR, timeout=60)
    if not ok:
        return False, f"git fetch échoué: {err[:200]}"

    ok, out, err = _run_cmd(["git", "pull", "origin", "main"], cwd=ROOT_DIR, timeout=60)
    if not ok:
        return False, f"git pull échoué: {err[:200]}"

    _set_task("running", "Mise à jour terminée", 100)
    _log("✓ Mises à jour récupérées depuis GitHub")
    return True, "Dernières versions installées"


def full_update():
    _log("=== MISE À JOUR COMPLÈTE ===")
    _set_task("running", "Étape 1/4: Pull des mises à jour...", 10)

    ok, msg = pull_updates()
    if not ok:
        _set_task("error", f"Échec pull: {msg}", 0)
        return False, msg

    _set_task("running", "Étape 2/4: Build du frontend...", 30)
    ok, msg = build_frontend()
    if not ok:
        _set_task("error", f"Échec build: {msg}", 30)
        return False, msg

    _set_task("running", "Étape 3/4: Push vers GitHub...", 70)
    ok, msg = deploy_render()
    if not ok:
        _set_task("error", f"Échec push: {msg}", 70)
        return False, msg

    _set_task("running", "Étape 4/4: Terminé!", 100)
    _log("✓ Mise à jour complète terminée avec succès")
    _set_task("completed", "Mise à jour complète terminée", 100)
    return True, "Mise à jour complète effectuée — frontend buildé + pushé + Render redéployé"


def run_background(task_func, *args):
    def _wrapper():
        try:
            _set_task("running", "Démarrage...", 0)
            ok, msg = task_func(*args)
            if ok:
                _set_task("completed", msg, 100)
            else:
                _set_task("error", msg, 0)
        except Exception as e:
            _set_task("error", f"Erreur inattendue: {e}", 0)
            _log(f"Erreur: {e}", "error")

    t = threading.Thread(target=_wrapper, daemon=True)
    t.start()
    return True


def get_git_log(limit=20):
    ok, out, err = _run_cmd(
        ["git", "log", f"--oneline", f"-{limit}", "--format=%h|%s|%ai"],
        cwd=ROOT_DIR,
    )
    if not ok:
        return []
    commits = []
    for line in out.strip().split("\n"):
        parts = line.split("|", 2)
        if len(parts) >= 2:
            commits.append({
                "hash": parts[0],
                "message": parts[1],
                "date": parts[2] if len(parts) > 2 else "",
            })
    return commits


def get_disk_usage():
    info = {}
    for name, path in [("root", ROOT_DIR), ("frontend_build", BUILD_DIR), ("dist", DIST_DIR), ("data", DATA_DIR), ("logs", LOGS_DIR)]:
        if path.exists():
            total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            info[name] = {
                "size_bytes": total,
                "size_mb": round(total / (1024 * 1024), 2),
            }
        else:
            info[name] = {"size_bytes": 0, "size_mb": 0}
    return info


def create_backup():
    _log("=== CRÉATION DE SAUVEGARDE ===")
    _set_task("running", "Création de la sauvegarde...", 20)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"yelmon_backup_{timestamp}.zip"
    backup_path = DIST_DIR / "backups"
    backup_path.mkdir(parents=True, exist_ok=True)
    backup_file = backup_path / backup_name

    exclude = {"dist", "temp_build", "__pycache__", "venv", "node_modules", ".git", "build"}

    with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zf:
        count = 0
        for root, dirs, files in os.walk(ROOT_DIR):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                fp = Path(root) / f
                arcname = fp.relative_to(ROOT_DIR)
                zf.write(fp, arcname)
                count += 1

    size_mb = backup_file.stat().st_size / (1024 * 1024)
    _set_task("completed", f"Sauvegarde créée: {backup_name} ({size_mb:.1f} MB)", 100)
    _log(f"✓ Sauvegarde créée: {backup_file.name} ({size_mb:.1f} MB, {count} fichiers)")
    return True, {"file": str(backup_file), "name": backup_name, "size_mb": round(size_mb, 2), "files": count}


def list_backups():
    backup_path = DIST_DIR / "backups"
    if not backup_path.exists():
        return []
    backups = []
    for f in sorted(backup_path.glob("yelmon_backup_*.zip"), reverse=True):
        backups.append({
            "name": f.name,
            "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "date": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return backups
