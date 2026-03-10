"""Pytest tests for PromptBuilder class."""

import pytest
from backend.llm.prompt_builder import PromptBuilder


class TestPromptBuilderBuildSystem:
    """Tests for PromptBuilder.build_system() method."""

    def test_build_system_easy_difficulty(self):
        """Test build_system with easy difficulty level."""
        prompt = PromptBuilder.build_system(difficulty="easy")

        # Verify base prompt is included
        assert "당신은 한국어 끝말잇기 AI 플레이어입니다" in prompt
        assert "게임 규칙:" in prompt
        assert "응답 형식:" in prompt

        # Verify easy difficulty specific text
        assert "난이도: 쉬움" in prompt
        assert "일반적이고 자주 사용하는 단어" in prompt

    def test_build_system_normal_difficulty(self):
        """Test build_system with normal difficulty level."""
        prompt = PromptBuilder.build_system(difficulty="normal")

        # Verify base prompt is included
        assert "당신은 한국어 끝말잇기 AI 플레이어입니다" in prompt
        assert "게임 규칙:" in prompt

        # Verify normal difficulty specific text
        assert "난이도: 중간" in prompt
        assert "적절한 수준의 일반적인 단어" in prompt

    def test_build_system_hard_difficulty(self):
        """Test build_system with hard difficulty level."""
        prompt = PromptBuilder.build_system(difficulty="hard")

        # Verify base prompt is included
        assert "당신은 한국어 끝말잇기 AI 플레이어입니다" in prompt
        assert "게임 규칙:" in prompt

        # Verify hard difficulty specific text
        assert "난이도: 어려움" in prompt
        assert "덜 일반적이고 창의적인 단어" in prompt

    def test_build_system_default_is_normal(self):
        """Test that build_system defaults to normal difficulty when not specified."""
        prompt = PromptBuilder.build_system()

        # Verify it defaults to normal
        assert "난이도: 중간" in prompt
        assert "적절한 수준의 일반적인 단어" in prompt

    def test_build_system_contains_game_rules(self):
        """Test that build_system always contains game rules."""
        for difficulty in ["easy", "normal", "hard"]:
            prompt = PromptBuilder.build_system(difficulty=difficulty)
            assert "주어진 글자로 시작하는 한국어 명사만" in prompt
            assert "2글자 이상의 단어만" in prompt
            assert "이전에 사용된 단어는 다시 사용할 수 없습니다" in prompt

    def test_build_system_contains_response_format(self):
        """Test that build_system always contains response format instructions."""
        prompt = PromptBuilder.build_system(difficulty="easy")
        assert "단 한 개의 단어만 답하세요" in prompt
        assert "추가 설명이나 문장 없이" in prompt
        assert "예: \"사과\"" in prompt

    def test_build_system_returns_string(self):
        """Test that build_system returns a string."""
        prompt = PromptBuilder.build_system()
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestPromptBuilderBuildUser:
    """Tests for PromptBuilder.build_user() method."""

    def test_build_user_with_single_character(self):
        """Test build_user with a single target character."""
        prompt = PromptBuilder.build_user(target_char="가", used_words=[])

        assert "'가'로 시작하는" in prompt
        assert "2글자 이상 한국어 명사" in prompt
        assert "하나만 답하세요" in prompt

    def test_build_user_with_empty_used_words(self):
        """Test build_user with empty used_words list."""
        prompt = PromptBuilder.build_user(target_char="나", used_words=[])

        # Should not contain any used words section
        assert "이미 사용된 단어:" not in prompt
        assert "'나'로 시작하는" in prompt

    def test_build_user_with_single_used_word(self):
        """Test build_user with one previously used word."""
        prompt = PromptBuilder.build_user(target_char="다", used_words=["대문"])

        assert "이미 사용된 단어: 대문" in prompt
        assert "위의 단어들은 사용할 수 없습니다" in prompt
        assert "'다'로 시작하는" in prompt

    def test_build_user_with_multiple_used_words(self):
        """Test build_user with multiple previously used words."""
        used = ["사과", "사진", "사랑"]
        prompt = PromptBuilder.build_user(target_char="사", used_words=used)

        assert "이미 사용된 단어:" in prompt
        assert "사과" in prompt
        assert "사진" in prompt
        assert "사랑" in prompt
        assert ", " in prompt  # words should be comma-separated
        assert "위의 단어들은 사용할 수 없습니다" in prompt

    def test_build_user_with_difficulty_easy(self):
        """Test build_user with easy difficulty."""
        prompt = PromptBuilder.build_user(
            target_char="나",
            used_words=[],
            difficulty="easy"
        )

        assert "'나'로 시작하는" in prompt
        assert isinstance(prompt, str)

    def test_build_user_with_difficulty_normal(self):
        """Test build_user with normal difficulty."""
        prompt = PromptBuilder.build_user(
            target_char="나",
            used_words=[],
            difficulty="normal"
        )

        assert "'나'로 시작하는" in prompt
        assert isinstance(prompt, str)

    def test_build_user_with_difficulty_hard(self):
        """Test build_user with hard difficulty."""
        prompt = PromptBuilder.build_user(
            target_char="나",
            used_words=[],
            difficulty="hard"
        )

        assert "'나'로 시작하는" in prompt
        assert isinstance(prompt, str)

    def test_build_user_returns_string(self):
        """Test that build_user returns a string."""
        prompt = PromptBuilder.build_user(target_char="가", used_words=[])
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_user_target_char_appears_in_prompt(self):
        """Test that target character appears in the prompt."""
        target_chars = ["가", "나", "다", "한", "글"]
        for char in target_chars:
            prompt = PromptBuilder.build_user(target_char=char, used_words=[])
            assert f"'{char}'로 시작하는" in prompt

    def test_build_user_with_long_used_words_list(self):
        """Test build_user with many previously used words."""
        used = [f"단어{i}" for i in range(10)]
        prompt = PromptBuilder.build_user(target_char="단", used_words=used)

        assert "이미 사용된 단어:" in prompt
        for word in used:
            assert word in prompt
        assert "위의 단어들은 사용할 수 없습니다" in prompt

    def test_build_user_format_consistency(self):
        """Test that build_user format is consistent across different parameters."""
        # Test 1: Basic format
        prompt1 = PromptBuilder.build_user(target_char="가", used_words=[])
        assert "'가'로 시작하는 2글자 이상 한국어 명사를 하나만 답하세요." in prompt1

        # Test 2: With used words
        prompt2 = PromptBuilder.build_user(target_char="나", used_words=["나비"])
        assert "'나'로 시작하는 2글자 이상 한국어 명사를 하나만 답하세요." in prompt2


class TestPromptBuilderIntegration:
    """Integration tests for PromptBuilder methods."""

    def test_system_and_user_prompts_work_together(self):
        """Test that system and user prompts can be used together."""
        system = PromptBuilder.build_system(difficulty="normal")
        user = PromptBuilder.build_user(target_char="가", used_words=["감"])

        assert len(system) > 0
        assert len(user) > 0
        assert "AI 플레이어" in system
        assert "'가'로 시작하는" in user

    def test_difficulty_affects_both_prompts(self):
        """Test that difficulty parameter works for both methods appropriately."""
        for difficulty in ["easy", "normal", "hard"]:
            system = PromptBuilder.build_system(difficulty=difficulty)
            user = PromptBuilder.build_user(
                target_char="가",
                used_words=[],
                difficulty=difficulty
            )

            assert isinstance(system, str)
            assert isinstance(user, str)
            assert len(system) > 0
            assert len(user) > 0

    def test_game_flow_simulation(self):
        """Test a simulated game flow with multiple rounds."""
        used_words = []
        difficulty = "normal"

        # Round 1
        system = PromptBuilder.build_system(difficulty=difficulty)
        user = PromptBuilder.build_user(target_char="가", used_words=used_words, difficulty=difficulty)
        assert "'가'로 시작하는" in user

        # Simulate first word being used
        used_words.append("가지")

        # Round 2
        user = PromptBuilder.build_user(target_char="지", used_words=used_words, difficulty=difficulty)
        assert "'지'로 시작하는" in user
        assert "가지" in user
        assert "위의 단어들은 사용할 수 없습니다" in user

        # Simulate second word being used
        used_words.append("지문")

        # Round 3
        user = PromptBuilder.build_user(target_char="문", used_words=used_words, difficulty=difficulty)
        assert "'문'로 시작하는" in user
        assert "가지" in user
        assert "지문" in user
