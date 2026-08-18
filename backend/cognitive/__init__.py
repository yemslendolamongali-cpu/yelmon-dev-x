"""YELMON Dev X - Architecture Cognitive Intégrée.

Orchestrateur qui connecte mémoire, raisonnement, apprentissage, contexte,
moteur d'hypothèses et générateur contre-factuel en un système cohérent.
"""

import time
import uuid

from .memory import ShortTermMemory, LongTermMemory
from .reasoning import CognitiveReasoner, ReasoningChain
from .learning import AdaptiveLearner
from .context import ConversationContext
from .hypothesis import HypothesisEngine, hypothesis_engine
from .counterfactual import CounterfactualEngine, counterfactual_engine


class CognitiveArchitecture:
    """Système cognitif complet de YELMON Dev X."""

    def __init__(self):
        self.short_memory = ShortTermMemory(max_turns=30)
        self.long_memory = LongTermMemory()
        self.reasoner = CognitiveReasoner()
        self.learner = AdaptiveLearner()
        self.context = ConversationContext()
        self.hypothesis = HypothesisEngine()
        self.counterfactual = CounterfactualEngine()
        self._active_sessions: dict[str, dict] = {}

    def process_message(self, username: str, message: str,
                        session_id: str = None) -> dict:
        """Traite un message entrant à travers toute la chaîne cognitive.

        Retourne un dict contenant:
          - session_id, reasoning_chain, context_summary,
          - user_profile, adaptations, intent, language, complexity,
          - reference_resolved (si pronon/référence détecté)
        """
        if not session_id:
            session_id = f"{username}_{uuid.uuid4().hex[:8]}"

        previous_context = self.short_memory.get_context(session_id, n=5)

        ref_resolved = self.context.resolve_reference(session_id, message)

        user_profile = self.long_memory.get_user_profile(username)

        chain = self.reasoner.analyze_intent_deep(
            message, previous_context, user_profile
        )

        conclusion = chain.conclusion or ""
        intent = self._parse_field(conclusion, "Intent")
        language = self._parse_field(conclusion, "Lang")
        complexity = self._parse_field(conclusion, "Complexity")

        adaptations = self.learner.get_adaptations(intent)

        self.short_memory.add(session_id, "user", message, {
            "intent": intent, "language": language
        })

        self.context.update(
            session_id, message, "",
            intent=intent, language=language
        )

        self._active_sessions[session_id] = {
            "username": username,
            "started": self._active_sessions.get(session_id, {}).get("started", time.time()),
            "message_count": self._active_sessions.get(session_id, {}).get("message_count", 0) + 1,
            "last_intent": intent,
            "last_language": language,
        }

        return {
            "session_id": session_id,
            "reasoning_chain": chain.to_dict(),
            "context_summary": self.context.get_context_summary(session_id),
            "user_profile_summary": self.long_memory.get_context_summary(username),
            "adaptations": adaptations,
            "intent": intent,
            "language": language,
            "complexity": complexity,
            "reference_resolved": ref_resolved,
            "turn_count": self.short_memory.get_turn_count(session_id),
        }

    def record_response(self, session_id: str, response: str):
        """Enregistre la réponse de l'assistant dans la mémoire."""
        self.short_memory.add(session_id, "assistant", response)
        self.context.update(session_id, "", response)

    def complete_interaction(self, username: str, intent: str,
                             language: str, prompt: str, success: bool):
        """Appelle quand une génération/analyse réussit ou échoue."""
        self.long_memory.record_interaction(
            username, intent, language, prompt, success
        )
        session_id = f"{username}_active"
        self.learner.record_auto_feedback(username, intent, success)

    def submit_feedback(self, username: str, message: str, response: str,
                        rating: int, intent: str):
        """Feedback manuel de l'utilisateur (1-5 étoiles)."""
        self.learner.record_feedback(username, message, response, rating, intent)

    def get_stats(self) -> dict:
        """Stats globales du système cognitif."""
        return {
            "active_sessions": len(self._active_sessions),
            "short_memory_buffers": len(self.short_memory._buffers),
            "long_memory_users": len(self.long_memory._data.get("users", {})),
            "learning": self.learner.get_learning_stats(),
            "context_sessions": len(self.context._sessions),
            "hypothesis": self.hypothesis.get_stats(),
            "counterfactual": self.counterfactual.get_stats(),
        }

    def get_user_cognitive_profile(self, username: str) -> dict:
        """Profil cognitif complet d'un utilisateur."""
        profile = self.long_memory.get_user_profile(username)
        stats = self.learner.get_learning_stats()
        return {
            "username": username,
            "profile": profile,
            "learning_stats": stats,
            "context_summary": self.long_memory.get_context_summary(username),
            "top_issues": self.learner.get_top_issues(),
        }

    def think(self, session_id: str, message: str) -> str:
        """Génère une réflexion interne (pour le debug / transparence)."""
        ctx = self.context.get_full_context(session_id)
        turns = self.short_memory.get_turn_count(session_id)
        parts = [
            f"=== RÉFLEXION COGNITIVE ===",
            f"Session: {session_id} ({turns} tours)",
            f"Message: '{message[:80]}'",
            f"Contexte: {ctx.get('current_topic', 'N/A')} | {ctx.get('current_language', 'N/A')}",
            f"Contraintes: {ctx.get('constraints', [])}",
            f"Références: funcs={ctx.get('mentioned_functions', [])}",
            f"Objectif: {ctx.get('conversation_goal', 'N/A')}",
            f"Hypothèses: {self.hypothesis.get_stats()}",
            f"==========================",
        ]
        return "\n".join(parts)

    def solve_fix(self, code: str, errors: list[dict], language: str) -> dict:
        """Résout des erreurs de code via le moteur d'hypothèses."""
        return self.hypothesis.solve_fix(code, errors, language)

    def solve_generation(self, prompt: str, language: str,
                         context: dict = None) -> dict:
        """Génère et teste plusieurs solutions possibles."""
        return self.hypothesis.solve_generation(prompt, language, context)

    def solve_optimization(self, code: str, language: str) -> dict:
        """Optimise du code via le moteur d'hypothèses."""
        return self.hypothesis.solve_optimization(code, language)

    def get_hypothesis_stats(self) -> dict:
        """Statistiques du moteur d'hypothèses."""
        return self.hypothesis.get_stats()

    def analyze_counterfactual_code(self, code: str, language: str) -> dict:
        """Analyse contre-factuelle du code avec alternatives."""
        return self.counterfactual.analyze_code(code, language)

    def analyze_counterfactual_decision(self, decision: str, context: str,
                                        language: str) -> dict:
        """Analyse contre-factuelle d'une décision."""
        return self.counterfactual.analyze_decision(decision, context, language)

    def explore_counterfactual_paths(self, code: str, decisions: list[dict],
                                     language: str) -> dict:
        """Explore les chemins alternatifs."""
        return self.counterfactual.explore_paths(code, decisions, language)

    def get_counterfactual_stats(self) -> dict:
        """Statistiques du générateur contre-factuel."""
        return self.counterfactual.get_stats()

    def _parse_field(self, text: str, field: str) -> str:
        for part in text.split(","):
            part = part.strip()
            if part.startswith(f"{field}="):
                return part.split("=", 1)[1].strip()
        return ""


cognitive = CognitiveArchitecture()
