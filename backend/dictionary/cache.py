"""Word cache for storing API responses."""

from collections import OrderedDict


class WordCache:
    """Simple LRU cache for word validation results."""

    def __init__(self, max_size: int = 1000):
        """Initialize cache with max size.

        Args:
            max_size: Maximum number of cached items (default: 1000)
        """
        self._cache: OrderedDict = OrderedDict()
        self._max_size: int = max_size

    def get(self, word: str) -> dict | None:
        """Get cached result for word.

        Args:
            word: The word to look up

        Returns:
            Cached result dict if found, None otherwise
        """
        if word in self._cache:
            # Move to end to mark as recently used
            self._cache.move_to_end(word)
            return self._cache[word]
        return None

    def set(self, word: str, result: dict) -> None:
        """Set cache value for word, evicting oldest if full.

        Args:
            word: The word key
            result: The result dict to cache
        """
        if word in self._cache:
            # Update existing entry
            self._cache.move_to_end(word)
            self._cache[word] = result
        else:
            # Add new entry
            if len(self._cache) >= self._max_size:
                # Remove oldest (first) item
                self._cache.popitem(last=False)
            self._cache[word] = result

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
