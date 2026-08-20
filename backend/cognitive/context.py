"""YELMON Dev X - Gestionnaire de contexte conversationnel."""

import re
import time
from typing import Optional


class ConversationContext:
    """Gère le contexte d'une conversation : thème, entités, suivi."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def _get(self, session_id: str) -> dict:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "current_topic": None,
                "current_language": None,
                "current_intent": None,
                "entities": {},
                "constraints": [],
                "topic_history": [],
                "mentioned_functions": [],
                "mentioned_classes": [],
                "mentioned_files": [],
                "pending_questions": [],
                "conversation_goal": None,
                "last_activity": time.time(),
            }
        return self._sessions[session_id]

    def update(self, session_id: str, user_message: str, assistant_response: str,
               intent: str = None, language: str = None):
        """Met à jour le contexte après chaque échange."""
        ctx = self._get(session_id)
        ctx["last_activity"] = time.time()

        if intent:
            ctx["current_intent"] = intent
        if language:
            ctx["current_language"] = language

        self._extract_entities(ctx, user_message)
        self._extract_topic(ctx, user_message, intent)
        self._extract_constraints(ctx, user_message)
        self._extract_code_references(ctx, user_message)
        self._extract_code_references(ctx, assistant_response)
        self._detect_pending_questions(ctx, assistant_response)

    def get_full_context(self, session_id: str) -> dict:
        ctx = self._get(session_id)
        return {
            "current_topic": ctx["current_topic"],
            "current_language": ctx["current_language"],
            "current_intent": ctx["current_intent"],
            "entities": ctx["entities"],
            "constraints": ctx["constraints"],
            "topic_history": ctx["topic_history"][-5:],
            "mentioned_functions": ctx["mentioned_functions"][-10:],
            "mentioned_classes": ctx["mentioned_classes"][-10:],
            "mentioned_files": ctx["mentioned_files"][-5:],
            "pending_questions": ctx["pending_questions"],
            "conversation_goal": ctx["conversation_goal"],
        }

    def get_context_summary(self, session_id: str) -> str:
        ctx = self._get(session_id)
        parts = []
        if ctx["current_topic"]:
            parts.append(f"Topic: {ctx['current_topic']}")
        if ctx["current_language"]:
            parts.append(f"Langage: {ctx['current_language']}")
        if ctx["current_intent"]:
            parts.append(f"Intent: {ctx['current_intent']}")
        if ctx["constraints"]:
            parts.append(f"Contraintes: {', '.join(ctx['constraints'][-3:])}")
        if ctx["mentioned_functions"]:
            parts.append(f"Fonctions: {', '.join(ctx['mentioned_functions'][-3:])}")
        if ctx["conversation_goal"]:
            parts.append(f"Objectif: {ctx['conversation_goal']}")
        return " | ".join(parts) if parts else "Nouvelle conversation"

    def resolve_reference(self, session_id: str, message: str) -> Optional[str]:
        """Résout les références implicites (pronoms, "cette fonction", etc.)."""
        ctx = self._get(session_id)
        msg_lower = message.lower().strip()

        ref_patterns = [
            (r"cette fonction\s+(\w+)", "function"),
            (r"la fonction\s+(\w+)", "function"),
            (r"le fichier\s+(\w+)", "file"),
            (r"la classe\s+(\w+)", "class"),
            (r"ce module\s+(\w+)", "module"),
        ]
        for pattern, ref_type in ref_patterns:
            m = re.search(pattern, msg_lower)
            if m:
                return f"{ref_type}:{m.group(1)}"

        pronouns = ["il", "elle", "ceci", "cela", "ça", "ce"]
        if any(msg_lower.startswith(p + " ") or msg_lower == p for p in pronouns):
            if ctx["mentioned_functions"]:
                return f"function:{ctx['mentioned_functions'][-1]}"
            if ctx["mentioned_classes"]:
                return f"class:{ctx['mentioned_classes'][-1]}"

        return None

    def set_goal(self, session_id: str, goal: str):
        self._get(session_id)["conversation_goal"] = goal

    def get_goal(self, session_id: str) -> Optional[str]:
        return self._get(session_id).get("conversation_goal")

    def clear(self, session_id: str):
        self._sessions.pop(session_id, None)

    def cleanup_old(self, max_age_seconds: int = 3600):
        now = time.time()
        to_remove = [sid for sid, ctx in self._sessions.items()
                     if now - ctx["last_activity"] > max_age_seconds]
        for sid in to_remove:
            del self._sessions[sid]

    def _extract_entities(self, ctx: dict, message: str):
        msg_lower = message.lower()
        entity_patterns = {
            "language": [
                (r"\b(python|py)\b", "python"),
                (r"\b(javascript|js|node)\b", "javascript"),
                (r"\b(java)\b", "java"),
                (r"\b(rust)\b", "rust"),
                (r"\b(go|golang)\b", "go"),
                (r"\b(c\+\+|cpp)\b", "cpp"),
                (r"\b(html|css)\b", "html"),
            ],
            "framework": [
                (r"\b(flask)\b", "flask"),
                (r"\b(django)\b", "django"),
                (r"\b(fastapi)\b", "fastapi"),
                (r"\b(express)\b", "express"),
                (r"\b(react)\b", "react"),
                (r"\b(pygame)\b", "pygame"),
            ],
        }
        for entity_type, patterns in entity_patterns.items():
            for regex, value in patterns:
                if re.search(regex, msg_lower):
                    ctx["entities"][entity_type] = value
                    if entity_type == "language":
                        ctx["current_language"] = value

    def _extract_topic(self, ctx: dict, message: str, intent: str = None):
        msg_lower = message.lower()
        topic_keywords = {
            "authentification": ["login", "auth", "jwt", "token", "password", "session"],
            "api": ["api", "rest", "endpoint", "route", "request"],
            "database": ["database", "sql", "sqlite", "mongo", "bdd", "requete"],
            "frontend": ["html", "css", "react", "vue", "page", "ui", "interface"],
            "testing": ["test", "unittest", "pytest", "jest", "spec"],
            "deployment": ["deploy", "docker", "render", "heroku", "serveur"],
            "security": ["security", "sécurité", "xss", "csrf", "injection"],
            "optimization": ["optimise", "performance", "cache", "rapide", "lent"],
        }
        for topic, keywords in topic_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                if ctx["current_topic"] != topic:
                    ctx["topic_history"].append({
                        "topic": topic,
                        "ts": time.time(),
                    })
                    ctx["topic_history"] = ctx["topic_history"][-10:]
                ctx["current_topic"] = topic
                return

    def _extract_constraints(self, ctx: dict, message: str):
        msg_lower = message.lower()
        constraint_patterns = [
            (r"sans\s+(\w+)", lambda m: f"sans {m.group(1)}"),
            (r"avec\s+(\w+)", lambda m: f"avec {m.group(1)}"),
            (r"en\s+(\w+)", lambda m: f"en {m.group(1)}"),
            (r"pour\s+(\w+)", lambda m: f"pour {m.group(1)}"),
        ]
        for regex, extractor in constraint_patterns:
            m = re.search(regex, msg_lower)
            if m:
                constraint = extractor(m)
                if constraint not in ctx["constraints"]:
                    ctx["constraints"].append(constraint)
                    ctx["constraints"] = ctx["constraints"][-10:]

    def _extract_code_references(self, ctx: dict, text: str):
        func_matches = re.findall(r"(?:def|function|fn)\s+(\w+)", text)
        for fn in func_matches:
            if fn not in ctx["mentioned_functions"]:
                ctx["mentioned_functions"].append(fn)
        ctx["mentioned_functions"] = ctx["mentioned_functions"][-10:]

        class_matches = re.findall(r"class\s+(\w+)", text)
        for cls in class_matches:
            if cls not in ctx["mentioned_classes"]:
                ctx["mentioned_classes"].append(cls)
        ctx["mentioned_classes"] = ctx["mentioned_classes"][-10:]

        file_matches = re.findall(r"[\w/\\]+\.\w{1,5}", text)
        for f in file_matches:
            if f not in ctx["mentioned_files"] and ("/" in f or "\\" in f):
                ctx["mentioned_files"].append(f)
        ctx["mentioned_files"] = ctx["mentioned_files"][-5:]

    def _detect_pending_questions(self, ctx: dict, response: str):
        if "?" in response:
            questions = [s.strip() for s in response.split("?") if s.strip()]
            if questions:
                ctx["pending_questions"] = questions[-3:]
        else:
            ctx["pending_questions"] = []
