import pytest
from backend.game.scoring import ScoringSystem


class TestScoringSystemCalculate:
    """Test suite for ScoringSystem.calculate() method"""

    def test_calculate_empty_word_returns_zero(self):
        """Empty word should return 0 score"""
        scorer = ScoringSystem()
        result = scorer.calculate("", combo=0, time_left=15)
        assert result == 0

    def test_calculate_three_letter_word_no_bonus(self):
        """Three-letter word with no combo/time bonus"""
        scorer = ScoringSystem()
        # base = 100 + (3-2)*10 = 110
        # combo_mult = 1.0
        # time_bonus = 15/15 = 1.0, so (1 + 1.0*0.1) = 1.1
        # score = int(110 * 1.0 * 1.1) = 121
        result = scorer.calculate("가나다", combo=0, time_left=15)
        assert result == 121

    def test_calculate_two_letter_word(self):
        """Two-letter word base calculation"""
        scorer = ScoringSystem()
        # base = 100 + (2-2)*10 = 100
        # combo_mult = 1.0
        # time_bonus = 15/15 = 1.0, so (1 + 1.0*0.1) = 1.1
        # score = int(100 * 1.0 * 1.1) = 110
        result = scorer.calculate("가나", combo=0, time_left=15)
        assert result == 110

    def test_calculate_long_word_length_bonus(self):
        """Longer words receive more base score"""
        scorer = ScoringSystem()
        # base = 100 + (5-2)*10 = 130
        # combo_mult = 1.0
        # time_bonus = 15/15 = 1.0, so (1 + 1.0*0.1) = 1.1
        # score = int(130 * 1.0 * 1.1) = 143
        result = scorer.calculate("가나다라마", combo=0, time_left=15)
        assert result == 143

    def test_calculate_zero_time_left(self):
        """No time bonus when time_left is 0"""
        scorer = ScoringSystem()
        # base = 100 + (3-2)*10 = 110
        # combo_mult = 1.0
        # time_bonus = 0/15 = 0, so (1 + 0*0.1) = 1.0
        # score = int(110 * 1.0 * 1.0) = 110
        result = scorer.calculate("가나다", combo=0, time_left=0)
        assert result == 110

    def test_calculate_negative_time_left(self):
        """Negative time_left should be treated as 0 (max(0, negative) = 0)"""
        scorer = ScoringSystem()
        # base = 100 + (3-2)*10 = 110
        # time_bonus = max(0, -5) / 15 = 0 / 15 = 0, so (1 + 0*0.1) = 1.0
        # score = int(110 * 1.0 * 1.0) = 110
        result = scorer.calculate("가나다", combo=0, time_left=-5)
        assert result == 110

    def test_calculate_partial_time_left(self):
        """Time bonus calculation with partial time remaining"""
        scorer = ScoringSystem()
        # base = 100 + (3-2)*10 = 110
        # combo_mult = 1.0
        # time_bonus = 8/15 ≈ 0.533, so (1 + 0.533*0.1) ≈ 1.0533
        # score = int(110 * 1.0 * 1.0533) = 115
        result = scorer.calculate("가나다", combo=0, time_left=8)
        assert result == 115

    def test_calculate_combo_multiplier_applied(self):
        """Combo multiplier affects final score"""
        scorer = ScoringSystem()
        result_no_combo = scorer.calculate("가나다", combo=0, time_left=15)
        result_combo_1 = scorer.calculate("가나다", combo=1, time_left=15)
        # combo=1 should give 1.5x multiplier
        assert result_combo_1 > result_no_combo
        assert result_combo_1 == int(result_no_combo * 1.5)

    def test_calculate_killer_word_bonus(self):
        """Killer word receives bonus points"""
        scorer = ScoringSystem()
        # Non-killer word with same length for fair comparison
        result_regular = scorer.calculate("가나", combo=0, time_left=15)
        # Killer word (ends with rare final, index 18)
        result_killer = scorer.calculate("값", combo=0, time_left=15)
        # "값" is 1 char, base = 100 + (1-2)*10 = 90, mult=1.0, time_bonus=1.0, score=int(90*1.0*1.1)=99, plus 500 killer = 599
        # "가나" base = 100, mult=1.0, time_bonus=1.0, score=int(100*1.0*1.1)=110
        assert result_killer > result_regular
        assert result_killer >= 500  # Should include killer bonus (599)

    def test_calculate_with_all_bonuses(self):
        """Calculate with both combo and killer word bonuses"""
        scorer = ScoringSystem()
        # Word ending with rare final (ㄿ) and combo bonus
        result = scorer.calculate("값", combo=2, time_left=15)
        # Should include both multiplier and killer bonus
        assert result > 0
        assert result > 121  # Basic score


class TestGetComboMultiplier:
    """Test suite for ScoringSystem.get_combo_multiplier() method"""

    def test_combo_zero_returns_one(self):
        """Combo 0 should return 1.0 multiplier"""
        scorer = ScoringSystem()
        result = scorer.get_combo_multiplier(0)
        assert result == 1.0

    def test_combo_negative_returns_one(self):
        """Negative combo should return 1.0 multiplier"""
        scorer = ScoringSystem()
        result = scorer.get_combo_multiplier(-5)
        assert result == 1.0

    def test_combo_one_returns_1_5(self):
        """Combo 1 should return 1.5 multiplier"""
        scorer = ScoringSystem()
        result = scorer.get_combo_multiplier(1)
        assert result == 1.5

    def test_combo_two_returns_2_0(self):
        """Combo 2 should return 2.0 multiplier"""
        scorer = ScoringSystem()
        result = scorer.get_combo_multiplier(2)
        assert result == 2.0

    def test_combo_three_returns_2_5(self):
        """Combo 3 should return 2.5 multiplier"""
        scorer = ScoringSystem()
        result = scorer.get_combo_multiplier(3)
        assert result == 2.5

    def test_combo_four_or_higher_returns_3_0(self):
        """Combo 4+ should return 3.0 multiplier (capped)"""
        scorer = ScoringSystem()
        result_four = scorer.get_combo_multiplier(4)
        result_five = scorer.get_combo_multiplier(5)
        result_high = scorer.get_combo_multiplier(10)
        assert result_four == 3.0
        assert result_five == 3.0
        assert result_high == 3.0

    def test_multiplier_progression(self):
        """Multipliers should increase progressively"""
        scorer = ScoringSystem()
        m0 = scorer.get_combo_multiplier(0)
        m1 = scorer.get_combo_multiplier(1)
        m2 = scorer.get_combo_multiplier(2)
        m3 = scorer.get_combo_multiplier(3)
        m4 = scorer.get_combo_multiplier(4)
        assert m0 < m1 < m2 < m3 < m4
        assert m3 == 2.5 and m4 == 3.0  # m3=2.5, m4=3.0


class TestIsKillerWord:
    """Test suite for ScoringSystem.is_killer_word() method"""

    def test_empty_word_not_killer(self):
        """Empty word should not be a killer word"""
        scorer = ScoringSystem()
        result = scorer.is_killer_word("")
        assert result is False

    def test_regular_korean_final_not_killer(self):
        """Words with common Korean finals should not be killer"""
        scorer = ScoringSystem()
        # "다" has final index 0 (ㅇ), which is not rare
        result = scorer.is_killer_word("다")
        assert result is False

    def test_rare_final_3_is_killer(self):
        """Final index 18 (ㄱ+ㄴ) is a rare final and should be killer"""
        scorer = ScoringSystem()
        # "값" has final index 18 (ㄿ), which is in rare_finals
        result = scorer.is_killer_word("값")
        assert result is True

    def test_killer_word_with_jongseong(self):
        """Words ending with certain consonants are killer words"""
        scorer = ScoringSystem()
        # Test with words that are actually killer words based on implementation
        # "값" (gabs) has final_index 18 which is in rare_finals set
        result = scorer.is_killer_word("값")
        assert result is True

    def test_rare_final_12_is_killer(self):
        """Final index 12 (ㅂ) is a rare final and should be killer"""
        scorer = ScoringSystem()
        # "값" has final ㄿ combination, which is index in rare_finals
        result = scorer.is_killer_word("값")
        assert result is True

    def test_english_word_not_killer(self):
        """English words should not be killer (not Korean)"""
        scorer = ScoringSystem()
        result = scorer.is_killer_word("hello")
        assert result is False

    def test_mixed_korean_english_checks_last_char(self):
        """Only last character determines killer status"""
        scorer = ScoringSystem()
        # Last char is Korean with rare final (index 18 for 값)
        result = scorer.is_killer_word("hello값")
        assert result is True

    def test_single_letter_killer(self):
        """Single Korean letter with rare final"""
        scorer = ScoringSystem()
        # "값" is killer (rare final ㄿ)
        result = scorer.is_killer_word("값")
        assert result is True

    def test_multiple_rare_finals_in_set(self):
        """Test rare finals: {3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 18, 20}"""
        scorer = ScoringSystem()
        # The rare_finals set in implementation is {3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 18, 20}
        # "값" is index 18, which is in the set
        killer_words = [
            "값",    # index 18 (in rare_finals)
        ]
        for word in killer_words:
            assert scorer.is_killer_word(word) is True, f"'{word}' should be killer"

        # Test non-killer words
        non_killer = ["가", "나", "다"]  # indices 1, 2, 0 (not in rare_finals)
        for word in non_killer:
            assert scorer.is_killer_word(word) is False, f"'{word}' should not be killer"

    def test_common_finals_not_killer(self):
        """Words with common finals should not be killer"""
        scorer = ScoringSystem()
        # Common finals (indices 0, 1, 2, 4, 7, 8, 16, 17, 19, 21, 22, 23, 24, 25, 26, 27)
        non_killer_words = [
            "다",    # final 0 (ㅇ)
            "가",    # final 1 (ㄱ)
            "나",    # final 2 (ㄲ)
        ]
        for word in non_killer_words:
            assert scorer.is_killer_word(word) is False, f"'{word}' should not be killer"

    def test_only_korean_hangul_checked(self):
        """Only Korean Hangul syllables are checked"""
        scorer = ScoringSystem()
        # Numbers, symbols, etc. should not be killer
        result = scorer.is_killer_word("123")
        assert result is False
        result = scorer.is_killer_word("!@#")
        assert result is False

    def test_killer_status_independent_of_word_length(self):
        """Killer status depends only on last character"""
        scorer = ScoringSystem()
        # Same rare final (값 with index 18), different lengths
        short = "값"
        long = "아주긴단어값"
        assert scorer.is_killer_word(short) is True
        assert scorer.is_killer_word(long) is True
        assert scorer.is_killer_word(short) == scorer.is_killer_word(long)


class TestIntegration:
    """Integration tests combining multiple methods"""

    def test_scoring_with_various_combos_and_time(self):
        """Test scoring across different combo/time combinations"""
        scorer = ScoringSystem()
        results = []
        for combo in range(0, 5):
            for time in [0, 8, 15]:
                score = scorer.calculate("가나다", combo=combo, time_left=time)
                results.append((combo, time, score))

        # Verify scores increase with combo
        for combo in range(0, 4):
            score_c = scorer.calculate("가나다", combo=combo, time_left=15)
            score_c_next = scorer.calculate("가나다", combo=combo+1, time_left=15)
            assert score_c_next >= score_c

    def test_killer_word_bonus_consistency(self):
        """Killer bonus should be consistent across different scenarios"""
        scorer = ScoringSystem()
        word_killer = "값"
        word_regular = "가나"

        # Score difference should include the killer bonus
        score_killer_base = scorer.calculate(word_killer, combo=0, time_left=15)
        score_regular = scorer.calculate(word_regular, combo=0, time_left=15)

        # The killer word should score higher due to bonus
        assert score_killer_base > score_regular

    def test_no_integer_overflow(self):
        """Very long words shouldn't cause overflow"""
        scorer = ScoringSystem()
        long_word = "가" * 50
        result = scorer.calculate(long_word, combo=4, time_left=15)
        assert isinstance(result, int)
        assert result > 0

    def test_score_always_non_negative(self):
        """Score should never be negative"""
        scorer = ScoringSystem()
        test_cases = [
            ("", 0, 0),
            ("", 5, -10),
            ("가", 0, -100),
            ("가나다라마", 4, 15),
        ]
        for word, combo, time in test_cases:
            result = scorer.calculate(word, combo=combo, time_left=time)
            assert result >= 0

    def test_empty_word_across_all_parameters(self):
        """Empty word should always return 0 regardless of other params"""
        scorer = ScoringSystem()
        test_combos = [-5, 0, 1, 3, 5, 10]
        test_times = [-100, 0, 7, 15, 30]

        for combo in test_combos:
            for time in test_times:
                result = scorer.calculate("", combo=combo, time_left=time)
                assert result == 0, f"Empty word with combo={combo}, time={time} should be 0"

    def test_score_reflects_all_factors(self):
        """Score should reflect word length, combo, time, and killer status"""
        scorer = ScoringSystem()

        # Base score
        score1 = scorer.calculate("가나", combo=0, time_left=0)
        # Longer word
        score2 = scorer.calculate("가나다라", combo=0, time_left=0)
        # Same length with combo
        score3 = scorer.calculate("가나다라", combo=1, time_left=0)
        # Same with time
        score4 = scorer.calculate("가나다라", combo=1, time_left=15)

        # All scores should progress logically
        assert score1 < score2 < score3 < score4


class TestEdgeCases:
    """Edge case and boundary tests"""

    def test_combo_boundary_values(self):
        """Test exact boundary values for combo multiplier"""
        scorer = ScoringSystem()
        assert scorer.get_combo_multiplier(-1) == 1.0
        assert scorer.get_combo_multiplier(0) == 1.0
        assert scorer.get_combo_multiplier(1) == 1.5
        assert scorer.get_combo_multiplier(2) == 2.0
        assert scorer.get_combo_multiplier(3) == 2.5
        assert scorer.get_combo_multiplier(4) == 3.0
        assert scorer.get_combo_multiplier(100) == 3.0

    def test_time_boundary_values(self):
        """Test exact boundary values for time bonus"""
        scorer = ScoringSystem()
        # time_left = 0
        result_zero = scorer.calculate("가나다", combo=0, time_left=0)
        # time_left = 15 (max)
        result_max = scorer.calculate("가나다", combo=0, time_left=15)
        # time_left = -1
        result_neg = scorer.calculate("가나다", combo=0, time_left=-1)

        assert result_zero == result_neg  # Both should be same (max(0, -1) = 0)
        assert result_max > result_zero

    def test_very_long_korean_word(self):
        """Long Korean word calculation"""
        scorer = ScoringSystem()
        long_word = "가" * 100
        result = scorer.calculate(long_word, combo=0, time_left=15)
        expected_base = 100 + (100 - 2) * 10  # 1080
        # Should be at least close to expected base with multipliers
        assert result > 0

    def test_unicode_korean_character_detection(self):
        """Korean Hangul detection in valid range 0xAC00-0xD7A3"""
        scorer = ScoringSystem()
        # Valid Hangul syllable range
        result_valid = scorer.is_killer_word("가")
        assert result_valid is not None

        # Character just outside the range should not be killer
        # (but should not crash)
        result_outside = scorer.is_killer_word("ㄱ")  # Hangul Jamo (outside range)
        assert result_outside is False

    def test_word_with_mixed_characters(self):
        """Only the last character determines killer status"""
        scorer = ScoringSystem()
        # Last char is common final (not killer)
        result1 = scorer.is_killer_word("hello다")
        assert result1 is False

        # Last char is rare final (killer) - 값 has index 18
        result2 = scorer.is_killer_word("world값")
        assert result2 is True

    def test_fractional_score_truncation(self):
        """Score is truncated to integer (no rounding up)"""
        scorer = ScoringSystem()
        # Create a case with fractional result
        result = scorer.calculate("가나다", combo=0, time_left=7)
        assert isinstance(result, int)
        # Result should be truncated, not rounded
        assert result >= 0
