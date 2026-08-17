"""YELMON Dev X - Détection d'intention et analyse de prompts."""

import re


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


_INTENT_KEYWORDS = {
    "api": ["api", "rest", "endpoint", "route", "serveur", "server"],
    "webapp": ["webapp", "web app", "site web", "frontend", "page web", "dashboard"],
    "html_page": ["page html", "landing page", "portfolio", "site vitrine", "one page",
                   "page d'accueil", "accueil site", "page statique", "page web pure",
                   "html css", "page responsive", "formulaire contact"],
    "cli": ["cli", "command line", "terminal", "ligne de commande", "argparse"],
    "game": ["jeu", "game", "snake", "tetris", "pong", "pygame", "gameboy"],
    "bot": ["bot", "telegram", "discord", "slack", "chatbot"],
    "scraper": ["scrap", "crawl", "beautifulsoup", "selenium"],
    "desktop": ["desktop", "gui", "interface graphique", "tkinter", "qt", "pyqt"],
    "data": ["data", "csv", "json", "pandas", "numpy", "analyse de données", "dataset"],
    "ml": ["machine learning", "ml", "neural", "tensorflow", "pytorch", "sklearn",
           "réseau de neurones", "classification", "régression"],
    "auth": ["auth", "login", "jwt", "token", "password", "inscription"],
    "database": ["database", "base de données", "sql", "sqlite", "postgres", "mysql", "mongodb"],
    "websocket": ["websocket", "socket", "temps réel", "realtime"],
    "docker": ["docker", "container", "dockerfile", "compose"],
    "testing": ["test", "unittest", "pytest", "jest"],
    "fullstack": ["fullstack", "full stack", "projet complet", "application complète"],
    "classe": ["classe", "class", "objet", "oop", "héritage", "abstrait", "interface java",
               "constructeur", "attribut", "méthode"],
}

_FRAMEWORK_KEYWORDS = {
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "express": ["express", "node", "npm"],
    "react": ["react", "jsx", "tsx"],
    "pygame": ["pygame"],
    "tkinter": ["tkinter", "tk"],
    "discord": ["discord.py", "discord"],
    "telegram": ["telegram"],
    "pandas": ["pandas"],
    "selenium": ["selenium"],
    "sqlalchemy": ["sqlalchemy", "orm"],
    "spring": ["spring", "java"],
    "actix": ["actix"],
    "gin": ["gin", "go"],
}

_FEATURE_KEYWORDS = {
    "auth": ["auth", "login", "jwt", "token", "password", "session"],
    "database": ["database", "sql", "sqlite", "mongo", "redis", "bdd"],
    "crud": ["crud", "create", "read", "update", "delete", "ajouter", "supprimer", "modifier"],
    "upload": ["upload", "fichier", "file", "image", "photo"],
    "email": ["email", "mail", "smtp"],
    "search": ["search", "recherche", "filter", "filtrer"],
    "pagination": ["page", "pagination", "offset", "limit"],
    "cache": ["cache", "redis", "memoize"],
    "websocket": ["websocket", "socket.io", "realtime"],
    "docker": ["docker", "dockerfile", "compose"],
    "testing": ["test", "pytest", "unittest", "jest"],
    "async": ["async", "await", "asynchrone", "concurrent"],
    "logging": ["log", "logging", "logger"],
    "config": ["config", "configuration", "env", "environnement"],
    "error_handling": ["error", "erreur", "exception", "try", "except"],
}


def detect_intent(prompt: str) -> dict:
    """Analyse un prompt et retourne intent, framework, features, complexity."""
    p = _norm(prompt)

    # Intent
    intent_scores = {}
    for intent, keywords in _INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in p)
        if score:
            intent_scores[intent] = score
    intent = max(intent_scores, key=intent_scores.get) if intent_scores else "generic"

    # Framework
    framework = None
    for fw, keywords in _FRAMEWORK_KEYWORDS.items():
        if any(kw in p for kw in keywords):
            framework = fw
            break

    # Features
    features = []
    for feat, keywords in _FEATURE_KEYWORDS.items():
        if any(kw in p for kw in keywords):
            features.append(feat)

    # Complexity
    complexity = "simple"
    if len(p.split()) > 20 or len(features) > 3:
        complexity = "complex"
    elif len(p.split()) > 10 or len(features) > 1:
        complexity = "medium"

    # Language hints — order matters: more specific first
    language_hints = []
    lang_patterns = {
        "python": ["python", "py", "pip", "flask", "fastapi", "django", "pandas",
                   "tkinter", "pygame"],
        "javascript": ["javascript", "js", "node", "npm", "express", "react", "vue",
                       "angular", "svelte"],
        "java": ["java", "spring", "maven", "gradle", "classe java", "jakarta"],
        "go": ["golang", "gin framework", "go lang"],
        "rust": ["rust", "cargo", "actix", "tokio"],
        "cpp": ["c++", "cpp", "cmake", "std::"],
        "html": ["html", "css", "landing page", "portfolio", "page web pure",
                 "page html", "site vitrine", "formulaire", "responsive html",
                 "one page", "page statique", "page d'accueil"],
    }
    for lang, keywords in lang_patterns.items():
        if any(kw in p for kw in keywords):
            language_hints.append(lang)

    return {
        "intent": intent,
        "framework": framework,
        "features": features,
        "complexity": complexity,
        "language_hints": language_hints,
        "prompt_clean": p,
    }
