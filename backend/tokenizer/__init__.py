"""YELMON Dev X - Tokenizer de code (approximation de tokens)."""

import re

_WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+\.\d+|\d+|[\+\-\*/%=<>!&|^~]+|[{}()\[\];,.:\"" "'`@#]")


def count_tokens(text: str) -> int:
    """Compte approximativement les tokens d'un texte/code."""
    if not text:
        return 0
    tokens = _WORD_RE.findall(text)
    return len(tokens)


def tokenize(text: str) -> list:
    """Retourne la liste des tokens."""
    if not text:
        return []
    return _WORD_RE.findall(text)
