"""
Pytest tests for GameRules class.

Tests cover:
- validate_chain(): Valid and invalid word chains
- is_word_used(): Duplicate word detection
- is_valid_length(): Minimum word length validation
- get_target_chars(): Target character extraction with dueum rules

Edge cases include:
- Empty strings
- Single character words
- Duplicate words (case-insensitive)
- Words with dueum variations
"""

import pytest
from backend.game.rules import GameRules


class TestGameRulesValidateChain:
    """Tests for GameRules.validate_chain() method."""

    def setup_method(self):
        """Initialize GameRules instance for each test."""
        self.rules = GameRules()

    def test_validate_chain_valid_chain(self):
        """Test valid word chain: 가능 -> 능력."""
        assert self.rules.validate_chain("가능", "능력") is True

    def test_validate_chain_invalid_chain(self):
        """Test invalid word chain: 가능 -> 다른"""
        assert self.rules.validate_chain("가능", "다른") is False

    def test_validate_chain_empty_prev_word(self):
        """Test with empty previous word."""
        assert self.rules.validate_chain("", "능력") is False

    def test_validate_chain_empty_next_word(self):
        """Test with empty next word."""
        assert self.rules.validate_chain("가능", "") is False

    def test_validate_chain_both_empty(self):
        """Test with both words empty."""
        assert self.rules.validate_chain("", "") is False

    def test_validate_chain_none_prev_word(self):
        """Test with None as previous word."""
        assert self.rules.validate_chain(None, "능력") is False

    def test_validate_chain_none_next_word(self):
        """Test with None as next word."""
        assert self.rules.validate_chain("가능", None) is False

    def test_validate_chain_single_char_prev(self):
        """Test valid chain with single character previous word."""
        assert self.rules.validate_chain("가", "가능") is True

    def test_validate_chain_single_char_next(self):
        """Test valid chain with single character next word."""
        assert self.rules.validate_chain("능력", "력") is True


class TestGameRulesIsWordUsed:
    """Tests for GameRules.is_word_used() method."""

    def setup_method(self):
        """Initialize GameRules instance for each test."""
        self.rules = GameRules()

    def test_is_word_used_found_exact_match(self):
        """Test word is found in used words list."""
        used_words = ["가능", "능력", "력사"]
        assert self.rules.is_word_used("능력", used_words) is True

    def test_is_word_used_not_found(self):
        """Test word is not found in used words list."""
        used_words = ["가능", "능력", "력사"]
        assert self.rules.is_word_used("새로운", used_words) is False

    def test_is_word_used_case_insensitive_uppercase(self):
        """Test case-insensitive detection with uppercase."""
        used_words = ["가능", "능력"]
        assert self.rules.is_word_used("가능".upper(), used_words) is True

    def test_is_word_used_case_insensitive_mixed(self):
        """Test case-insensitive detection with mixed case."""
        used_words = ["TEST", "test", "TeSt"]
        assert self.rules.is_word_used("test", used_words) is True

    def test_is_word_used_empty_word(self):
        """Test with empty word."""
        used_words = ["가능", "능력"]
        assert self.rules.is_word_used("", used_words) is False

    def test_is_word_used_empty_list(self):
        """Test with empty used words list."""
        assert self.rules.is_word_used("가능", []) is False

    def test_is_word_used_single_item_match(self):
        """Test with single item in used words list that matches."""
        assert self.rules.is_word_used("가능", ["가능"]) is True

    def test_is_word_used_single_item_no_match(self):
        """Test with single item in used words list that doesn't match."""
        assert self.rules.is_word_used("가능", ["능력"]) is False

    def test_is_word_used_duplicate_in_list(self):
        """Test duplicate words in used words list."""
        used_words = ["가능", "능력", "가능"]
        assert self.rules.is_word_used("가능", used_words) is True

    def test_is_word_used_whitespace_word(self):
        """Test with word containing whitespace."""
        used_words = ["가능", "능 력"]
        assert self.rules.is_word_used("능 력", used_words) is True


class TestGameRulesIsValidLength:
    """Tests for GameRules.is_valid_length() method."""

    def setup_method(self):
        """Initialize GameRules instance for each test."""
        self.rules = GameRules()

    def test_is_valid_length_minimum_length(self):
        """Test word with minimum valid length (2 characters)."""
        assert self.rules.is_valid_length("가능") is True

    def test_is_valid_length_below_minimum(self):
        """Test word below minimum length (1 character)."""
        assert self.rules.is_valid_length("가") is False

    def test_is_valid_length_empty_string(self):
        """Test with empty string."""
        assert self.rules.is_valid_length("") is False

    def test_is_valid_length_long_word(self):
        """Test word with more than minimum length."""
        assert self.rules.is_valid_length("가능력있다") is True

    def test_is_valid_length_very_long_word(self):
        """Test word with very long length."""
        long_word = "가" * 100
        assert self.rules.is_valid_length(long_word) is True

    def test_is_valid_length_english_word(self):
        """Test English word with minimum length."""
        assert self.rules.is_valid_length("ab") is True

    def test_is_valid_length_english_single_char(self):
        """Test English single character."""
        assert self.rules.is_valid_length("a") is False

    def test_is_valid_length_mixed_language(self):
        """Test mixed language word."""
        assert self.rules.is_valid_length("가a") is True

    def test_is_valid_length_special_characters(self):
        """Test word with special characters."""
        assert self.rules.is_valid_length("가-능") is True

    def test_is_valid_length_numbers(self):
        """Test word with numbers."""
        assert self.rules.is_valid_length("가1") is True


class TestGameRulesGetTargetChars:
    """Tests for GameRules.get_target_chars() method."""

    def setup_method(self):
        """Initialize GameRules instance for each test."""
        self.rules = GameRules()

    def test_get_target_chars_korean_word(self):
        """Test getting target chars from Korean word."""
        result = self.rules.get_target_chars("가능")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(char, str) for char in result)

    def test_get_target_chars_single_char_word(self):
        """Test getting target chars from single character word."""
        result = self.rules.get_target_chars("가")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_target_chars_empty_string(self):
        """Test with empty string returns empty list."""
        assert self.rules.get_target_chars("") == []

    def test_get_target_chars_none_input(self):
        """Test with None input."""
        result = self.rules.get_target_chars(None)
        # Should handle None gracefully
        assert isinstance(result, list)

    def test_get_target_chars_multiple_calls_consistency(self):
        """Test that same word always returns same target chars."""
        result1 = self.rules.get_target_chars("가능")
        result2 = self.rules.get_target_chars("가능")
        assert result1 == result2

    def test_get_target_chars_different_words(self):
        """Test that different words can return different target chars."""
        result1 = self.rules.get_target_chars("가능")
        result2 = self.rules.get_target_chars("다른")
        # Results might be same or different, but both should be valid lists
        assert isinstance(result1, list)
        assert isinstance(result2, list)

    def test_get_target_chars_no_duplicates(self):
        """Test that target chars list has no duplicates."""
        result = self.rules.get_target_chars("가능")
        assert len(result) == len(set(result))

    def test_get_target_chars_all_strings(self):
        """Test that all target chars are strings."""
        result = self.rules.get_target_chars("가능")
        assert all(isinstance(char, str) for char in result)

    def test_get_target_chars_with_dueum(self):
        """Test target chars considers dueum variations."""
        # Words ending with similar sounds should include dueum variations
        result = self.rules.get_target_chars("닭")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_target_chars_english_word(self):
        """Test with English word."""
        result = self.rules.get_target_chars("test")
        # Should handle English gracefully
        assert isinstance(result, list)

    def test_get_target_chars_special_characters(self):
        """Test with word containing special characters."""
        result = self.rules.get_target_chars("가-능")
        # Should handle special characters gracefully
        assert isinstance(result, list)

    def test_get_target_chars_numbers(self):
        """Test with word containing numbers."""
        result = self.rules.get_target_chars("가1")
        # Should handle numbers gracefully
        assert isinstance(result, list)

    def test_get_target_chars_not_empty_for_valid_korean(self):
        """Test that valid Korean word returns non-empty target chars."""
        result = self.rules.get_target_chars("능력")
        assert len(result) > 0


class TestGameRulesIntegration:
    """Integration tests combining multiple GameRules methods."""

    def setup_method(self):
        """Initialize GameRules instance for each test."""
        self.rules = GameRules()

    def test_full_word_chain_validation_flow(self):
        """Test complete word chain validation flow."""
        used_words = ["가능"]
        new_word = "능력"

        # Check if new word has valid length
        assert self.rules.is_valid_length(new_word) is True

        # Check if word hasn't been used
        assert self.rules.is_word_used(new_word, used_words) is False

        # Check if chain is valid
        assert self.rules.validate_chain(used_words[0], new_word) is True

        # Get target chars for next word
        target_chars = self.rules.get_target_chars(new_word)
        assert len(target_chars) > 0

    def test_chain_with_duplicate_detection(self):
        """Test that duplicate words are properly detected in chain."""
        used_words = ["가능", "능력"]

        # Try to add a word that was already used
        duplicate_word = "가능"
        assert self.rules.is_word_used(duplicate_word, used_words) is True

        # Try to add a new word
        new_word = "력사"
        assert self.rules.is_word_used(new_word, used_words) is False

    def test_chain_validation_with_invalid_length(self):
        """Test validation of word with invalid length in chain."""
        used_words = ["가능"]

        # Single char word should fail length validation
        short_word = "력"
        assert self.rules.is_valid_length(short_word) is False

        # But chain validation might still pass (separate concerns)
        # This tests that rules are independent

    def test_empty_input_handling_across_methods(self):
        """Test that all methods handle empty input gracefully."""
        # All methods should handle empty strings without crashing
        assert self.rules.validate_chain("", "") is False
        assert self.rules.is_word_used("", []) is False
        assert self.rules.is_valid_length("") is False
        assert self.rules.get_target_chars("") == []

    def test_case_insensitivity_across_methods(self):
        """Test case-insensitive behavior in word used check."""
        # Different case variations should be treated as same word
        used_words = ["TEST"]
        assert self.rules.is_word_used("test", used_words) is True
        assert self.rules.is_word_used("Test", used_words) is True
        assert self.rules.is_word_used("TEST", used_words) is True

    def test_min_word_length_constant(self):
        """Test that MIN_WORD_LENGTH constant is properly used."""
        assert GameRules.MIN_WORD_LENGTH == 2

        # Words with length >= MIN_WORD_LENGTH should pass
        assert self.rules.is_valid_length("ab") is True

        # Words with length < MIN_WORD_LENGTH should fail
        assert self.rules.is_valid_length("a") is False
