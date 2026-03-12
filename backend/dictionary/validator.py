"""Word validation service using local dictionary (26만 단어)."""

from enum import Enum
from .cache import WordCache
from .fallback_dict import is_known_noun


class ValidationReason(Enum):
    VALID = "VALID"
    NOT_IN_DICT = "NOT_IN_DICT"


class WordValidator:
    """Validates Korean words using local dictionary only."""

    def __init__(self, api_client=None, cache=None):
        self._cache: WordCache = cache or WordCache()

    async def validate(self, word: str) -> dict:
        cached = self._cache.get(word)
        if cached is not None:
            return cached

        if is_known_noun(word):
            result = {
                "valid": True,
                "is_noun": True,
                "reason": ValidationReason.VALID.value,
                "message": f"'{word}'은(는) 유효한 명사입니다.",
            }
        else:
            result = {
                "valid": False,
                "is_noun": False,
                "reason": ValidationReason.NOT_IN_DICT.value,
                "message": "사전에 없는 단어",
            }

        self._cache.set(word, result)
        return result
