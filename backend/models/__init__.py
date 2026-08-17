"""YELMON Dev X - Moteur de génération de code avancé.

Route intelligent par langage → intent → keywords → template.
Supporte : Python, JavaScript, Java, Go, Rust, C++, HTML/CSS.
"""

import re
from models.intent import detect_intent
from models.templates import (
    PYTHON_TEMPLATES, _PY_KEYWORD_MAP, _py_default,
    JS_TEMPLATES, _JS_KEYWORD_MAP,
    JAVA_TEMPLATES, _JAVA_KEYWORD_MAP,
    GO_TEMPLATES, _GO_KEYWORD_MAP,
    RUST_TEMPLATES, _RUST_KEYWORD_MAP,
    CPP_TEMPLATES, _CPP_KEYWORD_MAP,
    HTML_TEMPLATES, _HTML_KEYWORD_MAP,
)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _match_keyword(prompt_clean: str, keyword_map: list) -> str | None:
    """Cherche le premier template correspondant aux keywords du prompt."""
    for keywords, template_name in keyword_map:
        if any(kw in prompt_clean for kw in keywords):
            return template_name
    return None


class CodeGenerator:
    """Génère du code à partir d'une description en langage naturel.

    Utilise une détection d'intention et des templates intelligents
    par langage pour produire du code complet et fonctionnel.
    """

    def __init__(self):
        self._lang_handlers = {
            "python": self._gen_python,
            "javascript": self._gen_javascript,
            "js": self._gen_javascript,
            "java": self._gen_java,
            "go": self._gen_go,
            "golang": self._gen_go,
            "rust": self._gen_rust,
            "cpp": self._gen_cpp,
            "c++": self._gen_cpp,
            "html": self._gen_html,
            "css": self._gen_html,
        }

    def _auto_detect_language(self, prompt: str) -> str:
        """Détecte automatiquement le langage à partir du prompt."""
        analysis = detect_intent(prompt)
        hints = analysis.get("language_hints", [])
        if hints:
            return hints[0]
        return "python"

    def generate(self, prompt: str, language: str = "python") -> str:
        """Point d'entrée principal. Génère du code pour le langage demandé."""
        language = (language or "python").lower().strip()
        if language in ("auto", "automatic", "auto-detect"):
            language = self._auto_detect_language(prompt)
        handler = self._lang_handlers.get(language, self._gen_python)
        try:
            return handler(prompt)
        except Exception as e:
            return self._fallback(prompt, language, str(e))

    def generate_with_analysis(self, prompt: str, language: str = "python") -> dict:
        """Génère du code et retourne aussi l'analyse d'intention."""
        analysis = detect_intent(prompt)
        code = self.generate(prompt, language)
        return {"code": code, "analysis": analysis}

    # ---------------------------------------------------------------
    # Python
    # ---------------------------------------------------------------

    def _gen_python(self, prompt: str) -> str:
        p = _norm(prompt)
        analysis = detect_intent(prompt)

        # Si on détecte un framework spécifique, utiliser le template directement
        if analysis["framework"]:
            fw = analysis["framework"]
            fw_map = {
                "flask": "api_flask",
                "fastapi": "api_fastapi",
                "pygame": "game",
                "tkinter": "gui",
                "discord": "discord_bot",
                "telegram": "telegram_bot",
                "selenium": "scraping",
                "pandas": "data_analysis",
                "sqlalchemy": "auth_jwt",
            }
            tpl_name = fw_map.get(fw)
            if tpl_name and tpl_name in PYTHON_TEMPLATES:
                return PYTHON_TEMPLATES[tpl_name](p)

        # Sinon, matcher par intent
        intent_map = {
            "api": "api_flask",
            "webapp": "webapp",
            "cli": "cli",
            "game": "game",
            "bot": "telegram_bot",
            "scraper": "scraping",
            "desktop": "gui",
            "data": "data_analysis",
            "ml": "machine_learning",
            "auth": "auth_jwt",
            "websocket": "websocket",
            "docker": "docker",
            "testing": "testing",
        }
        tpl_name = intent_map.get(analysis["intent"])
        if tpl_name and tpl_name in PYTHON_TEMPLATES:
            return PYTHON_TEMPLATES[tpl_name](p)

        # Sinon, matcher par keywords
        tpl_name = _match_keyword(p, _PY_KEYWORD_MAP)
        if tpl_name and tpl_name in PYTHON_TEMPLATES:
            return PYTHON_TEMPLATES[tpl_name](p)

        # Fallback
        return _py_default(p)

    # ---------------------------------------------------------------
    # JavaScript
    # ---------------------------------------------------------------

    def _gen_javascript(self, prompt: str) -> str:
        p = _norm(prompt)
        analysis = detect_intent(prompt)

        # Keywords
        tpl_name = _match_keyword(p, _JS_KEYWORD_MAP)
        if tpl_name and tpl_name in JS_TEMPLATES:
            return JS_TEMPLATES[tpl_name](p)

        # Intent fallback
        intent_map = {
            "api": "express_api",
            "webapp": "react_app",
            "bot": "discord_bot",
            "game": "game",
        }
        tpl_name = intent_map.get(analysis["intent"])
        if tpl_name and tpl_name in JS_TEMPLATES:
            return JS_TEMPLATES[tpl_name](p)

        # Default
        return '''\
// Code généré par YELMON Dev X
function maFonction(...valeurs) {
  const resultat = [];
  for (const v of valeurs) {
    resultat.push(v);
  }
  return resultat;
}

console.log(maFonction(1, 2, 3, 4));
'''

    # ---------------------------------------------------------------
    # Java
    # ---------------------------------------------------------------

    def _gen_java(self, prompt: str) -> str:
        p = _norm(prompt)
        tpl_name = _match_keyword(p, _JAVA_KEYWORD_MAP)
        if tpl_name and tpl_name in JAVA_TEMPLATES:
            return JAVA_TEMPLATES[tpl_name](p)
        return JAVA_TEMPLATES["default"](p)

    # ---------------------------------------------------------------
    # Go
    # ---------------------------------------------------------------

    def _gen_go(self, prompt: str) -> str:
        p = _norm(prompt)
        tpl_name = _match_keyword(p, _GO_KEYWORD_MAP)
        if tpl_name and tpl_name in GO_TEMPLATES:
            return GO_TEMPLATES[tpl_name](p)
        return GO_TEMPLATES["default"](p)

    # ---------------------------------------------------------------
    # Rust
    # ---------------------------------------------------------------

    def _gen_rust(self, prompt: str) -> str:
        p = _norm(prompt)
        tpl_name = _match_keyword(p, _RUST_KEYWORD_MAP)
        if tpl_name and tpl_name in RUST_TEMPLATES:
            return RUST_TEMPLATES[tpl_name](p)
        return RUST_TEMPLATES["default"](p)

    # ---------------------------------------------------------------
    # C++
    # ---------------------------------------------------------------

    def _gen_cpp(self, prompt: str) -> str:
        p = _norm(prompt)
        tpl_name = _match_keyword(p, _CPP_KEYWORD_MAP)
        if tpl_name and tpl_name in CPP_TEMPLATES:
            return CPP_TEMPLATES[tpl_name](p)
        return CPP_TEMPLATES["default"](p)

    # ---------------------------------------------------------------
    # HTML/CSS
    # ---------------------------------------------------------------

    def _gen_html(self, prompt: str) -> str:
        p = _norm(prompt)
        analysis = detect_intent(prompt)

        tpl_name = _match_keyword(p, _HTML_KEYWORD_MAP)
        if tpl_name and tpl_name in HTML_TEMPLATES:
            return HTML_TEMPLATES[tpl_name](p)

        intent_map = {
            "html_page": "landing_page",
            "webapp": "landing_page",
        }
        tpl_name = intent_map.get(analysis["intent"])
        if tpl_name and tpl_name in HTML_TEMPLATES:
            return HTML_TEMPLATES[tpl_name](p)

        return HTML_TEMPLATES["default"](p)

    # ---------------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------------

    def _fallback(self, prompt: str, language: str, error: str) -> str:
        return (
            f"# Erreur de génération pour '{language}' : {error}\n"
            f"# Prompt original : {prompt}\n\n"
            f"print('YELMON Dev X - génération en mode dégradé')\n"
        )
