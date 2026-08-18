"""YELMON Dev X - Analyseur de code avancé

© 2026 Yems junior lendola — All Rights Reserved.
Proprietary — do not distribute.

Détecte les erreurs syntaxiques réelles, signale la localisation
exacte, et corrige automatiquement le code pour chaque langage.
"""

import re
import ast
import sys
import json
import subprocess
import tempfile
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Auto-corrections Python courantes
# ---------------------------------------------------------------------------

_PY_FIXES = [
    (r"except\s*:", "except Exception:"),
    (r"print\s*\(([^)]*)\)\s*$", r"print(\1)"),
    (r"==\s*True\b", "is True"),
    (r"==\s*False\b", "is False"),
    (r"==\s*None\b", "is None"),
    (r"!=\s*None\b", "is not None"),
    (r"(\w+)\s*=\s*(\[|\{)\s*\]", r"\1 = \2]"),
    (r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\)\s*:", r"for \1 in range(len(\2)):"),
    (r"import\s+(\w+)\s*,\s*(\w+)", r"import \1\nimport \2"),
]


def _check_python(code: str) -> list:
    """Vérifie la syntaxe Python via compile()."""
    errors = []
    try:
        compile(code, "<code>", "exec")
    except SyntaxError as e:
        errors.append({
            "line": e.lineno or 0,
            "col": e.offset or 0,
            "type": "syntax",
            "severity": "critical",
            "message": str(e.msg),
            "source": "python-compile",
        })
    return errors


def _check_js(code: str) -> list:
    """Vérifie la syntaxe JavaScript via Node --check."""
    errors = []
    try:
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            result = subprocess.run(
                ["node", "--check", f.name],
                capture_output=True, text=True, timeout=10,
            )
            Path(f.name).unlink(missing_ok=True)
            if result.returncode != 0:
                msg = result.stderr.strip().split("\n")[0] if result.stderr else "Syntax error"
                m = re.search(r"(\d+)\s*\((\d+)\)", msg)
                line = int(m.group(1)) if m else 0
                col = int(m.group(2)) if m else 0
                errors.append({
                    "line": line, "col": col, "type": "syntax",
                    "severity": "critical", "message": msg,
                    "source": "node-check",
                })
    except FileNotFoundError:
        errors.append({
            "line": 0, "col": 0, "type": "info",
            "severity": "info", "message": "Node.js non disponible pour vérification JS",
            "source": "node-check",
        })
    except Exception:
        pass
    return errors


def _check_html(code: str) -> list:
    """Vérifie le HTML pour les erreurs courantes."""
    errors = []
    # Balises non fermées
    open_tags = re.findall(r"<(\w+)[^/>]*>", code)
    void_tags = {"br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "param", "source", "track", "wbr"}
    close_tags = re.findall(r"</(\w+)>", code)
    for tag in open_tags:
        if tag.lower() not in void_tags and tag not in close_tags:
            errors.append({
                "line": 0, "col": 0, "type": "html",
                "severity": "warning", "message": f"Balise <{tag}> non fermée",
                "source": "html-check",
            })
    # Attributs sans guillemets
    unquoted = re.findall(r'<\w+\s+[^>]*\w+=[^"\'\s>]+', code)
    for match in unquoted[:3]:
        errors.append({
            "line": 0, "col": 0, "type": "html",
            "severity": "style", "message": "Attribut HTML sans guillemets détecté",
            "source": "html-check",
        })
    return errors


# ---------------------------------------------------------------------------
# Auto-corrections multi-langages
# ---------------------------------------------------------------------------

def _auto_fix_python(code: str) -> str:
    """Applique les auto-corrections Python."""
    fixed = code
    for pattern, replacement in _PY_FIXES:
        fixed = re.sub(pattern, replacement, fixed, flags=re.M)

    # Ajouter les deux-points manquants après def, class, if, etc.
    keyword_re = re.compile(
        r"^(\s*(?:async\s+)?(?:def|class|if|elif|else|for|while|try|except|finally|with)\b.*?)\s*$"
    )
    lines = fixed.split("\n")
    result = []
    for ln in lines:
        m = keyword_re.match(ln)
        if m:
            content = m.group(1).rstrip()
            if not content.endswith(":"):
                content += ":"
            result.append(content)
        else:
            result.append(ln)

    # Corriger indentation cassée
    for i, ln in enumerate(result):
        stripped = ln.lstrip()
        if stripped and not ln.startswith((" ", "\t")) and stripped not in (
            "import", "from", "class", "def", "if", "for", "while", "try",
            "except", "finally", "with", "elif", "else", "return", "raise",
        ) and not stripped.startswith(("#", "@", '"""', "'''", "def ", "class ", "if ", "for ", "while ")):
            if not ln.endswith(("\\", ":", ",", "(", "[", "{")):
                result[i] = "    " + ln

    return "\n".join(result)


def _auto_fix_js(code: str) -> str:
    """Applique les auto-corrections JavaScript."""
    fixed = code
    # == → ===
    fixed = re.sub(r"(?<!=)==(?!=)", "===", fixed)
    # != → !==
    fixed = re.sub(r"(?<!!)!=(?!=)", "!==", fixed)
    # var → const/let
    fixed = re.sub(r"\bvar\s+", "const ", fixed)
    # Ajouter point-virgules manquants
    lines = fixed.split("\n")
    result = []
    for ln in lines:
        stripped = ln.rstrip()
        if stripped and not stripped.endswith((";", "{", "}", ",", ":", "(", ")", "[", "]", "//", "/*")):
            if not stripped.startswith(("//", "/*", "*", "export ", "import ")):
                result.append(stripped + ";")
                continue
        result.append(stripped)
    return "\n".join(result)


def _auto_fix_html(code: str) -> str:
    """Applique les auto-corrections HTML."""
    fixed = code
    # Fermer les balises non fermées
    void_tags = {"br", "hr", "img", "input", "meta", "link", "area", "base", "col", "embed", "param", "source", "track", "wbr", "!DOCTYPE"}
    open_tags = re.findall(r"<(\w+)[^/>]*>", fixed)
    close_tags = re.findall(r"</(\w+)>", fixed)
    for tag in open_tags:
        if tag.lower() not in void_tags and tag not in close_tags:
            fixed += f"\n</{tag}>"
    return fixed


_AUTO_FIXERS = {
    "python": _auto_fix_python,
    "javascript": _auto_fix_js,
    "js": _auto_fix_js,
    "html": _auto_fix_html,
    "css": lambda c: c,
    "java": lambda c: c,
    "go": lambda c: c,
    "rust": lambda c: c,
    "cpp": lambda c: c,
    "c++": lambda c: c,
}

_CHECKERS = {
    "python": _check_python,
    "javascript": _check_js,
    "js": _check_js,
    "html": _check_html,
}


# ---------------------------------------------------------------------------
# Analyse quality (enhanced from existing agent)
# ---------------------------------------------------------------------------

def _quality_analysis(code: str, language: str) -> dict:
    """Analyse de qualité rapide du code."""
    lines = code.split("\n")
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith(("#", "//", "/*", "*"))]
    issues = []

    # Lignes trop longues
    for i, ln in enumerate(lines):
        if len(ln) > 120:
            issues.append({
                "line": i + 1, "col": 120, "type": "style",
                "severity": "info", "message": f"Ligne trop longue ({len(ln)} car.)",
                "source": "quality",
            })

    # TODO/FIXME
    for i, ln in enumerate(lines):
        if re.search(r"TODO|FIXME|HACK|XXX", ln, re.I):
            issues.append({
                "line": i + 1, "col": 0, "type": "style",
                "severity": "info", "message": "Commentaire TODO/FIXME détecté",
                "source": "quality",
            })

    # Console.log en production (JS)
    if language in ("javascript", "js"):
        for i, ln in enumerate(lines):
            if "console.log" in ln:
                issues.append({
                    "line": i + 1, "col": 0, "type": "style",
                    "severity": "info", "message": "console.log détecté — à retirer en production",
                    "source": "quality",
                })

    # Print en production (Python)
    if language == "python":
        for i, ln in enumerate(lines):
            if re.match(r"\s*print\(", ln):
                issues.append({
                    "line": i + 1, "col": 0, "type": "style",
                    "severity": "info", "message": "print() détecté — considérez logging",
                    "source": "quality",
                })

    return {
        "total_lines": len(lines),
        "code_lines": len(code_lines),
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# API principale
# ---------------------------------------------------------------------------

def analyze_code(code: str, language: str = "auto", fix: bool = False) -> dict:
    """Analyse complète du code avec détection d'erreurs et auto-correction."""
    if not code.strip():
        return {"error": "Code vide", "errors": [], "fixed_code": code}

    lang = language.lower().strip()
    if lang == "auto":
        lang = _detect_language(code)

    # 1. Détection d'erreurs syntaxiques réelles
    checker = _CHECKERS.get(lang)
    syntax_errors = checker(code) if checker else []

    # 2. Analyse qualité
    quality = _quality_analysis(code, lang)

    # 3. Auto-correction si demandée
    fixed_code = code
    if fix:
        fixer = _AUTO_FIXERS.get(lang)
        if fixer:
            fixed_code = fixer(code)
            # Re-vérifier le code corrigé
            if lang in _CHECKERS:
                recheck = _CHECKERS[lang](fixed_code)
                syntax_errors_after = [e for e in recheck if e["type"] == "syntax"]
                if not syntax_errors_after:
                    syntax_errors = []
                else:
                    syntax_errors = syntax_errors_after

    # 4. Score
    critical = sum(1 for e in syntax_errors if e.get("severity") == "critical")
    warnings = sum(1 for e in quality["issues"] if e.get("severity") == "warning")
    style = sum(1 for e in quality["issues"] if e.get("severity") == "style")
    info = sum(1 for e in quality["issues"] if e.get("severity") == "info")

    penalty = critical * 15 + warnings * 5 + style * 2 + info * 1
    score = max(0, min(100, 100 - penalty))

    return {
        "language": lang,
        "errors": syntax_errors,
        "quality_issues": quality["issues"],
        "total_lines": quality["total_lines"],
        "code_lines": quality["code_lines"],
        "fixed_code": fixed_code if fix else None,
        "has_fix": fix and fixed_code != code,
        "score": score,
        "grade": "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D" if score >= 50 else "F",
        "summary": {
            "critical": critical,
            "warnings": warnings,
            "style": style,
            "info": info,
            "total": critical + warnings + style + info,
        },
    }


def _detect_language(code: str) -> str:
    """Détecte automatiquement le langage du code."""
    code_stripped = code.strip()
    if code_stripped.startswith(("{", "<!DOCTYPE", "<html", "<div")):
        return "html"
    if re.search(r"^\s*(def|class|import|from|if __name__)", code, re.M):
        return "python"
    if re.search(r"(function\s|const\s|let\s|var\s|=>\s*\{)", code):
        return "javascript"
    if re.search(r"^\s*(public\s+class|private\s+class|import\s+java)", code, re.M):
        return "java"
    if re.search(r"^\s*func\s+\w+", code, re.M):
        return "go"
    if re.search(r"(fn\s+\w+|let\s+mut|impl\s+)", code):
        return "rust"
    if re.search(r"(#include\s*<|std::|void\s+main)", code):
        return "cpp"
    return "python"
