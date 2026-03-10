"""Pytest tests for WordCache class."""
import pytest
from collections import OrderedDict
from backend.dictionary.cache import WordCache


class TestWordCacheInit:
    """Test WordCache initialization."""

    def test_cache_initialization_default_max_size(self):
        """Test cache initializes with default max_size of 1000."""
        cache = WordCache()
        assert cache._max_size == 1000
        assert len(cache._cache) == 0
        assert isinstance(cache._cache, OrderedDict)

    def test_cache_initialization_custom_max_size(self):
        """Test cache initializes with custom max_size."""
        cache = WordCache(max_size=100)
        assert cache._max_size == 100
        assert len(cache._cache) == 0


class TestWordCacheSet:
    """Test WordCache set() method."""

    def test_set_single_item(self):
        """Test setting a single item in cache."""
        cache = WordCache()
        result = {"valid": True, "word": "apple"}
        cache.set("apple", result)
        assert len(cache._cache) == 1
        assert cache._cache["apple"] == result

    def test_set_multiple_items(self):
        """Test setting multiple items in cache."""
        cache = WordCache()
        result1 = {"valid": True}
        result2 = {"valid": False}
        result3 = {"valid": True}
        cache.set("apple", result1)
        cache.set("banana", result2)
        cache.set("cherry", result3)
        assert len(cache._cache) == 3
        assert cache._cache["apple"] == result1
        assert cache._cache["banana"] == result2
        assert cache._cache["cherry"] == result3

    def test_set_update_existing_item(self):
        """Test updating an existing item in cache."""
        cache = WordCache()
        result1 = {"valid": True}
        result2 = {"valid": False}
        cache.set("apple", result1)
        cache.set("apple", result2)
        assert len(cache._cache) == 1
        assert cache._cache["apple"] == result2

    def test_set_preserves_insertion_order(self):
        """Test that items maintain insertion order."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        keys = list(cache._cache.keys())
        assert keys == ["apple", "banana", "cherry"]


class TestWordCacheGet:
    """Test WordCache get() method."""

    def test_get_existing_item(self):
        """Test getting an existing item from cache."""
        cache = WordCache()
        result = {"valid": True, "word": "apple"}
        cache.set("apple", result)
        retrieved = cache.get("apple")
        assert retrieved == result

    def test_get_nonexistent_item(self):
        """Test getting a non-existent item returns None."""
        cache = WordCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_get_from_empty_cache(self):
        """Test getting from empty cache returns None."""
        cache = WordCache()
        result = cache.get("apple")
        assert result is None

    def test_get_moves_item_to_end(self):
        """Test that get() moves accessed item to end (most recently used)."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        # Access banana - should move to end
        cache.get("banana")
        keys = list(cache._cache.keys())
        assert keys[-1] == "banana"
        assert keys == ["apple", "cherry", "banana"]

    def test_get_multiple_accesses_maintain_order(self):
        """Test multiple get accesses update item order correctly."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        cache.set("date", {"valid": True})
        # Access in specific order
        cache.get("apple")
        cache.get("cherry")
        keys = list(cache._cache.keys())
        assert keys[-2:] == ["apple", "cherry"]


class TestWordCacheLRUEviction:
    """Test LRU eviction when max_size exceeded."""

    def test_lru_eviction_on_max_size_exceeded(self):
        """Test that oldest item is evicted when max_size is exceeded."""
        cache = WordCache(max_size=3)
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        assert len(cache._cache) == 3
        # Add fourth item - should evict "apple" (oldest)
        cache.set("date", {"valid": True})
        assert len(cache._cache) == 3
        assert "apple" not in cache._cache
        assert "banana" in cache._cache
        assert "cherry" in cache._cache
        assert "date" in cache._cache

    def test_lru_eviction_multiple_times(self):
        """Test multiple LRU evictions work correctly."""
        cache = WordCache(max_size=2)
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})  # Evicts apple
        cache.set("date", {"valid": True})    # Evicts banana
        assert len(cache._cache) == 2
        assert "cherry" in cache._cache
        assert "date" in cache._cache
        assert "apple" not in cache._cache
        assert "banana" not in cache._cache

    def test_lru_respects_access_order(self):
        """Test LRU eviction respects access recency from get()."""
        cache = WordCache(max_size=3)
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        # Access banana - moves to end
        cache.get("banana")
        # Add new item - should evict apple (now oldest)
        cache.set("date", {"valid": True})
        assert len(cache._cache) == 3
        assert "apple" not in cache._cache
        assert "banana" in cache._cache
        assert "cherry" in cache._cache
        assert "date" in cache._cache

    def test_lru_respects_set_order_update(self):
        """Test LRU respects order when updating existing items."""
        cache = WordCache(max_size=3)
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        # Update banana - moves to end
        cache.set("banana", {"valid": True, "updated": True})
        # Add new item - should evict apple (now oldest)
        cache.set("date", {"valid": True})
        assert len(cache._cache) == 3
        assert "apple" not in cache._cache
        assert "banana" in cache._cache
        assert "cherry" in cache._cache
        assert "date" in cache._cache

    def test_lru_eviction_with_max_size_one(self):
        """Test LRU eviction with max_size of 1."""
        cache = WordCache(max_size=1)
        cache.set("apple", {"valid": True})
        assert len(cache._cache) == 1
        cache.set("banana", {"valid": False})
        assert len(cache._cache) == 1
        assert "apple" not in cache._cache
        assert "banana" in cache._cache


class TestWordCacheMoveToEnd:
    """Test move-to-end behavior on access."""

    def test_move_to_end_on_get(self):
        """Test that get() calls move_to_end internally."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        original_keys = list(cache._cache.keys())
        assert original_keys == ["apple", "banana", "cherry"]
        # Get banana
        cache.get("banana")
        new_keys = list(cache._cache.keys())
        assert new_keys == ["apple", "cherry", "banana"]
        assert new_keys[-1] == "banana"

    def test_move_to_end_on_set_update(self):
        """Test that set() on existing key moves item to end."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        original_keys = list(cache._cache.keys())
        assert original_keys == ["apple", "banana", "cherry"]
        # Update banana
        cache.set("banana", {"valid": True, "updated": True})
        new_keys = list(cache._cache.keys())
        assert new_keys == ["apple", "cherry", "banana"]
        assert new_keys[-1] == "banana"

    def test_sequential_get_calls_maintain_order(self):
        """Test that sequential get calls maintain correct LRU order."""
        cache = WordCache(max_size=5)
        words = ["apple", "banana", "cherry", "date", "elderberry"]
        for word in words:
            cache.set(word, {"word": word})
        # Access in order: apple, cherry, banana
        cache.get("apple")
        cache.get("cherry")
        cache.get("banana")
        keys = list(cache._cache.keys())
        # Expected: date, elderberry, apple, cherry, banana
        assert keys[-3:] == ["apple", "cherry", "banana"]


class TestWordCacheClear:
    """Test WordCache clear() method."""

    def test_clear_empty_cache(self):
        """Test clearing an already empty cache."""
        cache = WordCache()
        cache.clear()
        assert len(cache._cache) == 0

    def test_clear_single_item(self):
        """Test clearing cache with single item."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        assert len(cache._cache) == 1
        cache.clear()
        assert len(cache._cache) == 0

    def test_clear_multiple_items(self):
        """Test clearing cache with multiple items."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.set("cherry", {"valid": True})
        assert len(cache._cache) == 3
        cache.clear()
        assert len(cache._cache) == 0

    def test_cache_usable_after_clear(self):
        """Test that cache can be used normally after clearing."""
        cache = WordCache()
        cache.set("apple", {"valid": True})
        cache.set("banana", {"valid": False})
        cache.clear()
        assert cache.get("apple") is None
        cache.set("cherry", {"valid": True})
        assert cache.get("cherry") == {"valid": True}
        assert len(cache._cache) == 1

    def test_clear_resets_max_size(self):
        """Test that max_size is preserved after clear."""
        cache = WordCache(max_size=5)
        cache.set("apple", {"valid": True})
        cache.clear()
        assert cache._max_size == 5
        for i in range(10):
            cache.set(f"word_{i}", {"valid": True})
        assert len(cache._cache) == 5


class TestWordCacheIntegration:
    """Integration tests for WordCache."""

    def test_typical_usage_workflow(self):
        """Test typical usage: set, get, update flow."""
        cache = WordCache(max_size=100)
        # Set initial value
        cache.set("hello", {"valid": True, "lang": "en"})
        # Get it
        result = cache.get("hello")
        assert result == {"valid": True, "lang": "en"}
        # Update it
        cache.set("hello", {"valid": True, "lang": "en", "freq": 5})
        # Get updated value
        result = cache.get("hello")
        assert result == {"valid": True, "lang": "en", "freq": 5}

    def test_cache_with_complex_result_dicts(self):
        """Test cache works with complex result dictionaries."""
        cache = WordCache()
        complex_result = {
            "valid": True,
            "word": "exemplify",
            "lang": "en",
            "definitions": [
                {"pos": "verb", "meaning": "to be a typical example"},
                {"pos": "verb", "meaning": "to show by example"},
            ],
            "synonyms": ["demonstrate", "illustrate", "show"],
            "metadata": {"difficulty": "advanced", "frequency": "rare"},
        }
        cache.set("exemplify", complex_result)
        retrieved = cache.get("exemplify")
        assert retrieved == complex_result

    def test_fifo_behavior_without_access(self):
        """Test pure FIFO (First-In-First-Out) behavior without access."""
        cache = WordCache(max_size=3)
        cache.set("first", {"order": 1})
        cache.set("second", {"order": 2})
        cache.set("third", {"order": 3})
        assert list(cache._cache.keys()) == ["first", "second", "third"]
        # Add fourth - first should be evicted
        cache.set("fourth", {"order": 4})
        assert list(cache._cache.keys()) == ["second", "third", "fourth"]
        assert "first" not in cache._cache

    def test_lru_behavior_with_frequent_access(self):
        """Test LRU behavior with frequently accessed items."""
        cache = WordCache(max_size=3)
        cache.set("a", {"id": "a"})
        cache.set("b", {"id": "b"})
        cache.set("c", {"id": "c"})
        # Access 'a' frequently
        for _ in range(5):
            cache.get("a")
        # Add new item - 'b' should be evicted (least recently used)
        cache.set("d", {"id": "d"})
        assert "a" in cache._cache
        assert "b" not in cache._cache
        assert "c" in cache._cache
        assert "d" in cache._cache
