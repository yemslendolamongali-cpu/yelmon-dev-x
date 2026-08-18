// © 2026 Yems junior lendola — All Rights Reserved.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './BackendDev.css';

const API_ENDPOINTS = [
    { method: 'POST', path: '/api/generate', desc: 'Générer du code', body: '{"prompt":"fibonacci","language":"auto"}' },
    { method: 'POST', path: '/api/execute', desc: 'Exécuter du code Python', body: '{"code":"print(42)","language":"python"}' },
    { method: 'POST', path: '/api/analyze', desc: 'Analyser du code', body: '{"code":"def add(a,b): return a+b"}' },
    { method: 'POST', path: '/api/chat', desc: 'Discuter avec l\'agent', body: '{"message":"Explique ce code"}' },
    { method: 'POST', path: '/api/search', desc: 'Recherche sémantique', body: '{"query":"api flask","top_k":5}' },
    { method: 'POST', path: '/api/tokens', desc: 'Compter les tokens', body: '{"text":"Hello World"}' },
    { method: 'GET', path: '/api/history', desc: 'Historique de génération', body: '' },
    { method: 'DELETE', path: '/api/history/:id', desc: 'Supprimer un historique', body: '' },
    { method: 'GET', path: '/api/snippets', desc: 'Lister les snippets', body: '' },
    { method: 'POST', path: '/api/snippets', desc: 'Sauvegarder un snippet', body: '{"title":"Mon snippet","code":"print(1)","language":"python"}' },
    { method: 'DELETE', path: '/api/snippets/:id', desc: 'Supprimer un snippet', body: '' },
    { method: 'POST', path: '/api/contact', desc: 'Envoyer un message', body: '{"name":"Chris","email":"c@x.com","subject":"bug","message":"..." }' },
    { method: 'GET', path: '/api/stats', desc: 'Statistiques globales', body: '' },
    { method: 'GET', path: '/api/app/info', desc: 'Info application', body: '' },
    { method: 'POST', path: '/api/auth/login', desc: 'Connexion', body: '{"username":"yems","password":"Kanikayo00"}' },
    { method: 'POST', path: '/api/auth/signup', desc: 'Inscription', body: '{"username":"new","email":"n@x.com","password":"pass123"}' },
];

const BACKEND_SNIPPETS = [
    {
        title: 'Middleware Auth JWT',
        lang: 'python',
        code: `from functools import wraps
from flask import request, jsonify
import jwt

SECRET = "yelmon-secret"

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else auth
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalide"}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.route("/api/protected")
@require_auth
def protected():
    return jsonify({"user": request.user["username"]})`
    },
    {
        title: 'CRUD Factory',
        lang: 'python',
        code: `def crud_routes(app, model, name):
    """Génère automatiquement les routes CRUD pour un modèle."""
    items = []
    next_id = 1

    @app.route(f"/api/{name}", methods=["GET"])
    def list_items():
        return jsonify({"items": items, "total": len(items)})

    @app.route(f"/api/{name}", methods=["POST"])
    def create_item():
        global next_id
        data = request.get_json()
        item = {"id": next_id, **data}
        next_id += 1
        items.append(item)
        return jsonify(item), 201

    @app.route(f"/api/{name}/<int:item_id>", methods=["PUT"])
    def update_item(item_id):
        item = next((i for i in items if i["id"] == item_id), None)
        if not item:
            return jsonify({"error": "Not found"}), 404
        item.update(request.get_json())
        return jsonify(item)

    @app.route(f"/api/{name}/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        global items
        items = [i for i in items if i["id"] != item_id]
        return jsonify({"ok": True})`
    },
    {
        title: 'Error Handler',
        lang: 'python',
        code: `from flask import jsonify

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Requête invalide", "code": 400}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Non autorisé", "code": 401}), 401

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ressource introuvable", "code": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erreur interne", "code": 500}), 500

@app.errorhandler(429)
def rate_limited(e):
    return jsonify({"error": "Trop de requêtes", "code": 429}), 429`
    },
    {
        title: 'Rate Limiter',
        lang: 'python',
        code: `import time
from functools import wraps
from flask import request, jsonify

_rate_limits = {}

def rate_limit(max_requests=60, window=60):
    """Limite le nombre de requêtes par IP."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            key = f"{ip}:{fn.__name__}"
            if key not in _rate_limits:
                _rate_limits[key] = []
            _rate_limits[key] = [t for t in _rate_limits[key] if now - t < window]
            if len(_rate_limits[key]) >= max_requests:
                return jsonify({"error": "Rate limit dépassé"}), 429
            _rate_limits[key].append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/api/data")
@rate_limit(max_requests=30, window=60)
def get_data():
    return jsonify({"data": [1, 2, 3]})`
    },
    {
        title: 'WebSocket Handler',
        lang: 'python',
        code: `from flask_socketio import emit, join_room, leave_room

@socketio.on("connect")
def on_connect():
    emit("connected", {"status": "ok"})

@socketio.on("join")
def on_join(data):
    room = data.get("room", "general")
    join_room(room)
    emit("joined", {"room": room})

@socketio.on("message")
def on_message(data):
    room = data.get("room", "general")
    msg = data.get("message", "")
    emit("new_message", {
        "from": data.get("user", "anonymous"),
        "message": msg,
    }, to=room)

@socketio.on("leave")
def on_leave(data):
    room = data.get("room", "general")
    leave_room(room)
    emit("left", {"room": room})`
    },
    {
        title: 'SQLite Database',
        lang: 'python',
        code: `import sqlite3
from pathlib import Path

DB_PATH = Path("yelmon.db")

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            language TEXT DEFAULT 'python',
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()

@app.route("/api/db/users")
def list_users():
    conn = get_db()
    users = conn.execute("SELECT id, username, email FROM users").fetchall()
    conn.close()
    return jsonify({"users": [dict(u) for u in users]})`
    },
];

const ARCH_LAYERS = [
    { icon: '🌐', name: 'Frontend React', desc: 'Interface utilisateur responsive avec CodeMirror, thèmes, PWA', tech: ['React', 'Vite', 'CodeMirror', 'Socket.IO Client'] },
    { icon: '🔄', name: 'API REST + WebSocket', desc: 'Endpoints RESTful et communication temps réel via SocketIO', tech: ['Flask', 'Flask-SocketIO', 'Flask-CORS'] },
    { icon: '🧠', name: 'Moteur de Génération', desc: 'Détection d\'intention, routing intelligent, templates par langage', tech: ['Python', 'Regex', 'Templates', 'Intent Detection'] },
    { icon: '🔍', name: 'RAG Engine', desc: 'Recherche sémantique de code avec TF-IDF et cosine similarity', tech: ['scikit-learn', 'TF-IDF', 'Cosine Similarity'] },
    { icon: '🤖', name: 'Agent IA', desc: 'Analyse de code, auto-correction, refactoring intelligent', tech: ['Agent', 'Tokenizer', 'Analysis'] },
    { icon: '🔐', name: 'Auth & Sécurité', desc: 'JWT tokens, PBKDF2 hashing, rate limiting, CORS', tech: ['JWT', 'PBKDF2', 'HMAC', 'CORS'] },
    { icon: '💾', name: 'Stockage Données', desc: 'Persistance JSON, historique, snippets, stats, contacts', tech: ['JSON', 'SQLite', 'File System'] },
    { icon: '🚀', name: 'Déploiement', desc: 'Docker, Render, Railway — déploiement cloud scalable', tech: ['Docker', 'Render', 'Gunicorn', 'Eventlet'] },
];

function BackendDev() {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('arch');
    const [stats, setStats] = useState(null);
    const [testEndpoint, setTestEndpoint] = useState(null);
    const [testBody, setTestBody] = useState('');
    const [testResult, setTestResult] = useState(null);
    const [testLoading, setTestLoading] = useState(false);
    const [copiedIdx, setCopiedIdx] = useState(null);

    useEffect(() => {
        fetch('/api/stats').then(r => r.json()).then(setStats).catch(() => {});
    }, []);

    const runTest = async () => {
        if (!testEndpoint) return;
        setTestLoading(true);
        setTestResult(null);
        try {
            const opts = { method: testEndpoint.method, headers: { 'Content-Type': 'application/json' } };
            if (testBody.trim() && testEndpoint.method !== 'GET' && testEndpoint.method !== 'DELETE') {
                opts.body = testBody;
            }
            const token = localStorage.getItem('yelmon_token');
            if (token) opts.headers['Authorization'] = `Bearer ${token}`;
            const res = await fetch(testEndpoint.path, opts);
            const text = await res.text();
            let data;
            try { data = JSON.parse(text); } catch { data = text; }
            setTestResult({ status: res.status, ok: res.ok, data });
        } catch (err) {
            setTestResult({ status: 0, ok: false, data: err.message });
        } finally {
            setTestLoading(false);
        }
    };

    const copyCode = (code, idx) => {
        navigator.clipboard.writeText(code);
        setCopiedIdx(idx);
        setTimeout(() => setCopiedIdx(null), 2000);
    };

    const methodColor = (m) => {
        if (m === 'GET') return '#22c55e';
        if (m === 'POST') return '#3b82f6';
        if (m === 'DELETE') return '#ef4444';
        if (m === 'PUT') return '#f59e0b';
        return '#888';
    };

    return (
        <div className="backend-page">
            <div className="backend-container">
                <button onClick={() => navigate('/')} className="backend-back">
                    ← Retour au tableau de bord
                </button>

                <div className="backend-header">
                    <div className="backend-header-icon">🖥</div>
                    <h1>Backend Développé</h1>
                    <p className="backend-subtitle">
                        Architecture, documentation API et outils backend du système YELMON Dev X.
                    </p>
                </div>

                {/* TAB BAR */}
                <div className="backend-tabs">
                    <button className={`backend-tab ${activeTab === 'arch' ? 'active' : ''}`} onClick={() => setActiveTab('arch')}>
                        🏗 Architecture
                    </button>
                    <button className={`backend-tab ${activeTab === 'api' ? 'active' : ''}`} onClick={() => setActiveTab('api')}>
                        📡 API Docs
                    </button>
                    <button className={`backend-tab ${activeTab === 'tools' ? 'active' : ''}`} onClick={() => setActiveTab('tools')}>
                        🧰 Outils
                    </button>
                </div>

                {/* TAB: ARCHITECTURE */}
                {activeTab === 'arch' && (
                    <div className="backend-content">
                        {/* Stats */}
                        {stats && (
                            <div className="backend-stats-row">
                                <div className="backend-stat">
                                    <div className="stat-val">{stats.total_users || 0}</div>
                                    <div className="stat-lbl">Utilisateurs</div>
                                </div>
                                <div className="backend-stat">
                                    <div className="stat-val">{stats.total_history || 0}</div>
                                    <div className="stat-lbl">Générations</div>
                                </div>
                                <div className="backend-stat">
                                    <div className="stat-val">{stats.total_snippets || 0}</div>
                                    <div className="stat-lbl">Snippets</div>
                                </div>
                                <div className="backend-stat">
                                    <div className="stat-val">{stats.languages || 0}</div>
                                    <div className="stat-lbl">Langages</div>
                                </div>
                            </div>
                        )}

                        {/* Architecture Layers */}
                        <div className="backend-section">
                            <h2>Couches de l'architecture</h2>
                            <div className="arch-grid">
                                {ARCH_LAYERS.map((layer, i) => (
                                    <div key={i} className="arch-card" style={{ animationDelay: `${i * 0.06}s` }}>
                                        <div className="arch-icon">{layer.icon}</div>
                                        <h3>{layer.name}</h3>
                                        <p>{layer.desc}</p>
                                        <div className="arch-techs">
                                            {layer.tech.map((t, j) => (
                                                <span key={j} className="arch-tech-badge">{t}</span>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Flow Diagram */}
                        <div className="backend-section">
                            <h2>Flux de données</h2>
                            <div className="arch-flow">
                                <div className="flow-step">
                                    <div className="flow-num">1</div>
                                    <div className="flow-label">Utilisateur</div>
                                    <div className="flow-desc">Envoie un prompt via le chat</div>
                                </div>
                                <div className="flow-arrow">→</div>
                                <div className="flow-step">
                                    <div className="flow-num">2</div>
                                    <div className="flow-label">API Flask</div>
                                    <div className="flow-desc">Route /api/generate valide et authentifie</div>
                                </div>
                                <div className="flow-arrow">→</div>
                                <div className="flow-step">
                                    <div className="flow-num">3</div>
                                    <div className="flow-label">Intent Detection</div>
                                    <div className="flow-desc">Analyse le prompt, détecte langage & framework</div>
                                </div>
                                <div className="flow-arrow">→</div>
                                <div className="flow-step">
                                    <div className="flow-num">4</div>
                                    <div className="flow-label">Code Generator</div>
                                    <div className="flow-desc">Sélectionne le template, génère le code</div>
                                </div>
                                <div className="flow-arrow">→</div>
                                <div className="flow-step">
                                    <div className="flow-num">5</div>
                                    <div className="flow-label">Réponse</div>
                                    <div className="flow-desc">Code + analysis retournés au frontend</div>
                                </div>
                            </div>
                        </div>

                        {/* Tech Stack */}
                        <div className="backend-section">
                            <h2>Stack technologique</h2>
                            <div className="tech-grid">
                                <div className="tech-card">
                                    <div className="tech-card-icon">🐍</div>
                                    <h4>Python 3.14</h4>
                                    <p>Langage principal du backend, gestion des calculs, templates et logique métier.</p>
                                </div>
                                <div className="tech-card">
                                    <div className="tech-card-icon">🌶</div>
                                    <h4>Flask</h4>
                                    <p>Framework web léger. Routes REST, middleware, Jinja2,.Blueprints.</p>
                                </div>
                                <div className="tech-card">
                                    <div className="tech-card-icon">⚡</div>
                                    <h4>SocketIO</h4>
                                    <p>Communication temps réel pour la génération live et les notifications.</p>
                                </div>
                                <div className="tech-card">
                                    <div className="tech-card-icon">🔐</div>
                                    <h4>JWT + PBKDF2</h4>
                                    <p>Authentification stateless avec tokens JWT et hashage sécurisé des mots de passe.</p>
                                </div>
                                <div className="tech-card">
                                    <div className="tech-card-icon">🔍</div>
                                    <h4>TF-IDF RAG</h4>
                                    <p>Recherche sémantique de code par vectorisation et cosine similarity.</p>
                                </div>
                                <div className="tech-card">
                                    <div className="tech-card-icon">🐳</div>
                                    <h4>Docker</h4>
                                    <p>Conteneurisation pour déploiement reproductible sur tout serveur.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* TAB: API DOCS */}
                {activeTab === 'api' && (
                    <div className="backend-content">
                        <div className="api-layout">
                            {/* Endpoint List */}
                            <div className="api-list-panel">
                                <h2>Endpoints ({API_ENDPOINTS.length})</h2>
                                <div className="api-endpoint-list">
                                    {API_ENDPOINTS.map((ep, i) => (
                                        <div
                                            key={i}
                                            className={`api-ep-item ${testEndpoint === ep ? 'active' : ''}`}
                                            onClick={() => { setTestEndpoint(ep); setTestBody(ep.body); setTestResult(null); }}
                                        >
                                            <span className="ep-method" style={{ background: methodColor(ep.method) }}>{ep.method}</span>
                                            <span className="ep-path">{ep.path}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Tester Panel */}
                            <div className="api-test-panel">
                                {testEndpoint ? (
                                    <>
                                        <div className="api-test-header">
                                            <span className="ep-method-lg" style={{ background: methodColor(testEndpoint.method) }}>{testEndpoint.method}</span>
                                            <span className="ep-path-lg">{testEndpoint.path}</span>
                                        </div>
                                        <p className="api-test-desc">{testEndpoint.desc}</p>

                                        {testEndpoint.method !== 'GET' && testEndpoint.method !== 'DELETE' && (
                                            <div className="api-test-field">
                                                <label>Body (JSON)</label>
                                                <textarea
                                                    value={testBody}
                                                    onChange={(e) => setTestBody(e.target.value)}
                                                    rows={8}
                                                    spellCheck={false}
                                                />
                                            </div>
                                        )}

                                        <button className="api-test-btn" onClick={runTest} disabled={testLoading}>
                                            {testLoading ? 'Envoi...' : '▶ Exécuter le test'}
                                        </button>

                                        {testResult && (
                                            <div className={`api-test-result ${testResult.ok ? 'success' : 'error'}`}>
                                                <div className="result-status">
                                                    <span className={`status-dot ${testResult.ok ? 'ok' : 'fail'}`}></span>
                                                    Status: {testResult.status} {testResult.ok ? 'OK' : 'Erreur'}
                                                </div>
                                                <pre>{typeof testResult.data === 'string' ? testResult.data : JSON.stringify(testResult.data, null, 2)}</pre>
                                            </div>
                                        )}
                                    </>
                                ) : (
                                    <div className="api-test-empty">
                                        <div className="empty-icon">📡</div>
                                        <p>Sélectionnez un endpoint dans la liste pour le tester.</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* TAB: TOOLS */}
                {activeTab === 'tools' && (
                    <div className="backend-content">
                        <div className="backend-section">
                            <h2>Snippets Backend Prêts à l'emploi</h2>
                            <p className="section-desc">Copiez ces patterns dans votre projet Flask pour un backend professionnel.</p>
                            <div className="snippets-grid">
                                {BACKEND_SNIPPETS.map((s, i) => (
                                    <div key={i} className="snippet-card">
                                        <div className="snippet-header">
                                            <h3>{s.title}</h3>
                                            <button className={`copy-btn ${copiedIdx === 's' + i ? 'copied' : ''}`} onClick={() => copyCode(s.code, 's' + i)}>
                                                {copiedIdx === 's' + i ? '✓ Copié' : '⎘ Copier'}
                                            </button>
                                        </div>
                                        <pre className="snippet-code"><code>{s.code}</code></pre>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="backend-section">
                            <h2>Boilerplate Flask Complet</h2>
                            <p className="section-desc">Un serveur Flask production-ready avec auth, CRUD, error handling et WebSocket.</p>
                            <div className="snippet-card full-width">
                                <div className="snippet-header">
                                    <h3>app.py — Serveur Complet</h3>
                                    <button className={`copy-btn ${copiedIdx === 'boilerplate' ? 'copied' : ''}`} onClick={() => copyCode(BOILERPLATE_CODE, 'boilerplate')}>
                                        {copiedIdx === 'boilerplate' ? '✓ Copié' : '⎘ Copier'}
                                    </button>
                                </div>
                                <pre className="snippet-code"><code>{BOILERPLATE_CODE}</code></pre>
                            </div>
                        </div>
                    </div>
                )}

                <div className="backend-footer">
                    <p>© 2026 Yems junior lendola — All Rights Reserved.</p>
                </div>
            </div>
        </div>
    );
}

const BOILERPLATE_CODE = `"""YELMON Backend Template — Flask + Auth + CRUD + WebSocket."""
import os, time, hashlib, hmac, base64, json, uuid
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

SECRET = os.environ.get("SECRET_KEY", "change-me-in-production")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- Auth ---
def hash_pw(pw):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), b"yelmon-salt", 100000).hex()

def create_token(user):
    hdr = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).decode()
    payload = {"user": user, "exp": int(time.time()) + 86400, "iat": int(time.time())}
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(SECRET.encode(), f"{hdr}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"{hdr}.{body}.{sig}"

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "")
        try:
            parts = token.split(".")
            sig = hmac.new(SECRET.encode(), f"{parts[0]}.{parts[1]}".encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, parts[2]):
                return jsonify({"error": "Token invalide"}), 401
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
            if payload.get("exp", 0) < time.time():
                return jsonify({"error": "Token expiré"}), 401
            request.user = payload
        except Exception:
            return jsonify({"error": "Non authentifié"}), 401
        return fn(*args, **kwargs)
    return wrapper

# --- Routes ---
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "ts": time.time()})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    # Validate user from DB here
    token = create_token(data.get("username", "user"))
    return jsonify({"token": token, "username": data.get("username")})

# --- WebSocket ---
@socketio.on("connect")
def on_connect():
    emit("connected", {"status": "ok"})

@socketio.on("message")
def on_message(data):
    emit("new_message", {"from": request.sid, "data": data}, broadcast=True)

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal error"}), 500

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))`;

export default BackendDev;
