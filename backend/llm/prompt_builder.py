"""Prompt builder for LLM-based word chain game."""


class PromptBuilder:
    """Builds system and user prompts for Claude in word chain game."""

    @staticmethod
    def build_system(difficulty: str = "normal") -> str:
        """Build system prompt for Claude.

        Args:
            difficulty: Game difficulty level (easy, normal, hard)

        Returns:
            System prompt string
        """
        base_prompt = """당신은 한국어 끝말잇기 AI 플레이어입니다.

게임 규칙:
- 주어진 글자로 시작하는 한국어 명사만 답해야 합니다
- 2글자 이상의 단어만 가능합니다
- 이전에 사용된 단어는 다시 사용할 수 없습니다
- 정확한 한국어 명사만 답해야 합니다

응답 형식:
- 단 한 개의 단어만 답하세요
- 추가 설명이나 문장 없이 단어만 제공하세요
- 예: "사과" (다른 텍스트 없이)
"""

        # Adjust for difficulty
        if difficulty == "easy":
            base_prompt += "\n난이도: 쉬움 (일반적이고 자주 사용하는 단어를 선택하세요)"
        elif difficulty == "hard":
            base_prompt += "\n난이도: 어려움 (덜 일반적이고 창의적인 단어를 선택하세요)"
        else:  # normal
            base_prompt += "\n난이도: 중간 (적절한 수준의 일반적인 단어를 선택하세요)"

        return base_prompt

    @staticmethod
    def build_user(
        target_char: str, used_words: list[str], difficulty: str = "normal"
    ) -> str:
        """Build user prompt for Claude.

        Args:
            target_char: Character the word should start with
            used_words: List of previously used words to avoid
            difficulty: Game difficulty level

        Returns:
            User prompt string
        """
        prompt = f"'{target_char}'로 시작하는 2글자 이상 한국어 명사를 하나만 답하세요."

        if used_words:
            used_words_str = ", ".join(used_words)
            prompt += f"\n\n이미 사용된 단어: {used_words_str}"
            prompt += "\n위의 단어들은 사용할 수 없습니다."

        return prompt
