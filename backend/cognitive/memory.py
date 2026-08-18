"""YELMON Dev X - Système de mémoire cognitive (court + long terme)."""

import json
import os
import time
from collections import deque
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class ShortTermMemory:
    """Buffer de conversation en mémoire vive — fenêtre glissante."""

    def __init__(self, max_turns: int = 20):
        self._buffers: dict[str, deque] = {}
        self.max_turns = max_turns

    def _get(self, session_id: str) -> deque:
        if session_id not in self._buffers:
            self._buffers[session_id] = deque(maxlen=self.max_turns)
        return self._buffers[session_id]

    def add(self, session_id: str, role: str, content: str, meta: Optional[dict] = None):
        buf = self._get(session_id)
        buf.append({
            "role": role,
            "content": content,
            "ts": time.time(),
            "meta": meta or {},
        })

    def get_context(self, session_id: str, n: Optional[int] = None) -> list[dict]:
        buf = self._get(session_id)
        items = list(buf)
        if n:
            items = items[-n:]
        return items

    def get_last_user_message(self, session_id: str) -> Optional[str]:
        buf = self._get(session_id)
        for item in reversed(buf):
            if item["role"] == "user":
                return item["content"]
        return None

    def get_last_assistant_message(self, session_id: str) -> Optional[str]:
        buf = self._get(session_id)
        for item in reversed(buf):
            if item["role"] == "assistant":
                return item["content"]
        return None

    def clear(self, session_id: str):
        self._buffers.pop(session_id, None)

    def get_turn_count(self, session_id: str) -> int:
        return len(self._get(session_id))

    def detect_followup(self, session_id: str, message: str) -> Optional[str]:
        """Détecte si un message est un suivi (pronoms, références implicites)."""
        followup_markers = [
            "il", "elle", "ce", "ça", "cette", "celui", "celle",
            "le même", "la même", "encore", "autre", "aussi",
            "mais", "pourtant", "cependant", "donc", "alors",
            "comment", "pourquoi", "quand",
        ]
        msg_lower = message.lower().strip()
        has_marker = any(m in msg_lower for m in followup_markers)
        has_context = self.get_turn_count(session_id) > 0
        if has_marker and has_context and len(msg_lower.split()) < 15:
            last = self.get_last_user_message(session_id)
            return last
        return None


class LongTermMemory:
    """Mémoire persistante : préférences utilisateur, patterns, faits apprisis."""

    def __init__(self):
        self._file = os.path.join(DATA_DIR, "cognitive_memory.json")
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self._file):
            try:
                with open(self._file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"users": {}, "facts": [], "patterns": {}}

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get_user_profile(self, username: str) -> dict:
        if username not in self._data["users"]:
            self._data["users"][username] = {
                "preferred_languages": [],
                "skill_level": "intermediate",
                "interaction_count": 0,
                "topics": {},
                "preferences": {},
                "created_at": time.time(),
                "last_seen": time.time(),
            }
            self._save()
        return self._data["users"][username]

    def update_user_profile(self, username: str, updates: dict):
        profile = self.get_user_profile(username)
        for k, v in updates.items():
            if k in ("preferred_languages",):
                existing = profile.get(k, [])
                if v and v not in existing:
                    existing.insert(0, v)
                    profile[k] = existing[:5]
            elif k == "topics":
                for topic, count in v.items():
                    profile["topics"][topic] = profile["topics"].get(topic, 0) + count
            else:
                profile[k] = v
        profile["last_seen"] = time.time()
        self._save()

    def record_interaction(self, username: str, intent: str, language: str,
                           prompt: str, success: bool):
        profile = self.get_user_profile(username)
        profile["interaction_count"] = profile.get("interaction_count", 0) + 1
        topics = profile.get("topics", {})
        topics[intent] = topics.get(intent, 0) + 1
        profile["topics"] = topics
        if language:
            langs = profile.get("preferred_languages", [])
            if language not in langs:
                langs.insert(0, language)
            profile["preferred_languages"] = langs[:5]
        total = profile["interaction_count"]
        successes = profile.get("success_count", 0) + (1 if success else 0)
        profile["success_count"] = successes
        profile["success_rate"] = round(successes / total, 2) if total else 0
        if total > 20:
            sr = profile.get("success_rate", 0.5)
            if sr > 0.8:
                profile["skill_level"] = "advanced"
            elif sr < 0.4:
                profile["skill_level"] = "beginner"
            else:
                profile["skill_level"] = "intermediate"
        profile["last_seen"] = time.time()
        self._save()

    def add_fact(self, fact: str, source: str = "user", confidence: float = 0.8):
        self._data["facts"].append({
            "fact": fact,
            "source": source,
            "confidence": confidence,
            "ts": time.time(),
        })
        self._data["facts"] = self._data["facts"][-500:]
        self._save()

    def get_relevant_facts(self, query: str, top_k: int = 5) -> list[dict]:
        query_words = set(query.lower().split())
        scored = []
        for fact in self._data["facts"]:
            fact_words = set(fact["fact"].lower().split())
            overlap = len(query_words & fact_words)
            if overlap > 0:
                scored.append((overlap * fact.get("confidence", 0.5), fact))
        scored.sort(key=lambda x: -x[0])
        return [f for _, f in scored[:top_k]]

    def detect_pattern(self, username: str, intent: str, language: str) -> Optional[str]:
        """Détecte des patterns récurrents chez l'utilisateur."""
        profile = self.get_user_profile(username)
        topics = profile.get("topics", {})
        total = sum(topics.values()) or 1
        if topics.get(intent, 0) / total > 0.4 and profile.get("interaction_count", 0) > 10:
            return f"L'utilisateur utilise souvent '{intent}' ({topics[intent]}x/{total})"
        return None

    def get_context_summary(self, username: str) -> str:
        """Résumé du profil utilisateur pour le contexte IA."""
        p = self.get_user_profile(username)
        parts = []
        if p.get("preferred_languages"):
            parts.append(f"Langages préférés: {', '.join(p['preferred_languages'][:3])}")
        parts.append(f"Niveau: {p.get('skill_level', 'intermediate')}")
        parts.append(f"Interactions: {p.get('interaction_count', 0)}")
        if p.get("topics"):
            top = sorted(p["topics"].items(), key=lambda x: -x[1])[:3]
            parts.append(f"Topics principaux: {', '.join(f'{t}({c})' for t, c in top)}")
        return " | ".join(parts)

    def forget_user(self, username: str):
        self._data["users"].pop(username, None)
        self._save()

    def get_all_users_summary(self) -> dict:
        summaries = {}
        for username in self._data["users"]:
            summaries[username] = {
                "profile": self.get_user_profile(username),
                "summary": self.get_context_summary(username),
            }
        return summaries
