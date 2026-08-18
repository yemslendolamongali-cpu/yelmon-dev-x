"""YELMON Dev X - Agent d'analyse et de dialogue avancé."""

import re
from collections import Counter


class YelmonAgent:
    """Analyse le code, détecte les bugs, suggère des améliorations, et répond."""

    def analyze(self, code: str) -> dict:
        """Analyse complète du code : structure, qualité, bugs potentiels, suggestions."""
        lines = code.splitlines()
        if not lines:
            return {"error": "Code vide", "lines": 0}

        # --- Structure ---
        functions = re.findall(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(", code, re.M)
        classes = re.findall(r"^\s*class\s+(\w+)", code, re.M)
        imports = re.findall(r"^\s*(?:import|from)\s+([\w.]+)", code, re.M)
        decorators = re.findall(r"^\s*@(\w+)", code, re.M)

        # --- Métriques ---
        code_lines = [ln for ln in lines if ln.strip() and not ln.strip().startswith("#")]
        comment_lines = [ln for ln in lines if ln.strip().startswith("#")]
        blank_lines = [ln for ln in lines if not ln.strip()]
        docstrings = len(re.findall(r'""".*?"""|\'\'\'.*?\'\'\'', code, re.S))

        # Complexité cyclomatique approximative
        complexity = 1
        for ln in code_lines:
            complexity += ln.count(" if ") + ln.count(" elif ") + ln.count(" and ") + ln.count(" or ")
            complexity += ln.count(" for ") + ln.count(" while ")
            complexity += ln.count(" except ") + ln.count(" except(")
            complexity += ln.count(" with ")

        # --- Détection de bugs potentiels ---
        bugs = self._detect_bugs(code, lines)

        # --- Avertissements qualité ---
        warnings = self._detect_warnings(code, lines, functions, classes)

        # --- Suggestions d'amélioration ---
        suggestions = self._suggest_improvements(code, lines, functions, classes, imports)

        # --- Score de qualité ---
        penalty = len(bugs) * 8 + len(warnings) * 3
        score = max(0, min(100, 100 - penalty - max(0, complexity - 10) * 2))

        return {
            "lines": len(lines),
            "code_lines": len(code_lines),
            "comment_lines": len(comment_lines),
            "blank_lines": len(blank_lines),
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "decorators": decorators,
            "docstrings": docstrings,
            "complexity": complexity,
            "bugs": bugs,
            "warnings": warnings,
            "suggestions": suggestions,
            "score": score,
            "grade": self._grade(score),
        }

    def _detect_bugs(self, code: str, lines: list) -> list:
        """Détecte les bugs potentiels courants."""
        bugs = []

        # Division par zéro potentielle
        for i, ln in enumerate(lines):
            m = re.search(r"\/\s*(\w+)", ln)
            if m and m.group(1) in ("0", "0.0"):
                bugs.append({"type": "critical", "line": i + 1, "msg": "Division par zéro possible"})

        # Variable utilisée avant assignment
        assigns = set()
        for i, ln in enumerate(lines):
            m = re.match(r"\s*(\w+)\s*=", ln)
            if m:
                assigns.add(m.group(1))

        # Bare except
        for i, ln in enumerate(lines):
            if re.match(r"\s*except\s*:", ln):
                bugs.append({"type": "warning", "line": i + 1, "msg": "except sans type d'exception (bare except)"})

        # Mutable default argument
        for i, ln in enumerate(lines):
            if re.search(r"def\s+\w+\s*\(.*=\s*(\[|\{|\[\])", ln):
                bugs.append({"type": "warning", "line": i + 1, "msg": "Argument par défaut mutable (list/dict)"})

        # Comparaison avec ==
        for i, ln in enumerate(lines):
            if re.search(r"==\s*(True|False|None)\b", ln):
                bugs.append({"type": "style", "line": i + 1, "msg": "Utilisez 'is' au lieu de '==' pour True/False/None"})

        # String formatting sans f-string
        if "%" in code and ("%.%" in code or re.search(r'["\'].*%[sdf]', code)):
            bugs.append({"type": "style", "line": 0, "msg": "Considérez f-strings au lieu de % formatting"})

        # Open sans encoding
        for i, ln in enumerate(lines):
            if "open(" in ln and "encoding" not in ln and "rb" not in ln:
                bugs.append({"type": "warning", "line": i + 1, "msg": "open() sans encoding explicite"})

        # Nested class/function definition shadowing
        if re.search(r"def\s+(\w+).*:\s*\n(?:\s+.*\n)*?\s+def\s+(\w+)", code):
            bugs.append({"type": "info", "line": 0, "msg": "Fonction imbriquée détectée"})

        return bugs

    def _detect_warnings(self, code: str, lines: list, functions: list, classes: list) -> list:
        """Détecte les problèmes de qualité de code."""
        warnings = []

        # Lignes trop longues
        long_lines = [i + 1 for i, ln in enumerate(lines) if len(ln) > 100]
        if long_lines:
            warnings.append(f"Lignes trop longues (>100 car.) : {long_lines[:5]}{'...' if len(long_lines) > 5 else ''}")

        # TODO/FIXME/HACK
        todos = [i + 1 for i, ln in enumerate(lines) if re.search(r"TODO|FIXME|HACK|XXX", ln, re.I)]
        if todos:
            warnings.append(f"Commentaires TODO/FIXME trouvés : lignes {todos}")

        # Fonctions sans docstring
        func_no_doc = []
        for fn in functions:
            pattern = rf"def\s+{re.escape(fn)}\s*\(.*?\):.*?\n(\s+\"\"\"|')"
            if not re.search(pattern, code, re.S):
                func_no_doc.append(fn)
        if func_no_doc:
            warnings.append(f"Fonctions sans docstring : {', '.join(func_no_doc[:5])}")

        # Code dupliqué approximatif (lignes identiques > 2 fois)
        stripped = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
        counter = Counter(stripped)
        dupes = {ln: cnt for ln, cnt in counter.items() if cnt > 2 and len(ln) > 10}
        if dupes:
            top = sorted(dupes.items(), key=lambda x: -x[1])[:3]
            warnings.append(f"Code potentiellement dupliqué : {', '.join(f'\"{ln[:40]}...\" x{c}' for ln, c in top)}")

        # Import inutilisé approximatif
        used_names = set()
        for ln in lines:
            for word in re.findall(r"\b(\w+)\b", ln):
                used_names.add(word)
        unused = [imp for imp in functions + classes if imp not in used_names and imp not in ("main",)]
        # Trop approximatif, on le met en info seulement
        if len(lines) > 50 and len(unused) > 2:
            warnings.append(f"Imports potentiellement inutilisés (à vérifier)")

        return warnings

    def _suggest_improvements(self, code: str, lines: list, functions: list, classes: list, imports: list) -> list:
        """Suggère des améliorations concrètes."""
        suggestions = []

        # Pas de type hints
        func_no_hint = [fn for fn in functions if "->" not in code.split(f"def {fn}")[1].split("):")[0] if f"def {fn}" in code]
        if func_no_hint:
            suggestions.append("Ajoutez des type hints aux fonctions (-> type, param: type)")

        # Pas de logging
        if "print(" in code and len(lines) > 30:
            suggestions.append("Remplacez print() par logging pour un code plus professionnel")

        # Pas de gestion d'erreurs
        if "try" not in code and ("open(" in code or "request" in code or "json.load" in code):
            suggestions.append("Ajoutez de la gestion d'erreurs (try/except) pour les opérations I/O")

        # Pas de tests
        if "def " in code and "test" not in code.lower():
            suggestions.append("Ajoutez des tests unitaires (unittest ou pytest)")

        # Pas de configuration
        if "SECRET" in code or "TOKEN" in code or "password" in code.lower():
            if "os.environ" not in code and ".env" not in code:
                suggestions.append("Utilisez des variables d'environnement pour les secrets (os.environ)")

        # Classe sans __init__
        for cls in classes:
            if f"class {cls}" in code:
                section = code.split(f"class {cls}")[1] if f"class {cls}" in code else ""
                if "__init__" not in section[:500]:
                    suggestions.append(f"Classe '{cls}' sans méthode __init__")

        # Pas de context manager
        if "open(" in code and "with " not in code:
            suggestions.append("Utilisez des context managers (with open(...) as f:)")

        # Fonctions trop longues
        if functions:
            suggestions.append(f"Le code contient {len(functions)} fonction(s), {len(classes)} classe(s)")

        return suggestions

    def _grade(self, score: int) -> str:
        if score >= 90:
            return "A+"
        if score >= 80:
            return "A"
        if score >= 70:
            return "B"
        if score >= 60:
            return "C"
        if score >= 50:
            return "D"
        return "F"

    def explain(self, code: str) -> str:
        """Génère une explication du code en langage naturel."""
        analysis = self.analyze(code)
        parts = []

        if analysis["functions"]:
            parts.append(f"Le code contient {len(analysis['functions'])} fonction(s) : {', '.join(analysis['functions'])}.")
        if analysis["classes"]:
            parts.append(f"Il définit {len(analysis['classes'])} classe(s) : {', '.join(analysis['classes'])}.")
        if analysis["imports"]:
            parts.append(f"Les imports incluent : {', '.join(analysis['imports'][:6])}.")
        parts.append(f"Score de qualité : {analysis['score']}/100 ({analysis['grade']}).")

        if analysis["bugs"]:
            crit = [b for b in analysis["bugs"] if b["type"] == "critical"]
            if crit:
                parts.append(f"ATTENTION : {len(crit)} bug(s) critique(s) détecté(s) !")
        if analysis["warnings"]:
            parts.append(f"{len(analysis['warnings'])} avertissement(s) de qualité.")
        if analysis["suggestions"]:
            parts.append("Suggestions : " + "; ".join(analysis["suggestions"][:3]) + ".")

        return " ".join(parts)

    def refactor_suggestions(self, code: str) -> list:
        """Retourne des suggestions concrètes de refactoring."""
        suggestions = []
        lines = code.splitlines()

        # Fonction trop longue (> 50 lignes)
        current_func = None
        func_start = 0
        for i, ln in enumerate(lines):
            m = re.match(r"def\s+(\w+)", ln)
            if m:
                if current_func and i - func_start > 50:
                    suggestions.append(f"Fonction '{current_func}' trop longue ({i - func_start} lignes) - découpez-la")
                current_func = m.group(1)
                func_start = i
        if current_func and len(lines) - func_start > 50:
            suggestions.append(f"Fonction '{current_func}' trop longue ({len(lines) - func_start} lignes)")

        # Si/elif chaînage trop long
        consecutive_if = 0
        for ln in lines:
            stripped = ln.strip()
            if stripped.startswith("if ") or stripped.startswith("elif "):
                consecutive_if += 1
            else:
                if consecutive_if > 4:
                    suggestions.append(f"Chaîne if/elif trop longue ({consecutive_if}) - utilisez un dictionnaire ou match/case")
                consecutive_if = 0

        # Parameters > 5
        for m in re.finditer(r"def\s+\w+\((.*?)\)", code, re.S):
            params = [p.strip().split(":")[0].split("=")[0].strip()
                      for p in m.group(1).split(",") if p.strip() and p.strip() != "self"]
            if len(params) > 5:
                suggestions.append(f"Fonction avec {len(params)} paramètres - utilisez un dataclass ou dict")

        return suggestions

    def reply(self, message: str) -> str:
        """Répond aux messages de l'utilisateur en langage naturel."""
        msg = (message or "").lower().strip()

        if not msg:
            return "Comment puis-je vous aider ? Décrivez ce que vous voulez coder."

        # Salutations
        if any(w in msg for w in ("bonjour", "salut", "hello", "hey", "coucou")):
            return (
                "Bonjour ! Je suis YELMON Dev X, votre assistant de codage. "
                "Je peux générer du code, analyser votre code, détecter des bugs, "
                "et suggérer des améliorations. Que souhaitez-vous faire ?"
            )

        # Aide
        if any(w in msg for w in ("help", "aide", "commande", "usage")):
            return (
                "Voici ce que je peux faire :\n"
                "- Générer du code : décrivez votre besoin en langage naturel\n"
                "- Analyser du code : collez-le dans l'éditeur et cliquez 'Analyser'\n"
                "- Exécuter du code : collez du Python et cliquez 'Exécuter'\n"
                "- Rechercher : utilisez la barre de recherche pour retrouver du code\n"
                "- Chaque réponse inclut des suggestions d'amélioration"
            )

        # Génération
        if any(w in msg for w in ("generer", "generate", "code", "créer", "ecrire", "écrire")):
            return (
                "Décrivez votre besoin dans la zone de texte puis cliquez sur Générer. "
                "Plus votre description est précise, meilleur sera le résultat. "
                "Exemples : 'API REST Flask avec CRUD pour des utilisateurs', "
                "'Jeu de snake en pygame', 'Bot Discord avec commands slash'"
            )

        # Bugs
        if any(w in msg for w in ("bug", "erreur", "error", "problème", "crash")):
            return (
                "Pour diagnostiquer un bug :\n"
                "1. Collez votre code dans l'éditeur\n"
                "2. Cliquez 'Analyser' pour détecter les problèmes\n"
                "3. Cliquez 'Exécuter' pour voir les erreurs en temps réel\n"
                "4. Le code détecte automatiquement : division par zéro, bare except, "
                "args mutables, comparaisons, encoding manquant"
            )

        # Refactoring
        if any(w in msg for w in ("refactor", "refactoriser", "améliorer", "optimiser", "clean")):
            return (
                "Pour des suggestions de refactoring :\n"
                "1. Collez le code dans l'éditeur\n"
                "2. L'analyse détecte automatiquement :\n"
                "   - Fonctions trop longues\n"
                "   - Chaînes if/elif à refactoriser\n"
                "   - Trop de paramètres\n"
                "   - Code dupliqué\n"
                "   - Manque de type hints, logging, tests"
            )

        # Architecture
        if any(w in msg for w in ("architect", "structure", "projet", "dossier", "organisation")):
            return (
                "Pour structurer un projet :\n"
                " mon_projet/\n"
                "  ├── src/          # Code source\n"
                "  │   ├── models/   # Modèles de données\n"
                "  │   ├── routes/   # Routes/API\n"
                "  │   └── utils/    # Utilitaires\n"
                "  ├── tests/        # Tests unitaires\n"
                "  ├── docs/         # Documentation\n"
                "  ├── requirements.txt\n"
                "  └── README.md"
            )

        # Merci
        if any(w in msg for w in ("merci", "thanks", "thank", "super", "parfait", "genial")):
            return (
                "Avec plaisir ! N'hésitez pas si vous avez d'autres questions. "
                "Codez plus vite, codez mieux. — YELMON Dev X"
            )

        # Question sur les langages
        if any(w in msg for w in ("langage", "language", "python", "javascript", "java", "rust", "go")):
            return (
                "Je supporte : Python, JavaScript, Java, Go, Rust et C++. "
                "Sélectionnez le langage dans le menu déroulant avant de générer. "
                "Chaque langage a ses propres templates pour les API, bots, jeux, etc."
            )

        # Défaut
        return (
            "Je suis YELMON Dev X. Je peux :\n"
            "- Générer du code (décrivez votre besoin)\n"
            "- Analyser du code (collez-le et cliquez Analyser)\n"
            "- Détecter bugs, améliorations, refactoring\n"
            "- Répondre à vos questions sur le développement\n"
            "Que souhaitez-vous faire ?"
        )

    def reply_cognitive(self, message: str, cognitive_result: dict) -> str:
        """Réponse enrichie par le système cognitif."""
        intent = cognitive_result.get("intent", "general")
        language = cognitive_result.get("language")
        complexity = cognitive_result.get("complexity", "simple")
        adaptations = cognitive_result.get("adaptations", {})
        ref = cognitive_result.get("reference_resolved")
        turn = cognitive_result.get("turn_count", 1)

        base = self.reply(message)

        if ref:
            base = f"(Référence détectée: {ref})\n{base}"

        if turn == 1 and intent != "greeting":
            profile_summary = cognitive_result.get("user_profile_summary", "")
            if profile_summary:
                level = "intermédiaire"
                if "beginner" in profile_summary:
                    level = "débutant"
                elif "advanced" in profile_summary:
                    level = "avancé"
                base = f"[Niveau détecté: {level}] {base}"

        if adaptations.get("add_explanations") and intent in ("code_generation", "explanation"):
            base += "\n\n💡 N'hésitez pas à demander des explications sur chaque partie du code."

        if adaptations.get("add_examples") and complexity == "complex":
            base += "\n\n📝 Je peux fournir des exemples d'utilisation si vous le souhaitez."

        if adaptations.get("detail_level") == "concise" and intent in ("code_generation",):
            base = base.split("\n")[0] + "\n(Voici le code directement, comme vous semblez préférer les réponses concises.)"

        return base
