"""YELMON Dev X - Backend Flask

© 2026 Yems junior lendola — All Rights Reserved.
PROPRIETARY SOFTWARE — Unauthorized copying, distribution, reverse
engineering, or reproduction of this code is strictly prohibited.

Serveur API principal (port 5001).
- Génération de code (templates + PyTorch optionnel)
- Exécution sandbox
- RAG (recherche sémantique TF-IDF + cosine)
- Historique, snippets, stats, authentification JWT
- SocketIO temps réel
- Sert l'interface React (frontend/build)
"""

import os
import sys
import json
import time
import shutil
import uuid
import threading
import subprocess
import tempfile
import re
import ast
from pathlib import Path
from datetime import datetime, timedelta, timezone
from functools import wraps

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
FRONTEND_DIR = ROOT_DIR / "frontend"
BUILD_DIR = FRONTEND_DIR / "build"
ASSETS_DIR = ROOT_DIR / "assets"

for d in (DATA_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

HISTORY_FILE = DATA_DIR / "history.json"
SNIPPETS_FILE = DATA_DIR / "snippets.json"
USERS_FILE = DATA_DIR / "users.json"
STATS_FILE = DATA_DIR / "stats.json"
CONTACT_FILE = DATA_DIR / "contact.json"
USER_BACKUPS_FILE = DATA_DIR / "user_backups.json"
MAINPY_FILE = Path(r"C:\Users\chris\OneDrive\Documents\Monprojet\main.py")

JWT_SECRET = os.environ.get("YELMON_SECRET", "yelmon-dev-x-local-secret-key-2026-8e2f1c0a")
JWT_EXPIRES_HOURS = 24

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False

try:
    import jwt as pyjwt
    HAS_JWT = True
except Exception:
    HAS_JWT = False

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import psutil

from auth import hash_password, verify_password, create_token, decode_token
from rag import RAGEngine
from models import CodeGenerator
from models.intent import detect_intent
from agent import YelmonAgent
from tokenizer import count_tokens
from updater import (
    get_update_status, build_frontend, deploy_render, pull_updates,
    full_update, run_background, get_git_log, get_disk_usage,
    create_backup, list_backups,
)
from code_analyzer import analyze_code
from system_admin import (
    get_system_summary, get_environment, get_listening_ports,
    get_processes, build_frontend_local, install_deps_local,
    create_full_backup, list_backups_local, get_reconstruction_scripts,
)
from local_launcher import (
    get_status as get_launcher_status, setup_venv, setup_requirements,
    setup_frontend, setup_shortcut, launch_backend, stop_backend,
    get_logs, clear_logs, full_setup,
)
from cognitive import cognitive

app = Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = JWT_SECRET
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

CORS(app, resources={r"/api/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

generator = CodeGenerator()
rag = RAGEngine()
agent = YelmonAgent()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _write_json(path: Path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def get_history() -> list:
    data = _read_json(HISTORY_FILE, [])
    return data if isinstance(data, list) else []


def add_history(entry: dict):
    history = get_history()
    entry["id"] = str(uuid.uuid4())
    entry["timestamp"] = int(time.time() * 1000)
    history.insert(0, entry)
    _write_json(HISTORY_FILE, history[:50])


def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not HAS_JWT:
            return fn(*args, **kwargs)
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else auth
        payload = decode_token(token, JWT_SECRET)
        if payload is None:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        request.user = payload
        return fn(*args, **kwargs)
    return wrapper


def _backup_user_registration(username, email, phone, display_name):
    """Sauvegarde les informations de connexion d'un nouvel utilisateur."""
    backups = _read_json(USER_BACKUPS_FILE, [])
    backups.append({
        "username": username,
        "email": email or None,
        "phone": phone or None,
        "display_name": display_name or username,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    })
    _write_json(USER_BACKUPS_FILE, backups)


def _log_connection_to_mainpy(event_type, username, email=None, phone=None, display_name=None):
    """Enregistre chaque connexion/inscription directement dans main.py (Monprojet)."""
    try:
        MAINPY_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip = request.remote_addr if request else "N/A"
        line = (
            f'{{"time": "{timestamp}", "event": "{event_type}", '
            f'"username": "{username}", "email": "{email or ""}", '
            f'"phone": "{phone or ""}", "display_name": "{display_name or username}", '
            f'"ip": "{ip}"}}\n'
        )
        with open(MAINPY_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Routes d'information
# ---------------------------------------------------------------------------

@app.route("/api/app/info")
def app_info():
    try:
        torch_status = "torch" if HAS_TORCH else "offline"
        mem = psutil.virtual_memory()
        cog_stats = cognitive.get_stats()
        return jsonify({
            "name": "YELMON Dev X",
            "version": "1.0.0",
            "status": "ok",
            "backend": "Flask",
            "python": sys.version.split()[0],
            "model": torch_status,
            "cuda": torch.cuda.is_available() if HAS_TORCH else False,
            "memory": {"total": mem.total, "available": mem.available},
            "uptime": time.time() - app_start_time,
            "cognitive": {
                "active": True,
                "sessions": cog_stats["active_sessions"],
                "users": cog_stats["long_memory_users"],
                "feedback_count": cog_stats["learning"]["total_feedback"],
            },
        })
    except Exception as e:
        return jsonify({"name": "YELMON Dev X", "version": "1.0.0", "status": "error", "error": str(e)}), 500


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    email = str(data.get("email", "")).strip().lower()
    phone = str(data.get("phone", "")).strip()
    display_name = str(data.get("display_name", "")).strip()

    if not username or not password:
        return jsonify({"error": "username et password requis"}), 400
    if len(password) < 4:
        return jsonify({"error": "Mot de passe trop court (minimum 4 caractères)"}), 400
    # Bloquer toute tentative de création de compte admin
    if str(data.get("role", "")).strip().lower() == "admin":
        return jsonify({"error": "Création de compte admin non autorisée"}), 403

    users = _read_json(USERS_FILE, {})

    if username in users:
        return jsonify({"error": "Nom d'utilisateur déjà pris"}), 409
    if email and any(u.get("email") == email for u in users.values()):
        return jsonify({"error": "Adresse email déjà utilisée"}), 409
    if phone and any(u.get("phone") == phone for u in users.values()):
        return jsonify({"error": "Numéro de téléphone déjà utilisé"}), 409

    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "email": email or None,
        "phone": phone or None,
        "display_name": display_name or username,
        "role": "user",
    }
    _write_json(USERS_FILE, users)
    _backup_user_registration(username, email, phone, display_name)
    _log_connection_to_mainpy("inscription", username, email, phone, display_name)
    if HAS_JWT:
        token = create_token({"username": username}, JWT_SECRET, JWT_EXPIRES_HOURS)
        return jsonify({"token": token, "username": username})
    return jsonify({"ok": True, "username": username})


def _find_user_by_identifier(identifier: str):
    """Cherche un utilisateur par username, email ou téléphone."""
    users = _read_json(USERS_FILE, {})
    identifier = identifier.strip().lower()
    if identifier in users:
        return identifier, users[identifier]
    for uname, udata in users.items():
        if udata.get("email") and udata["email"].lower() == identifier:
            return uname, udata
        if udata.get("phone") and udata["phone"] == identifier:
            return uname, udata
    return None, None


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    identifier = str(data.get("username", "") or data.get("email", "") or data.get("phone", "")).strip()
    password = str(data.get("password", ""))

    if not identifier or not password:
        return jsonify({"error": "Identifiant et mot de passe requis"}), 400

    username, user = _find_user_by_identifier(identifier)
    if not user or not verify_password(user.get("password", ""), password):
        return jsonify({"error": "Identifiants invalides"}), 401

    _log_connection_to_mainpy("connexion", username, user.get("email"), user.get("phone"), user.get("display_name"))

    if HAS_JWT:
        token = create_token({"username": username}, JWT_SECRET, JWT_EXPIRES_HOURS)
        return jsonify({"token": token, "username": username})
    return jsonify({"ok": True, "username": username})


@app.route("/api/auth/me", methods=["GET"])
@require_token
def auth_me():
    user = getattr(request, "user", None)
    if not user:
        return jsonify({"error": "Non authentifié"}), 401
    username = user.get("username", "")
    users = _read_json(USERS_FILE, {})
    user_data = users.get(username, {})
    return jsonify({
        "username": username,
        "role": user_data.get("role", "user"),
        "display_name": user_data.get("display_name", username),
        "email": user_data.get("email", ""),
        "phone": user_data.get("phone", ""),
        "ok": True,
    })


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    return jsonify({"ok": True, "message": "Déconnecté"})


@app.route("/api/auth/delete", methods=["DELETE"])
@require_token
def auth_delete():
    user = getattr(request, "user", None)
    if not user:
        return jsonify({"error": "Non authentifié"}), 401
    username = user.get("username", "")
    users = _read_json(USERS_FILE, {})
    if username not in users:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    del users[username]
    _write_json(USERS_FILE, users)
    return jsonify({"ok": True, "message": f"Compte '{username}' supprimé"})


# ---------------------------------------------------------------------------
# Génération de code
# ---------------------------------------------------------------------------

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    language = str(data.get("language", "auto")).strip().lower()
    session_id = data.get("session_id")

    if not prompt:
        return jsonify({"error": "Aucune description fournie"}), 400

    username = "anonymous"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_token(auth_header.split(" ", 1)[1])
        if payload:
            username = payload.get("sub", "anonymous")

    cog_result = cognitive.process_message(username, prompt, session_id)
    resolved_language = language
    if language in ("auto", "automatic", "auto-detect", ""):
        if cog_result.get("language"):
            resolved_language = cog_result["language"]
        else:
            analysis = detect_intent(prompt)
            hints = analysis.get("language_hints", [])
            resolved_language = hints[0] if hints else "python"

    start = time.time()
    code = generator.generate(prompt, resolved_language)
    elapsed = time.time() - start
    output = f" Code {resolved_language} généré en {elapsed:.2f}s"

    cognitive.complete_interaction(
        username, cog_result.get("intent", "code_generation"),
        resolved_language, prompt, True
    )
    cognitive.record_response(cog_result["session_id"], code[:500])

    add_history({
        "language": resolved_language,
        "prompt": prompt,
        "code": code,
        "output": output,
        "success": True,
    })
    return jsonify({
        "code": code, "output": output, "language": resolved_language,
        "session_id": cog_result["session_id"],
        "cognitive": {
            "intent": cog_result["intent"],
            "complexity": cog_result["complexity"],
            "adaptations": cog_result["adaptations"],
        },
    })


@app.route("/api/history")
def history():
    return jsonify({"history": get_history()})


@app.route("/api/history/<history_id>", methods=["DELETE"])
def delete_history(history_id):
    history = [h for h in get_history() if h.get("id") != history_id]
    _write_json(HISTORY_FILE, history)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Exécution sandbox
# ---------------------------------------------------------------------------

def _run_python(code: str, timeout: int = 10):
    with tempfile.TemporaryDirectory(prefix="yelmon_run_") as tmp:
        script = Path(tmp) / "main.py"
        script.write_text(code, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=timeout,
                cwd=tmp,
            )
            return {
                "output": (proc.stdout or "").strip(),
                "error": (proc.stderr or "").strip(),
                "code": proc.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": f"Timeout dépassé ({timeout}s)", "code": -1}
        except Exception as e:
            return {"output": "", "error": str(e), "code": -1}


@app.route("/api/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    code = str(data.get("code", ""))
    language = str(data.get("language", "python")).strip().lower()

    if not code.strip():
        return jsonify({"error": "Code vide"}), 400

    if language == "python":
        result = _run_python(code)
        return jsonify({
            "output": result["output"] or ("(aucune sortie)" if not result["error"] else ""),
            "error": result["error"] or None,
            "exit_code": result["code"],
        })

    return jsonify({
        "output": "",
        "error": f"Exécution sandbox non disponible pour '{language}' (utilisez Python ou HTML dans le navigateur)",
    }), 400


# ---------------------------------------------------------------------------
# RAG - recherche sémantique
# ---------------------------------------------------------------------------

@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    top_k = int(data.get("top_k", 5))
    if not query:
        return jsonify({"error": "Aucune requête"}), 400
    results = rag.search(query, top_k=top_k)
    return jsonify({"results": results})


@app.route("/api/rag/index", methods=["POST"])
def rag_index():
    data = request.get_json(silent=True) or {}
    snippets = data.get("snippets", [])
    if snippets:
        rag.index(snippets)
    return jsonify({"indexed": len(rag.documents)})


# ---------------------------------------------------------------------------
# Snippets
# ---------------------------------------------------------------------------

@app.route("/api/snippets", methods=["GET"])
def list_snippets():
    snippets = _read_json(SNIPPETS_FILE, [])
    return jsonify({"snippets": snippets if isinstance(snippets, list) else []})


@app.route("/api/snippets", methods=["POST"])
def save_snippet():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    code = str(data.get("code", ""))
    language = str(data.get("language", "python")).strip().lower()
    if not code.strip():
        return jsonify({"error": "Code vide"}), 400

    snippets = _read_json(SNIPPETS_FILE, [])
    if not isinstance(snippets, list):
        snippets = []
    snippet = {
        "id": str(uuid.uuid4()),
        "title": title or f"Snippet {len(snippets) + 1}",
        "code": code,
        "language": language,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    snippets.insert(0, snippet)
    _write_json(SNIPPETS_FILE, snippets)
    rag.index([{"code": code, "language": language, "title": snippet["title"]}])
    return jsonify({"ok": True, "snippet": snippet})


@app.route("/api/snippets/<snippet_id>", methods=["DELETE"])
def delete_snippet(snippet_id):
    snippets = _read_json(SNIPPETS_FILE, [])
    snippets = [s for s in snippets if s.get("id") != snippet_id] if isinstance(snippets, list) else []
    _write_json(SNIPPETS_FILE, snippets)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Analyse / Agent
# ---------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    code = str(data.get("code", ""))
    if not code.strip():
        return jsonify({"error": "Code vide"}), 400
    analysis = agent.analyze(code)
    return jsonify(analysis)


@app.route("/api/code/check", methods=["POST"])
def code_check():
    """Analyse avancée : détecte les erreurs réelles, signale leur position,
    et corrige automatiquement le code."""
    data = request.get_json(silent=True) or {}
    code = str(data.get("code", ""))
    language = str(data.get("language", "auto")).strip().lower()
    fix = bool(data.get("fix", False))
    if not code.strip():
        return jsonify({"error": "Code vide"}), 400
    result = analyze_code(code, language, fix)
    return jsonify(result)


# ---------------------------------------------------------------------------
# System Admin — merged from reconstruction scripts
# ---------------------------------------------------------------------------

@app.route("/api/system/summary")
def system_summary():
    return jsonify(get_system_summary())


@app.route("/api/system/env")
def system_env():
    return jsonify(get_environment())


@app.route("/api/system/ports")
def system_ports():
    return jsonify(get_listening_ports())


@app.route("/api/system/processes")
def system_processes():
    return jsonify(get_processes())


@app.route("/api/system/scripts")
def system_scripts():
    return jsonify(get_reconstruction_scripts())


@app.route("/api/system/build-frontend", methods=["POST"])
def system_build_frontend():
    result = build_frontend_local()
    return jsonify(result)


@app.route("/api/system/install-deps", methods=["POST"])
def system_install_deps():
    result = install_deps_local()
    return jsonify(result)


@app.route("/api/system/backup", methods=["POST"])
def system_backup():
    result = create_full_backup()
    return jsonify(result)


@app.route("/api/system/backups")
def system_backups():
    return jsonify(list_backups_local())


# ---------------------------------------------------------------------------
# Local Launcher — merged from YELMON_Launcher.py, installer.py, auto_deploy.py
# ---------------------------------------------------------------------------

@app.route("/api/launcher/status")
def launcher_status():
    return jsonify(get_launcher_status())


@app.route("/api/launcher/setup/venv", methods=["POST"])
def launcher_setup_venv():
    return jsonify(setup_venv())


@app.route("/api/launcher/setup/deps", methods=["POST"])
def launcher_setup_deps():
    return jsonify(setup_requirements())


@app.route("/api/launcher/setup/frontend", methods=["POST"])
def launcher_setup_frontend():
    return jsonify(setup_frontend())


@app.route("/api/launcher/setup/shortcut", methods=["POST"])
def launcher_setup_shortcut():
    return jsonify(setup_shortcut())


@app.route("/api/launcher/setup/full", methods=["POST"])
def launcher_setup_full():
    return jsonify(full_setup())


@app.route("/api/launcher/start", methods=["POST"])
def launcher_start():
    return jsonify(launch_backend())


@app.route("/api/launcher/stop", methods=["POST"])
def launcher_stop():
    return jsonify(stop_backend())


@app.route("/api/launcher/logs")
def launcher_logs():
    lines = request.args.get("lines", 100, type=int)
    return jsonify(get_logs(lines))


@app.route("/api/launcher/logs/clear", methods=["POST"])
def launcher_logs_clear():
    clear_logs()
    return jsonify({"ok": True})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    session_id = data.get("session_id")
    if not message:
        return jsonify({"error": "Message vide"}), 400

    username = "anonymous"
    token = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)
        if payload:
            username = payload.get("sub", "anonymous")

    cog_result = cognitive.process_message(username, message, session_id)
    cognitive.record_response(cog_result["session_id"], "")
    reply = agent.reply_cognitive(message, cog_result)

    cognitive.record_response(cog_result["session_id"], reply)

    return jsonify({
        "reply": reply,
        "session_id": cog_result["session_id"],
        "cognitive": {
            "intent": cog_result["intent"],
            "language": cog_result["language"],
            "complexity": cog_result["complexity"],
            "context": cog_result["context_summary"],
            "reasoning_steps": len(cog_result["reasoning_chain"]["steps"]),
            "adaptations": cog_result["adaptations"],
            "turn_count": cog_result["turn_count"],
        },
    })


# ---------------------------------------------------------------------------
# Cognitive Architecture
# ---------------------------------------------------------------------------

@app.route("/api/cognitive/stats", methods=["GET"])
def cognitive_stats():
    return jsonify(cognitive.get_stats())


@app.route("/api/cognitive/profile", methods=["GET"])
def cognitive_profile():
    username = "anonymous"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_token(auth_header.split(" ", 1)[1])
        if payload:
            username = payload.get("sub", "anonymous")
    return jsonify(cognitive.get_user_cognitive_profile(username))


@app.route("/api/cognitive/feedback", methods=["POST"])
def cognitive_feedback():
    data = request.get_json(silent=True) or {}
    rating = int(data.get("rating", 3))
    message_text = data.get("message", "")
    response_text = data.get("response", "")
    intent = data.get("intent", "general")
    username = "anonymous"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_token(auth_header.split(" ", 1)[1])
        if payload:
            username = payload.get("sub", "anonymous")
    cognitive.submit_feedback(username, message_text, response_text, rating, intent)
    return jsonify({"ok": True, "message": "Feedback enregistré"})


@app.route("/api/cognitive/think", methods=["POST"])
def cognitive_think():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    session_id = data.get("session_id", "debug_session")
    return jsonify({"reflection": cognitive.think(session_id, message)})


@app.route("/api/cognitive/reason", methods=["POST"])
def cognitive_reason():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "Code vide"}), 400
    chain = cognitive.reasoner.reason_about_code(code, language)
    return jsonify(chain.to_dict())


@app.route("/api/cognitive/reset", methods=["POST"])
def cognitive_reset():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if session_id:
        cognitive.short_memory.clear(session_id)
        cognitive.context.clear(session_id)
    return jsonify({"ok": True, "message": "Session réinitialisée"})


# ---------------------------------------------------------------------------
# Hypothesis Engine
# ---------------------------------------------------------------------------

@app.route("/api/hypothesis/fix", methods=["POST"])
def hypothesis_fix():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    errors = data.get("errors", [])
    if not code:
        return jsonify({"error": "Code requis"}), 400
    if not errors:
        try:
            if language == "python":
                ast.parse(code)
            errors = []
        except SyntaxError as e:
            errors = [{"line": e.lineno, "msg": e.msg, "type": "syntax"}]
    result = cognitive.solve_fix(code, errors, language)
    return jsonify(result)


@app.route("/api/hypothesis/generate", methods=["POST"])
def hypothesis_generate():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    language = data.get("language", "python")
    if not prompt:
        return jsonify({"error": "Prompt requis"}), 400
    result = cognitive.solve_generation(prompt, language)
    return jsonify(result)


@app.route("/api/hypothesis/optimize", methods=["POST"])
def hypothesis_optimize():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "Code requis"}), 400
    result = cognitive.solve_optimization(code, language)
    return jsonify(result)


@app.route("/api/hypothesis/stats", methods=["GET"])
def hypothesis_stats():
    return jsonify(cognitive.get_hypothesis_stats())


@app.route("/api/hypothesis/history", methods=["GET"])
def hypothesis_history():
    return jsonify({"history": cognitive.hypothesis.get_history()})


# ---------------------------------------------------------------------------
# Counterfactual Engine
# ---------------------------------------------------------------------------

@app.route("/api/counterfactual/analyze", methods=["POST"])
def counterfactual_analyze():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "Code requis"}), 400
    result = cognitive.analyze_counterfactual_code(code, language)
    return jsonify(result)


@app.route("/api/counterfactual/decision", methods=["POST"])
def counterfactual_decision():
    data = request.get_json(silent=True) or {}
    decision = data.get("decision", "")
    context = data.get("context", "")
    language = data.get("language", "python")
    if not decision:
        return jsonify({"error": "Décision requise"}), 400
    result = cognitive.analyze_counterfactual_decision(decision, context, language)
    return jsonify(result)


@app.route("/api/counterfactual/paths", methods=["POST"])
def counterfactual_paths():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    decisions = data.get("decisions", [])
    language = data.get("language", "python")
    if not code:
        return jsonify({"error": "Code requis"}), 400
    result = cognitive.explore_counterfactual_paths(code, decisions, language)
    return jsonify(result)


@app.route("/api/counterfactual/stats", methods=["GET"])
def counterfactual_stats():
    return jsonify(cognitive.get_counterfactual_stats())


@app.route("/api/counterfactual/history", methods=["GET"])
def counterfactual_history():
    return jsonify({"history": cognitive.counterfactual.get_history()})


@app.route("/api/tokens", methods=["POST"])
def tokens():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", ""))
    return jsonify({"tokens": count_tokens(text)})


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not subject or not message:
        return jsonify({"error": "Tous les champs sont requis"}), 400

    username = "anonymous"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_token(auth_header.split(" ", 1)[1])
        if payload:
            username = payload.get("sub", "anonymous")

    entry = {
        "id": str(uuid.uuid4()),
        "username": username,
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "timestamp": int(time.time() * 1000),
        "read": False,
        "user_read": False,
        "reply": None,
        "replied_at": None,
    }

    messages = _read_json(CONTACT_FILE, [])
    if not isinstance(messages, list):
        messages = []
    messages.insert(0, entry)
    _write_json(CONTACT_FILE, messages[:100])

    return jsonify({"ok": True, "message": "Message envoyé avec succès"})


@app.route("/api/contact", methods=["GET"])
def list_contacts():
    messages = _read_json(CONTACT_FILE, [])
    return jsonify({"messages": messages if isinstance(messages, list) else []})


@app.route("/api/contact/my", methods=["GET"])
def list_my_contacts():
    username = "anonymous"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_token(auth_header.split(" ", 1)[1])
        if payload:
            username = payload.get("sub", "anonymous")
    messages = _read_json(CONTACT_FILE, [])
    if not isinstance(messages, list):
        messages = []
    my_messages = [m for m in messages if m.get("username") == username]
    return jsonify({"messages": my_messages})


@app.route("/api/contact/<contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    messages = _read_json(CONTACT_FILE, [])
    messages = [m for m in messages if m.get("id") != contact_id] if isinstance(messages, list) else []
    _write_json(CONTACT_FILE, messages)
    return jsonify({"ok": True})


@app.route("/api/contact/<contact_id>/reply", methods=["POST"])
def reply_contact(contact_id):
    data = request.get_json(silent=True) or {}
    reply_text = str(data.get("reply", "")).strip()
    if not reply_text:
        return jsonify({"error": "Réponse vide"}), 400
    messages = _read_json(CONTACT_FILE, [])
    if not isinstance(messages, list):
        return jsonify({"error": "Aucun message"}), 404
    for m in messages:
        if m.get("id") == contact_id:
            m["reply"] = reply_text
            m["replied_at"] = int(time.time() * 1000)
            m["read"] = True
            m["user_read"] = False
            _write_json(CONTACT_FILE, messages)
            return jsonify({"ok": True, "message": "Réponse envoyée"})
    return jsonify({"error": "Message non trouvé"}), 404


@app.route("/api/contact/<contact_id>/read", methods=["POST"])
def mark_read_contact(contact_id):
    messages = _read_json(CONTACT_FILE, [])
    if not isinstance(messages, list):
        return jsonify({"error": "Aucun message"}), 404
    for m in messages:
        if m.get("id") == contact_id:
            m["read"] = True
            _write_json(CONTACT_FILE, messages)
            return jsonify({"ok": True})
    return jsonify({"error": "Message non trouvé"}), 404


@app.route("/api/contact/<contact_id>/user-read", methods=["POST"])
def mark_user_read_contact(contact_id):
    messages = _read_json(CONTACT_FILE, [])
    if not isinstance(messages, list):
        return jsonify({"error": "Aucun message"}), 404
    for m in messages:
        if m.get("id") == contact_id:
            m["user_read"] = True
            _write_json(CONTACT_FILE, messages)
            return jsonify({"ok": True})
    return jsonify({"error": "Message non trouvé"}), 404


# ---------------------------------------------------------------------------
# Statistiques
# ---------------------------------------------------------------------------

@app.route("/api/stats")
def stats():
    history = get_history()
    snippets = _read_json(SNIPPETS_FILE, [])
    langs = {}
    for h in history:
        langs[h.get("language", "?")] = langs.get(h.get("language", "?"), 0) + 1
    return jsonify({
        "generations": len(history),
        "snippets": len(snippets) if isinstance(snippets, list) else 0,
        "languages": langs,
        "uptime": time.time() - app_start_time,
    })


# ---------------------------------------------------------------------------
# Admin — Mise à jour automatique & Gestion du déploiement
# ---------------------------------------------------------------------------

def _require_admin():
    """Vérifie que l'utilisateur est admin via le token JWT.
    Seuls les comptes avec role='admin' en base de données ont accès.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    data = decode_token(auth[7:], JWT_SECRET)
    if not data:
        return None
    username = data.get("username", "")
    users = _read_json(USERS_FILE, {})
    u = users.get(username, {})
    if u.get("role") != "admin":
        return None
    return username


@app.route("/api/admin/update/status")
def admin_update_status():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify(get_update_status())


@app.route("/api/admin/update/build", methods=["POST"])
def admin_update_build():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    ok = run_background(build_frontend)
    return jsonify({"ok": ok, "message": "Build frontend lancé en arrière-plan"})


@app.route("/api/admin/update/deploy", methods=["POST"])
def admin_update_deploy():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    ok = run_background(deploy_render)
    return jsonify({"ok": ok, "message": "Déploiement lancé en arrière-plan"})


@app.route("/api/admin/update/pull", methods=["POST"])
def admin_update_pull():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    ok = run_background(pull_updates)
    return jsonify({"ok": ok, "message": "Pull des mises à jour lancé"})


@app.route("/api/admin/update/full", methods=["POST"])
def admin_update_full():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    ok = run_background(full_update)
    return jsonify({"ok": ok, "message": "Mise à jour complète lancée (pull + build + deploy)"})


@app.route("/api/admin/update/backup", methods=["POST"])
def admin_update_backup():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    ok, result = create_backup()
    return jsonify({"ok": ok, **result})


@app.route("/api/admin/update/backups")
def admin_update_backups():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify({"backups": list_backups()})


@app.route("/api/admin/update/git-log")
def admin_update_git_log():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    limit = request.args.get("limit", 20, type=int)
    return jsonify({"commits": get_git_log(limit)})


@app.route("/api/admin/update/disk")
def admin_update_disk():
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify(get_disk_usage())


@app.route("/api/admin/users/backups")
def admin_user_backups():
    """Liste de toutes les sauvegardes d'inscriptions utilisateurs."""
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    backups = _read_json(USER_BACKUPS_FILE, [])
    users = _read_json(USERS_FILE, {})
    enriched = []
    for b in backups:
        u = users.get(b.get("username", ""), {})
        enriched.append({
            **b,
            "current_role": u.get("role", "deleted"),
            "account_exists": bool(u),
        })
    return jsonify({"backups": enriched, "total": len(enriched)})


@app.route("/api/admin/users/list")
def admin_user_list():
    """Liste de tous les utilisateurs (sans mots de passe)."""
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    users = _read_json(USERS_FILE, {})
    safe_users = []
    for uname, udata in users.items():
        safe_users.append({
            "username": uname,
            "email": udata.get("email"),
            "phone": udata.get("phone"),
            "display_name": udata.get("display_name", uname),
            "role": udata.get("role", "user"),
            "created_at": udata.get("created_at", ""),
        })
    return jsonify({"users": safe_users, "total": len(safe_users)})


@app.route("/api/admin/users/export")
def admin_user_export():
    """Export JSON de tous les backups d'inscription."""
    admin = _require_admin()
    if not admin:
        return jsonify({"error": "Accès refusé"}), 403
    backups = _read_json(USER_BACKUPS_FILE, [])
    return jsonify({
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "app_version": APP_VERSION if 'APP_VERSION' in dir() else "1.0.0",
        "total_registrations": len(backups),
        "registrations": backups,
    })


# ---------------------------------------------------------------------------
# SocketIO
# ---------------------------------------------------------------------------

@socketio.on("connect")
def on_connect():
    emit("connected", {"status": "ok", "app": "YELMON Dev X"})


@socketio.on("generate")
def on_generate(data):
    prompt = str(data.get("prompt", "")).strip()
    language = str(data.get("language", "auto")).strip().lower()
    if not prompt:
        emit("generate_result", {"error": "Aucune description"})
        return
    resolved_language = language
    if language in ("auto", "automatic", "auto-detect", ""):
        analysis = detect_intent(prompt)
        hints = analysis.get("language_hints", [])
        resolved_language = hints[0] if hints else "python"
    code = generator.generate(prompt, language)
    emit("generate_result", {"code": code, "language": resolved_language})


@socketio.on("stats")
def on_stats():
    emit("stats_result", stats().get_json())


# ---------------------------------------------------------------------------
# Frontend statique (build React)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if BUILD_DIR.exists() and (BUILD_DIR / "index.html").exists():
        return send_from_directory(str(BUILD_DIR), "index.html")
    return jsonify({"message": "YELMON Dev X - interface non compilée (frontend/build introuvable)"})


@app.route("/<path:filename>")
def static_files(filename):
    if BUILD_DIR.exists():
        target = BUILD_DIR / filename
        if target.is_file():
            return send_from_directory(str(BUILD_DIR), filename)
        index_file = BUILD_DIR / "index.html"
        if index_file.exists():
            return send_from_directory(str(BUILD_DIR), "index.html")
    return jsonify({"error": "Interface non disponible"}), 404


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

app_start_time = time.time()


def _ensure_admin_account():
    """Crée les comptes admin exclusifs. Seuls ces comptes auront le rôle admin."""
    try:
        admin_user = os.environ.get("YELMON_ADMIN_USER", "yems")
        admin_pass = os.environ.get("YELMON_ADMIN_PASS", "Kanikayo00")
        admin_name = os.environ.get("YELMON_ADMIN_NAME", "Yems junior lendola")
        admin_email = os.environ.get("YELMON_ADMIN_EMAIL", "yemsjuniorlendola@gmail.com")
        local_admin_user = "01yem's"
        local_admin_pass = "Kanikayo00"

        users = _read_json(USERS_FILE, {})

        # Compte admin principal (username: yems)
        if admin_user not in users:
            users[admin_user] = {
                "password": hash_password(admin_pass),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "email": admin_email,
                "phone": None,
                "display_name": admin_name,
                "role": "admin",
            }
        else:
            users[admin_user]["role"] = "admin"

        # Compte admin par email
        email_user = "__email_yemsjuniorlendola"
        if email_user not in users:
            users[email_user] = {
                "password": hash_password(admin_pass),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "email": admin_email,
                "phone": None,
                "display_name": admin_name,
                "role": "admin",
            }
        else:
            users[email_user]["role"] = "admin"

        # Compte admin local (01yem's)
        if local_admin_user not in users:
            users[local_admin_user] = {
                "password": hash_password(local_admin_pass),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "email": admin_email,
                "phone": None,
                "display_name": admin_name,
                "role": "admin",
            }
        else:
            users[local_admin_user]["role"] = "admin"

        # Forcer role='user' pour tout autre compte existant (sécurité)
        for uname, udata in users.items():
            if uname not in (admin_user, email_user, local_admin_user):
                if udata.get("role") == "admin":
                    udata["role"] = "user"

        _write_json(USERS_FILE, users)
        print(f"[YELMON Dev X] Comptes admin verrouillés: {admin_user} / {local_admin_user} / {admin_email}")
    except Exception as e:
        print(f"[YELMON Dev X] Erreur creation admin: {e}")


def main():
    host = os.environ.get("YELMON_HOST", "0.0.0.0")
    port = int(os.environ.get("YELMON_PORT", os.environ.get("PORT", "5001")))
    debug = os.environ.get("YELMON_DEBUG", "0") == "1"

    print(f"[YELMON Dev X] Backend démarré sur http://{host}:{port}")
    print(f"[YELMON Dev X] Torch: {'disponible' if HAS_TORCH else 'offline (templates)'}")
    print(f"[YELMON Dev X] RAG: {'scikit-learn' if HAS_SKLEARN else 'brouillon (base)'}")
    print(f"[YELMON Dev X] Données: {DATA_DIR}")

    _ensure_admin_account()

    socketio.run(app, host=host, port=port, debug=debug,
                 use_reloader=debug, log_output=True,
                 allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
