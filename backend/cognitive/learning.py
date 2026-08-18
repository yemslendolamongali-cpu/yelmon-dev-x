"""YELMON Dev X - Système d'apprentissage adaptatif."""

import json
import os
import time
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class AdaptiveLearner:
    """Apprend des interactions pour améliorer les réponses futures."""

    def __init__(self):
        self._file = os.path.join(DATA_DIR, "cognitive_learning.json")
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self._file):
            try:
                with open(self._file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "feedback": [],
            "successful_patterns": {},
            "failed_patterns": {},
            "response_ratings": [],
            "learned_rules": [],
        }

    def _save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def record_feedback(self, username: str, message: str, response: str,
                        rating: int, intent: str):
        """Enregistre le feedback utilisateur (1-5 étoiles)."""
        self._data["feedback"].append({
            "username": username,
            "message": message[:200],
            "response": response[:200],
            "rating": max(1, min(5, rating)),
            "intent": intent,
            "ts": time.time(),
        })
        self._data["feedback"] = self._data["feedback"][-1000:]
        pattern_key = f"{intent}"
        if rating >= 4:
            self._data["successful_patterns"][pattern_key] = \
                self._data["successful_patterns"].get(pattern_key, 0) + 1
        elif rating <= 2:
            self._data["failed_patterns"][pattern_key] = \
                self._data["failed_patterns"].get(pattern_key, 0) + 1
        self._data["response_ratings"].append({
            "rating": rating,
            "intent": intent,
            "ts": time.time(),
        })
        self._data["response_ratings"] = self._data["response_ratings"][-2000:]
        self._update_rules()
        self._save()

    def record_auto_feedback(self, username: str, intent: str, success: bool):
        """Feedback automatique basé sur l'acceptation implicite."""
        rating = 4 if success else 2
        self._data["feedback"].append({
            "username": username,
            "message": "(auto)",
            "response": "(auto)",
            "rating": rating,
            "intent": intent,
            "ts": time.time(),
            "auto": True,
        })
        self._data["feedback"] = self._data["feedback"][-1000:]
        pattern_key = f"{intent}"
        if success:
            self._data["successful_patterns"][pattern_key] = \
                self._data["successful_patterns"].get(pattern_key, 0) + 1
        else:
            self._data["failed_patterns"][pattern_key] = \
                self._data["failed_patterns"].get(pattern_key, 0) + 1
        self._save()

    def get_success_rate(self, intent: str) -> float:
        s = self._data["successful_patterns"].get(intent, 0)
        f = self._data["failed_patterns"].get(intent, 0)
        total = s + f
        return s / total if total > 0 else 0.5

    def get_avg_rating(self, intent: Optional[str] = None) -> float:
        ratings = self._data["response_ratings"]
        if intent:
            ratings = [r for r in ratings if r["intent"] == intent]
        if not ratings:
            return 3.0
        return sum(r["rating"] for r in ratings) / len(ratings)

    def get_learning_stats(self) -> dict:
        total = len(self._data["feedback"])
        auto = sum(1 for f in self._data["feedback"] if f.get("auto"))
        manual = total - auto
        avg = self.get_avg_rating()
        return {
            "total_feedback": total,
            "auto_feedback": auto,
            "manual_feedback": manual,
            "avg_rating": round(avg, 2),
            "successful_patterns": dict(self._data["successful_patterns"]),
            "failed_patterns": dict(self._data["failed_patterns"]),
            "rules_count": len(self._data["learned_rules"]),
        }

    def _update_rules(self):
        rules = []
        sp = self._data["successful_patterns"]
        fp = self._data["failed_patterns"]
        for intent, count in sp.items():
            fail = fp.get(intent, 0)
            total = count + fail
            if total >= 5 and count / total > 0.8:
                rules.append({
                    "type": "strength",
                    "intent": intent,
                    "confidence": round(count / total, 2),
                    "msg": f"Bon taux de succès pour '{intent}' ({count}/{total})",
                })
            elif total >= 5 and count / total < 0.3:
                rules.append({
                    "type": "weakness",
                    "intent": intent,
                    "confidence": round(fail / total, 2),
                    "msg": f"Faible taux de succès pour '{intent}' ({count}/{total}) — amélioration nécessaire",
                })
        self._data["learned_rules"] = rules

    def get_adaptations(self, intent: str) -> dict:
        """Retourne les adaptations à appliquer pour un intent donné."""
        rate = self.get_success_rate(intent)
        avg = self.get_avg_rating(intent)
        adaptations = {
            "detail_level": "normal",
            "style": "standard",
            "add_examples": False,
            "add_explanations": False,
        }
        if rate < 0.4:
            adaptations["detail_level"] = "high"
            adaptations["add_examples"] = True
            adaptations["add_explanations"] = True
            adaptations["style"] = "thorough"
        elif rate < 0.6:
            adaptations["detail_level"] = "medium"
            adaptations["add_examples"] = True
        elif rate > 0.85:
            adaptations["detail_level"] = "concise"
            adaptations["style"] = "efficient"
        if avg < 2.5:
            adaptations["style"] = "extra_careful"
            adaptations["add_explanations"] = True
        return adaptations

    def get_top_issues(self, top_k: int = 5) -> list[dict]:
        fp = self._data["failed_patterns"]
        sorted_issues = sorted(fp.items(), key=lambda x: -x[1])
        return [{"intent": i, "failures": c} for i, c in sorted_issues[:top_k]]
