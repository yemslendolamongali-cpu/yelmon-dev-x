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
from agent import YelmonAgent
from tokenizer import count_tokens

app = Flask(__name__, static_folder=str(BUILD_DIR), static_url_path="")
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


# ---------------------------------------------------------------------------
# Routes d'information
# ---------------------------------------------------------------------------

@app.route("/api/app/info")
def app_info():
    try:
        torch_status = "torch" if HAS_TORCH else "offline"
        mem = psutil.virtual_memory()
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
    language = str(data.get("language", "python")).strip().lower()

    if not prompt:
        return jsonify({"error": "Aucune description fournie"}), 400

    start = time.time()
    code = generator.generate(prompt, language)
    output = f" Code {language} généré en {time.time() - start:.2f}s"

    add_history({
        "language": language,
        "prompt": prompt,
        "code": code,
        "output": output,
        "success": True,
    })
    return jsonify({"code": code, "output": output, "language": language})


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
        "error": f"Exécution sandbox non disponible pour '{language}' (utilisez Python)",
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


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"error": "Message vide"}), 400
    reply = agent.reply(message)
    return jsonify({"reply": reply})


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

    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "timestamp": int(time.time() * 1000),
        "read": False,
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


@app.route("/api/contact/<contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    messages = _read_json(CONTACT_FILE, [])
    messages = [m for m in messages if m.get("id") != contact_id] if isinstance(messages, list) else []
    _write_json(CONTACT_FILE, messages)
    return jsonify({"ok": True})


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
# SocketIO
# ---------------------------------------------------------------------------

@socketio.on("connect")
def on_connect():
    emit("connected", {"status": "ok", "app": "YELMON Dev X"})


@socketio.on("generate")
def on_generate(data):
    prompt = str(data.get("prompt", "")).strip()
    language = str(data.get("language", "python")).strip().lower()
    if not prompt:
        emit("generate_result", {"error": "Aucune description"})
        return
    code = generator.generate(prompt, language)
    emit("generate_result", {"code": code, "language": language})


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


def main():
    host = os.environ.get("YELMON_HOST", "0.0.0.0")
    port = int(os.environ.get("YELMON_PORT", "5001"))
    debug = os.environ.get("YELMON_DEBUG", "0") == "1"

    print(f"[YELMON Dev X] Backend démarré sur http://{host}:{port}")
    print(f"[YELMON Dev X] Torch: {'disponible' if HAS_TORCH else 'offline (templates)'}")
    print(f"[YELMON Dev X] RAG: {'scikit-learn' if HAS_SKLEARN else 'brouillon (base)'}")
    print(f"[YELMON Dev X] Données: {DATA_DIR}")

    socketio.run(app, host=host, port=port, debug=debug,
                 use_reloader=debug, log_output=True,
                 allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
