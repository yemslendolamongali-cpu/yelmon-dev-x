"""YELMON Dev X - Moteur RAG (recherche sémantique TF-IDF + cosine)."""

import re
from collections import Counter

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False


def _tokens(text: str):
    return re.findall(r"[a-z0-9_]+", (text or "").lower())


class RAGEngine:
    """Indexe des extraits de code et recherche par similarité sémantique."""

    def __init__(self):
        self.documents = []
        self.metas = []
        self._vectorizer = None
        self._matrix = None
        self._dirty = True

    def index(self, snippets):
        """Ajoute des snippets à l'index. Chaque snippet: {code, language, title}."""
        if not snippets:
            return
        for s in snippets:
            code = s.get("code", "")
            if not code.strip():
                continue
            self.documents.append(code)
            self.metas.append({
                "title": s.get("title", ""),
                "language": s.get("language", ""),
            })
        self._dirty = True
        self._rebuild()

    def _rebuild(self):
        if not self.documents:
            return
        if HAS_SKLEARN:
            try:
                self._vectorizer = TfidfVectorizer(token_pattern=r"[a-z0-9_]+", ngram_range=(1, 2))
                self._matrix = self._vectorizer.fit_transform(self.documents)
                self._dirty = False
                return
            except Exception:
                pass
        self._dirty = False

    def search(self, query: str, top_k: int = 5) -> list:
        """Recherche les snippets les plus pertinents."""
        if not query.strip() or not self.documents:
            return []
        self._ensure_index()
        if HAS_SKLEARN and self._vectorizer is not None and self._matrix is not None:
            try:
                q = self._vectorizer.transform([query])
                scores = cosine_similarity(q, self._matrix).flatten()
                best = scores.argsort()[::-1][:top_k]
                return [
                    {"score": round(float(scores[i]), 4), "code": self.documents[i],
                     "title": self.metas[i]["title"], "language": self.metas[i]["language"]}
                    for i in best if scores[i] > 0
                ]
            except Exception:
                pass
        # Fallback : score par chevauchement de tokens
        q = Counter(_tokens(query))
        results = []
        for idx, doc in enumerate(self.documents):
            d = Counter(_tokens(doc))
            overlap = sum((q & d).values())
            if overlap > 0:
                results.append({
                    "score": round(overlap / (len(q) or 1), 4),
                    "code": doc, "title": self.metas[idx]["title"],
                    "language": self.metas[idx]["language"],
                })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    def _ensure_index(self):
        if self._dirty:
            self._rebuild()
