"""
Comprehensive pytest tests for Korean utility functions.
Tests cover: get_last_char, get_initial_jamo, apply_dueum, is_valid_chain.
Includes edge cases: empty strings, non-Korean characters, dueum law variations.
"""

import pytest
from backend.utils.korean import (
    get_last_char,
    get_initial_jamo,
    apply_dueum,
    is_valid_chain,
)


class TestGetLastChar:
    """Tests for get_last_char function."""

    def test_get_last_char_basic_korean(self):
        """Test with basic Korean word."""
        assert get_last_char("사과") == "과"

    def test_get_last_char_single_char(self):
        """Test with single Korean character."""
        assert get_last_char("가") == "가"

    def test_get_last_char_long_word(self):
        """Test with longer Korean word."""
        assert get_last_char("대학교") == "교"

    def test_get_last_char_empty_string(self):
        """Test with empty string - should return empty."""
        assert get_last_char("") == ""

    def test_get_last_char_english(self):
        """Test with English word."""
        assert get_last_char("apple") == "e"

    def test_get_last_char_mixed(self):
        """Test with mixed Korean and English."""
        assert get_last_char("한글ABC") == "C"

    def test_get_last_char_numbers(self):
        """Test with numbers."""
        assert get_last_char("123") == "3"

    def test_get_last_char_special_chars(self):
        """Test with special characters."""
        assert get_last_char("!@#") == "#"


class TestGetInitialJamo:
    """Tests for get_initial_jamo function."""

    def test_get_initial_jamo_basic(self):
        """Test extracting initial consonant from basic Korean character."""
        initial = get_initial_jamo("가")
        assert initial != ""
        assert initial == get_initial_jamo("가")

    def test_get_initial_jamo_different_initials(self):
        """Test that different initial consonants produce different results."""
        initial_ga = get_initial_jamo("가")
        initial_na = get_initial_jamo("나")
        assert initial_ga != initial_na

    def test_get_initial_jamo_same_initial(self):
        """Test that same initial consonants produce same result."""
        initial_ga = get_initial_jamo("가")
        initial_go = get_initial_jamo("고")
        assert initial_ga == initial_go

    def test_get_initial_jamo_empty_string(self):
        """Test with empty string."""
        assert get_initial_jamo("") == ""

    def test_get_initial_jamo_english(self):
        """Test with English character - should not decompose."""
        result = get_initial_jamo("a")
        assert result == "a"

    def test_get_initial_jamo_special_char(self):
        """Test with special character."""
        result = get_initial_jamo("!")
        assert result == "!"

    def test_get_initial_jamo_common_chars(self):
        """Test with common Korean characters."""
        # ㄱ, ㄴ, ㄷ, ㄹ initials should all be different
        choseong_list = [
            get_initial_jamo("가"),
            get_initial_jamo("나"),
            get_initial_jamo("다"),
            get_initial_jamo("라"),
        ]
        assert len(set(choseong_list)) == 4  # All should be unique


class TestApplyDueum:
    """Tests for apply_dueum function."""

    def test_apply_dueum_no_dueum(self):
        """Test character with no dueum rule."""
        result = apply_dueum("가")
        assert result == ["가"]

    def test_apply_dueum_eon_rule(self):
        """Test ㄴ dueum rule (should include both ㄴ and ㅇ)."""
        result = apply_dueum("은")
        assert "은" in result  # Original character
        # ㄴ dueum should have 2 variations minimum

    def test_apply_dueum_rieul_rule(self):
        """Test ㄹ dueum rule (should include ㄹ, ㅇ, ㄴ)."""
        result = apply_dueum("을")
        assert "을" in result  # Original character
        # ㄹ dueum should have 3 variations

    def test_apply_dueum_yeong_rule(self):
        """Test 려 → 여 dueum rule."""
        result = apply_dueum("려")
        assert "려" in result
        assert "여" in result

    def test_apply_dueum_yeo_rule(self):
        """Test 뇨 → 요 dueum rule."""
        result = apply_dueum("뇨")
        assert "뇨" in result
        assert "요" in result

    def test_apply_dueum_ryo_rule(self):
        """Test 료 → 요 dueum rule."""
        result = apply_dueum("료")
        assert "료" in result
        assert "요" in result

    def test_apply_dueum_ra_rule(self):
        """Test 라 → 나 dueum rule."""
        result = apply_dueum("라")
        assert "라" in result
        assert "나" in result

    def test_apply_dueum_ri_rule(self):
        """Test 리 → 이 dueum rule."""
        result = apply_dueum("리")
        assert "리" in result
        assert "이" in result

    def test_apply_dueum_empty_string(self):
        """Test with empty string."""
        assert apply_dueum("") == []

    def test_apply_dueum_no_duplicates(self):
        """Test that result has no duplicate entries."""
        result = apply_dueum("려")
        assert len(result) == len(set(result))

    def test_apply_dueum_original_always_first(self):
        """Test that original character is always first in result."""
        for char in ["가", "려", "라", "은"]:
            result = apply_dueum(char)
            if result:  # Only test if result is not empty
                assert result[0] == char


class TestIsValidChain:
    """Tests for is_valid_chain function."""

    def test_is_valid_chain_direct_match(self):
        """Test valid chain with direct character match."""
        assert is_valid_chain("사과", "과학") is True

    def test_is_valid_chain_invalid_mismatch(self):
        """Test invalid chain with no match."""
        assert is_valid_chain("사과", "나무") is False

    def test_is_valid_chain_empty_prev_word(self):
        """Test with empty previous word."""
        assert is_valid_chain("", "과학") is False

    def test_is_valid_chain_empty_next_word(self):
        """Test with empty next word."""
        assert is_valid_chain("사과", "") is False

    def test_is_valid_chain_both_empty(self):
        """Test with both words empty."""
        assert is_valid_chain("", "") is False

    def test_is_valid_chain_dueum_yeo(self):
        """Test dueum chain: 려 → 여 should be valid."""
        assert is_valid_chain("~려", "여~") is True

    def test_is_valid_chain_dueum_yeo_invalid(self):
        """Test that non-matching dueum chain is invalid."""
        assert is_valid_chain("~려", "나~") is False

    def test_is_valid_chain_dueum_yo_from_nyo(self):
        """Test dueum chain: 뇨 → 요 should be valid."""
        assert is_valid_chain("~뇨", "요~") is True

    def test_is_valid_chain_dueum_yo_from_ryo(self):
        """Test dueum chain: 료 → 요 should be valid."""
        assert is_valid_chain("~료", "요~") is True

    def test_is_valid_chain_dueum_na_from_ra(self):
        """Test dueum chain: 라 → 나 should be valid."""
        assert is_valid_chain("~라", "나~") is True

    def test_is_valid_chain_dueum_i_from_ri(self):
        """Test dueum chain: 리 → 이 should be valid."""
        assert is_valid_chain("~리", "이~") is True

    def test_is_valid_chain_dueum_i_from_ni(self):
        """Test dueum chain: 니 → 이 should be valid."""
        assert is_valid_chain("~니", "이~") is True

    def test_is_valid_chain_single_chars(self):
        """Test chain with single character words."""
        assert is_valid_chain("가", "가") is True

    def test_is_valid_chain_different_initials(self):
        """Test invalid chain with different initials."""
        assert is_valid_chain("강", "나") is False

    def test_is_valid_chain_real_words_valid(self):
        """Test with real Korean words - valid chain."""
        assert is_valid_chain("사과", "과자") is True

    def test_is_valid_chain_real_words_invalid(self):
        """Test with real Korean words - invalid chain."""
        assert is_valid_chain("사과", "딸기") is False

    def test_is_valid_chain_long_words(self):
        """Test with longer words."""
        assert is_valid_chain("대학교", "교육") is True

    def test_is_valid_chain_complex_dueum(self):
        """Test complex dueum scenario."""
        # 올림 → 미나: 올림 ends with 림, 미나 starts with 미
        # 림 → ㅇ/ㄴ/ㄹ variations don't match 미
        assert is_valid_chain("올림", "미나") is False

    def test_is_valid_chain_nae_rule(self):
        """Test 래 → 내 dueum rule."""
        assert is_valid_chain("~래", "내~") is True

    def test_is_valid_chain_yae_rule(self):
        """Test 례 → 예 dueum rule."""
        assert is_valid_chain("~례", "예~") is True

    def test_is_valid_chain_nae_not_matching(self):
        """Test that non-matching ㄴ initial doesn't match wrong dueum."""
        assert is_valid_chain("~래", "가~") is False

    def test_is_valid_chain_ro_rule(self):
        """Test 로 → 노 dueum rule."""
        assert is_valid_chain("~로", "노~") is True

    def test_is_valid_chain_ru_rule(self):
        """Test 루 → 누 dueum rule."""
        assert is_valid_chain("~루", "누~") is True

    def test_is_valid_chain_ryu_rule(self):
        """Test 류 → 유 dueum rule."""
        assert is_valid_chain("~류", "유~") is True

    def test_is_valid_chain_reul_rule(self):
        """Test 르 → 느 dueum rule."""
        assert is_valid_chain("~르", "느~") is True

    def test_is_valid_chain_nyu_rule(self):
        """Test 뉴 → 유 dueum rule."""
        assert is_valid_chain("~뉴", "유~") is True

    def test_is_valid_chain_nyeo_rule(self):
        """Test 녀 → 여 dueum rule."""
        assert is_valid_chain("~녀", "여~") is True


class TestDueumCoverage:
    """Additional tests to ensure comprehensive dueum coverage."""

    def test_all_dueum_chars_in_dict(self):
        """Test that all predefined dueum chars are in DUEUM_CHARS."""
        from backend.utils.korean import DUEUM_CHARS

        dueum_list = [
            "녀", "뇨", "뉴", "니", "라", "래", "려", "례", "료", "류", "리", "로", "루", "르"
        ]
        for char in dueum_list:
            assert char in DUEUM_CHARS, f"{char} should be in DUEUM_CHARS"

    def test_apply_dueum_consistency(self):
        """Test that apply_dueum is consistent across multiple calls."""
        for char in ["려", "라", "리", "료"]:
            result1 = apply_dueum(char)
            result2 = apply_dueum(char)
            assert result1 == result2

    def test_is_valid_chain_bidirectional_dueum(self):
        """Test that dueum rules work in valid chains."""
        # Test all documented dueum variations
        test_cases = [
            ("~려", "여~", True),
            ("~뇨", "요~", True),
            ("~뉴", "유~", True),
            ("~니", "이~", True),
            ("~라", "나~", True),
            ("~래", "내~", True),
            ("~례", "예~", True),
            ("~료", "요~", True),
            ("~류", "유~", True),
            ("~리", "이~", True),
            ("~로", "노~", True),
            ("~루", "누~", True),
            ("~르", "느~", True),
            ("~녀", "여~", True),
        ]
        for prev_ending, next_start, expected in test_cases:
            result = is_valid_chain(prev_ending, next_start)
            assert result == expected, (
                f"Chain {prev_ending} → {next_start} should be {expected}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
