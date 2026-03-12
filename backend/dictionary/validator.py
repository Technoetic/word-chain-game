"""Word validation service."""

from enum import Enum

from .cache import WordCache
from .korean_api_client import KoreanAPIClient
from .fallback_dict import is_known_noun


class ValidationReason(Enum):
    """Validation result reasons."""

    VALID = "VALID"
    NOT_IN_DICT = "NOT_IN_DICT"
    NOT_A_NOUN = "NOT_A_NOUN"
    API_ERROR = "API_ERROR"


class WordValidator:
    """Validates Korean words using local dictionary + API fallback."""

    def __init__(self, api_client: KoreanAPIClient, cache: WordCache):
        self._api_client: KoreanAPIClient = api_client
        self._cache: WordCache = cache

    async def validate(self, word: str) -> dict:
        """Validate if word is a valid Korean noun.

        Priority: cache → local dict (26만 단어) → API fallback
        """
        # Check cache first
        cached = self._cache.get(word)
        if cached is not None:
            print(f"[Validator] '{word}' → cache hit: {cached['reason']}")
            return cached

        # Local dictionary first (instant, no network)
        if is_known_noun(word):
            result = {
                "valid": True,
                "is_noun": True,
                "reason": ValidationReason.VALID.value,
                "message": f"'{word}'은(는) 유효한 명사입니다.",
            }
            self._cache.set(word, result)
            print(f"[Validator] '{word}' → local dict: VALID")
            return result

        print(f"[Validator] '{word}' → not in local dict, trying API...")

        # Not in local dict → try API as fallback
        try:
            api_response = await self._api_client.search(word)
            if api_response and "error" not in api_response:
                result = self._parse_api_response(word, api_response)
                self._cache.set(word, result)
                print(f"[Validator] '{word}' → API: {result['reason']}")
                return result
            else:
                print(f"[Validator] '{word}' → API error: {api_response}")
        except Exception as e:
            print(f"[Validator] '{word}' → API exception: {e}")

        # Neither local nor API found it
        result = {
            "valid": False,
            "is_noun": False,
            "reason": ValidationReason.NOT_IN_DICT.value,
            "message": "사전에 없는 단어",
        }
        self._cache.set(word, result)
        print(f"[Validator] '{word}' → NOT_IN_DICT (final)")
        return result

    def _parse_api_response(self, word: str, api_response: dict) -> dict:
        """Parse API response and determine validity."""
        try:
            channel = api_response.get("channel")
            if not channel:
                return {
                    "valid": False,
                    "is_noun": False,
                    "reason": ValidationReason.NOT_IN_DICT.value,
                    "message": "사전에 없는 단어",
                }

            total = channel.get("total", 0)
            if total == 0 or "item" not in channel:
                return {
                    "valid": False,
                    "is_noun": False,
                    "reason": ValidationReason.NOT_IN_DICT.value,
                    "message": "사전에 없는 단어",
                }

            items = channel["item"]
            if not isinstance(items, list):
                items = [items]

            for item in items:
                if isinstance(item, dict):
                    pos = item.get("pos", "")
                    if pos == "명사" or "명사" in str(pos):
                        return {
                            "valid": True,
                            "is_noun": True,
                            "reason": ValidationReason.VALID.value,
                            "message": f"'{word}'은(는) 유효한 명사입니다.",
                        }

            return {
                "valid": False,
                "is_noun": False,
                "reason": ValidationReason.NOT_A_NOUN.value,
                "message": "명사가 아닙니다",
            }

        except (KeyError, TypeError, IndexError):
            return {
                "valid": False,
                "is_noun": False,
                "reason": ValidationReason.NOT_IN_DICT.value,
                "message": "사전에 없는 단어",
            }
