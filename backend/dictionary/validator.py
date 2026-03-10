"""Word validation service."""

from enum import Enum

from .cache import WordCache
from .korean_api_client import KoreanAPIClient


class ValidationReason(Enum):
    """Validation result reasons."""

    VALID = "VALID"
    NOT_IN_DICT = "NOT_IN_DICT"
    NOT_A_NOUN = "NOT_A_NOUN"
    API_ERROR = "API_ERROR"


class WordValidator:
    """Validates Korean words using dictionary API and cache."""

    def __init__(self, api_client: KoreanAPIClient, cache: WordCache):
        """Initialize validator.

        Args:
            api_client: KoreanAPIClient instance
            cache: WordCache instance
        """
        self._api_client: KoreanAPIClient = api_client
        self._cache: WordCache = cache

    async def validate(self, word: str) -> dict:
        """Validate if word is a valid Korean noun.

        Args:
            word: The word to validate

        Returns:
            Dict with keys:
                - valid: bool - whether word is valid
                - is_noun: bool - whether word is a noun
                - reason: str - validation reason (VALID, NOT_IN_DICT, NOT_A_NOUN, API_ERROR)
                - message: str - human readable message
        """
        # Check cache first
        cached = self._cache.get(word)
        if cached is not None:
            return cached

        # Call API
        api_response = await self._api_client.search(word)

        # Handle empty/None response (API returns empty body for unknown words)
        if api_response is None:
            api_response = {}

        # Parse response
        result = self._parse_response(word, api_response)

        # Cache result
        self._cache.set(word, result)

        return result

    def _parse_response(self, word: str, api_response: dict) -> dict:
        """Parse API response and determine validity.

        Args:
            word: The word that was searched
            api_response: Raw response from API

        Returns:
            Validation result dict
        """
        # Check for API error - allow word on API failure for playability
        if "error" in api_response:
            return {
                "valid": True,
                "is_noun": True,
                "reason": ValidationReason.API_ERROR.value,
                "message": f"사전 확인 불가 (통과 처리)",
            }

        # 표준국어대사전 API response format:
        # {"channel": {"total": N, "item": [{"word": "...", "pos": "명사", ...}]}}
        try:
            channel = api_response.get("channel")
            if not channel:
                return {
                    "valid": False,
                    "is_noun": False,
                    "reason": ValidationReason.NOT_IN_DICT.value,
                    "message": f"표준국어대사전에 없는 단어",
                }

            total = channel.get("total", 0)
            if total == 0 or "item" not in channel:
                return {
                    "valid": False,
                    "is_noun": False,
                    "reason": ValidationReason.NOT_IN_DICT.value,
                    "message": f"표준국어대사전에 없는 단어",
                }

            items = channel["item"]
            if not isinstance(items, list):
                items = [items]

            # Check if any entry is a noun (명사)
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

            # Word exists but is not a noun
            return {
                "valid": False,
                "is_noun": False,
                "reason": ValidationReason.NOT_A_NOUN.value,
                "message": f"명사가 아닙니다",
            }

        except (KeyError, TypeError, IndexError) as e:
            return {
                "valid": False,
                "is_noun": False,
                "reason": ValidationReason.API_ERROR.value,
                "message": f"API 응답 파싱 오류: {str(e)}",
            }
