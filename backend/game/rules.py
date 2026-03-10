from typing import List
from backend.utils.korean import (
    is_valid_chain,
    get_initial_jamo,
    apply_dueum,
    get_last_char,
)


class GameRules:
    """Class for managing Korean word chain game rules."""

    MIN_WORD_LENGTH = 2

    def validate_chain(self, prev_word: str, next_word: str) -> bool:
        """Validate if next_word can follow prev_word in a word chain."""
        if not prev_word or not next_word:
            return False

        return is_valid_chain(prev_word, next_word)

    def is_word_used(self, word: str, used_words: List[str]) -> bool:
        """Check if a word has already been used in the game."""
        return word.lower() in [w.lower() for w in used_words]

    def is_valid_length(self, word: str) -> bool:
        """Check if word has minimum required length."""
        return len(word) >= self.MIN_WORD_LENGTH

    def get_target_chars(self, word: str) -> List[str]:
        """Get possible starting characters for next word considering dueum rules."""
        if not word:
            return []

        last_char = get_last_char(word)
        if not last_char:
            return []

        # Get initial jamo of the last character
        initial_jamo = get_initial_jamo(last_char)
        if not initial_jamo:
            return []

        # Apply dueum rules
        dueum_variations = apply_dueum(last_char)

        # Collect all possible initial jamo characters
        target_chars = []
        for variation in dueum_variations:
            variation_jamo = get_initial_jamo(variation)
            if variation_jamo and variation_jamo not in target_chars:
                target_chars.append(variation_jamo)

        return target_chars if target_chars else [initial_jamo]
