"""YELMON Dev X - Moteur de raisonnement cognitif (chaîne de pensée, réflexion)."""

import re
import time
import unicodedata
from typing import Optional


def _normalize(text: str) -> str:
    """Supprime les accents pour le matching."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class ThoughtStep:
    """Une étape dans une chaîne de raisonnement."""

    def __init__(self, step_type: str, content: str, confidence: float = 0.8):
        self.step_type = step_type  # observe, analyze, decide, act, reflect
        self.content = content
        self.confidence = confidence
        self.ts = time.time()

    def to_dict(self) -> dict:
        return {
            "type": self.step_type,
            "content": self.content,
            "confidence": self.confidence,
            "ts": self.ts,
        }


class ReasoningChain:
    """Chaîne de raisonnement multi-étapes."""

    def __init__(self):
        self.steps: list[ThoughtStep] = []
        self.conclusion: Optional[str] = None
        self.confidence: float = 0.0

    def add_step(self, step_type: str, content: str, confidence: float = 0.8):
        self.steps.append(ThoughtStep(step_type, content, confidence))

    def finalize(self, conclusion: str):
        self.conclusion = conclusion
        if self.steps:
            self.confidence = sum(s.confidence for s in self.steps) / len(self.steps)

    def to_dict(self) -> dict:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "conclusion": self.conclusion,
            "confidence": round(self.confidence, 2),
        }


class CognitiveReasoner:
    """Moteur de raisonnement : analyse → décision → action → réflexion."""

    def analyze_intent_deep(self, message: str, context: list[dict],
                            user_profile: Optional[dict] = None) -> ReasoningChain:
        chain = ReasoningChain()
        msg_lower = message.lower()

        chain.add_step("observe", f"Message reçu: '{message[:100]}...' " if len(message) > 100
                       else f"Message reçu: '{message}'", 1.0)

        intent_signals = self._extract_signals(msg_lower)
        chain.add_step("analyze", f"Signaux détectés: {intent_signals}", 0.85)

        if context:
            chain.add_step("analyze", f"Contexte conversation: {len(context)} tours précédents", 0.9)

        if user_profile:
            level = user_profile.get("skill_level", "intermediate")
            chain.add_step("analyze", f"Profil utilisateur: niveau={level}", 0.9)

        intent = self._determine_intent(msg_lower, intent_signals)
        chain.add_step("decide", f"Intention principale: {intent}", 0.85)

        language = self._infer_language(msg_lower, intent_signals)
        if language:
            chain.add_step("decide", f"Langage inféré: {language}", 0.8)

        complexity = self._assess_complexity(msg_lower, intent_signals, context)
        chain.add_step("decide", f"Complexité estimée: {complexity}", 0.75)

        approach = self._select_approach(intent, language, complexity, user_profile)
        chain.add_step("act", f"Approche choisie: {approach}", 0.8)

        chain.finalize(f"Intent={intent}, Lang={language}, Complexity={complexity}, Approach={approach}")
        return chain

    def reason_about_code(self, code: str, language: str) -> ReasoningChain:
        chain = ReasoningChain()

        chain.add_step("observe", f"Code analysé: {len(code.splitlines())} lignes, langage={language}", 1.0)

        issues = self._detect_issues(code, language)
        chain.add_step("analyze", f"Problèmes potentiels: {len(issues)}", 0.85)

        quality = self._assess_quality(code, language)
        chain.add_step("analyze", f"Qualité estimée: {quality}/100", 0.7)

        improvements = self._suggest_improvements(code, language, quality)
        chain.add_step("decide", f"Améliorations suggérées: {len(improvements)}", 0.8)

        priority = self._prioritize_fixes(issues)
        chain.add_step("act", f"Priorité de correction: {priority}", 0.75)

        chain.finalize(f"Quality={quality}, Issues={len(issues)}, Improvements={len(improvements)}")
        return chain

    def reflect_on_response(self, user_message: str, response: str,
                            was_successful: bool) -> ReasoningChain:
        chain = ReasoningChain()

        chain.add_step("observe", f"Réponse donnée à: '{user_message[:80]}'", 1.0)

        if was_successful:
            chain.add_step("reflect", "L'utilisateur a accepté la réponse", 0.9)
        else:
            chain.add_step("reflect", "L'utilisateur n'a pas été satisfait", 0.3)

        response_length = len(response)
        if response_length < 50:
            chain.add_step("reflect", "Réponse trop courte, besoin de plus de détails", 0.7)
        elif response_length > 2000:
            chain.add_step("reflect", "Réponse très longue, peut-être trop verbeuse", 0.6)
        else:
            chain.add_step("reflect", "Longueur de réponse appropriée", 0.85)

        chain.finalize("Réflexion terminée")
        return chain

    def _extract_signals(self, msg: str) -> dict:
        signals = {}
        msg_norm = _normalize(msg)
        signal_map = {
            "wants_code": ["generer", "genere", "cree", "creer", "ecris", "ecrire", "code", "build", "make", "create",
                           "write"],
            "wants_analysis": ["analyse", "analyser", "verifie", "verifier", "check", "debug", "corrige", "corriger",
                               "analyze", "review", "test", "scan"],
            "wants_explanation": ["explique", "expliquer", "comment", "pourquoi", "quoi", "explain",
                                  "what", "how", "why"],
            "wants_refactor": ["refactor", "ameliore", "ameliorer", "optimise", "optimiser", "clean", "improve",
                               "optimize", "refactorize"],
            "has_bug": ["bug", "erreur", "error", "crash", "exception", "traceback",
                        "ne marche pas", "ça plante"],
            "wants_tutorial": ["tutoriel", "tutorial", "apprends", "learn", "guide",
                               "how to", "comment faire"],
            "greeting": ["bonjour", "salut", "hello", "hey", "coucou", "bonsoir"],
            "thanks": ["merci", "thanks", "thank", "super", "parfait", "génial"],
            "question": ["?", "est-ce que", "peux-tu", "pourrais-tu", "is it", "can you"],
        }
        for signal, keywords in signal_map.items():
            signals[signal] = any(kw in msg_norm for kw in keywords)
        return signals

    def _determine_intent(self, msg: str, signals: dict) -> str:
        if signals.get("has_bug"):
            return "bug_fix"
        if signals.get("wants_code"):
            return "code_generation"
        if signals.get("wants_analysis"):
            return "code_analysis"
        if signals.get("wants_refactor"):
            return "refactoring"
        if signals.get("wants_explanation"):
            return "explanation"
        if signals.get("wants_tutorial"):
            return "tutorial"
        if signals.get("question"):
            return "question"
        if signals.get("greeting"):
            return "greeting"
        if signals.get("thanks"):
            return "thanks"
        return "general"

    def _infer_language(self, msg: str, signals: dict) -> Optional[str]:
        lang_hints = {
            "python": ["python", "py", "flask", "django", "fastapi", "pip", "pip3"],
            "javascript": ["javascript", "js", "node", "npm", "express", "react", "vue"],
            "java": ["java", "spring", "maven"],
            "go": ["golang", "go lang"],
            "rust": ["rust", "cargo"],
            "cpp": ["c++", "cpp", "cmake"],
            "html": ["html", "css", "landing", "portfolio"],
        }
        for lang, keywords in lang_hints.items():
            if any(kw in msg for kw in keywords):
                return lang
        return None

    def _assess_complexity(self, msg: str, signals: dict, context: list[dict]) -> str:
        indicators = 0
        if len(msg.split()) > 30:
            indicators += 2
        elif len(msg.split()) > 15:
            indicators += 1
        complex_words = ["api", "database", "auth", "websocket", "deploy", "docker",
                         "microservice", "graphql", "cache"]
        indicators += sum(1 for w in complex_words if w in msg)
        if len(context) > 5:
            indicators += 1
        if indicators >= 4:
            return "complex"
        if indicators >= 2:
            return "medium"
        return "simple"

    def _select_approach(self, intent: str, language: Optional[str],
                         complexity: str, user_profile: Optional[dict]) -> str:
        level = (user_profile or {}).get("skill_level", "intermediate")
        if intent == "greeting":
            return "friendly_greeting"
        if intent == "thanks":
            return "acknowledgment"
        if intent == "code_generation":
            if complexity == "complex":
                return "step_by_step_with_examples"
            if level == "beginner":
                return "detailed_with_explanations"
            return "efficient_with_comments"
        if intent == "bug_fix":
            return "diagnose_then_fix"
        if intent == "code_analysis":
            return "thorough_review"
        if intent == "explanation":
            if level == "beginner":
                return "simple_analogies"
            return "technical_deep_dive"
        return "helpful_response"

    def _detect_issues(self, code: str, language: str) -> list[str]:
        issues = []
        if language == "python":
            if re.search(r"except\s*:", code):
                issues.append("bare_except")
            if re.search(r"def\s+\w+\(.*=\s*(\[|\{)", code):
                issues.append("mutable_default")
            if re.search(r"==\s*(None|True|False)", code):
                issues.append("identity_comparison")
            if "open(" in code and "encoding" not in code:
                issues.append("missing_encoding")
        if language in ("javascript", "typescript"):
            if re.search(r"\bvar\b", code):
                issues.append("var_usage")
            if re.search(r"==(?!=)", code):
                issues.append("loose_equality")
        for i, line in enumerate(code.splitlines(), 1):
            if len(line) > 120:
                issues.append(f"long_line_{i}")
                if len([x for x in issues if x.startswith("long_line")]) > 3:
                    break
        return issues

    def _assess_quality(self, code: str, language: str) -> int:
        score = 70
        lines = code.splitlines()
        if not lines:
            return 0
        has_docstring = '"""' in code or "'''" in code
        has_type_hints = "->" in code or ": str" in code or ": int" in code
        has_comments = any(l.strip().startswith("#") or l.strip().startswith("//") for l in lines)
        has_functions = bool(re.search(r"def\s+\w+|function\s+\w+|fn\s+\w+", code))
        has_classes = bool(re.search(r"class\s+\w+", code))
        if has_docstring:
            score += 5
        if has_type_hints:
            score += 5
        if has_comments:
            score += 3
        if has_functions:
            score += 5
        if has_classes:
            score += 3
        issues = self._detect_issues(code, language)
        score -= len(issues) * 5
        avg_line_len = sum(len(l) for l in lines) / len(lines)
        if avg_line_len > 80:
            score -= 5
        if len(lines) > 100:
            score -= 3
        return max(0, min(100, score))

    def _suggest_improvements(self, code: str, language: str, quality: int) -> list[str]:
        suggestions = []
        if language == "python":
            if '"""' not in code and "'''" not in code:
                suggestions.append("Ajoutez des docstrings aux fonctions/classes")
            if "->" not in code:
                suggestions.append("Ajoutez des type hints")
            if "logging" not in code and "print(" in code:
                suggestions.append("Remplacez print() par logging")
            if "test" not in code.lower():
                suggestions.append("Ajoutez des tests unitaires")
        if quality < 50:
            suggestions.append("Score de qualité faible — révision complète recommandée")
        elif quality < 70:
            suggestions.append("Score de qualité moyen — quelques améliorations possibles")
        return suggestions

    def _prioritize_fixes(self, issues: list[str]) -> list[str]:
        critical = [i for i in issues if "bare" in i or "mutable" in i or "identity" in i]
        warnings = [i for i in issues if i not in critical]
        return critical + warnings
