"""Fallback local dictionary for when the API is unavailable.

Uses the open Korean dictionary dataset (우리말샘) via a bundled noun list.
If the noun list file doesn't exist, falls back to a small built-in set.
"""

import os

_NOUNS: set[str] | None = None
_DICT_PATH = os.path.join(os.path.dirname(__file__), "nouns.txt")


def _load() -> set[str]:
    global _NOUNS
    if _NOUNS is not None:
        return _NOUNS
    _NOUNS = set()
    if os.path.exists(_DICT_PATH):
        with open(_DICT_PATH, encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    _NOUNS.add(word)
    print(f"[Fallback Dict] loaded {len(_NOUNS)} nouns")
    return _NOUNS


def is_known_noun(word: str) -> bool:
    """Check if word is in the local noun list."""
    nouns = _load()
    return word in nouns
