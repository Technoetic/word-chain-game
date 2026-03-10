"""Korean dictionary API client using 국립국어원 API."""

import aiohttp
import json
from typing import Optional


class KoreanAPIClient:
    """Client for Korean dictionary API from 국립국어원 (National Institute of Korean Language)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://stdict.korean.go.kr/api/search.do",
    ):
        """Initialize API client.

        Args:
            api_key: API key for 국립국어원 API
            base_url: Base URL for the API (default: official endpoint)
        """
        self._api_key: str = api_key
        self._base_url: str = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session (lazy initialization).

        Returns:
            aiohttp.ClientSession instance
        """
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def search(self, word: str) -> dict:
        """Search for word in Korean dictionary.

        Args:
            word: Word to search for

        Returns:
            Parsed JSON response from API
        """
        session = await self._get_session()

        params = {
            "key": self._api_key,
            "q": word,
            "req_type": "json",
            "method": "exact",
        }

        try:
            async with session.get(
                self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    return data
                else:
                    return {"error": f"API returned status {response.status}"}
        except aiohttp.ClientError as e:
            return {"error": f"API request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse API response: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def close(self) -> None:
        """Close aiohttp session."""
        if self._session is not None:
            await self._session.close()
            self._session = None
