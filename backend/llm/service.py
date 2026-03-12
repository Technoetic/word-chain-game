"""LLM service for word chain game using Claude API."""

import anthropic
from typing import AsyncGenerator

from .prompt_builder import PromptBuilder


class LLMService:
    """Service for interacting with Claude LLM."""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001", base_url: str = ""):
        self._api_key: str = api_key
        self._model: str = model
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client: anthropic.AsyncAnthropic = anthropic.AsyncAnthropic(**kwargs)

    STREAM_TIMEOUT = 10  # seconds

    async def stream_word(
        self, target_char: str, used_words: list[str], difficulty: str = "normal",
        revenge: bool = False
    ) -> AsyncGenerator[str, None]:
        """Stream word generation from Claude, yielding character deltas."""
        system_prompt = PromptBuilder.build_system(difficulty, revenge=revenge)
        user_prompt = PromptBuilder.build_user(target_char, used_words, difficulty)

        async with self.client.messages.stream(
            model=self._model,
            max_tokens=100,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            timeout=self.STREAM_TIMEOUT,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def stream_reaction(
        self, user_word: str, target_char: str, killer_count: int = 1
    ) -> AsyncGenerator[str, None]:
        """Stream a frustrated reaction when user plays a killer word."""
        if killer_count >= 3:
            mood = "극대노. 복수를 다짐하며 분노 폭발. 살벌하게."
            examples = "'야 진짜 죽을래?', '나 진심 열받네 두고봐', '복수한다 진짜로'"
        elif killer_count >= 2:
            mood = "화남. 복수를 선언하며 짜증."
            examples = "'또? 야 나도 안봐준다', '다음엔 각오해', 'ㅋㅋ 복수할거임'"
        else:
            mood = "짜증. 가볍게 투덜거림."
            examples = "'ㅋㅋ 미쳤냐', '아 ㅅㅂ', '야 그건 좀...', '와 개사기'"

        system_prompt = (
            f"너는 끝말잇기 AI 플레이어야. 상대가 한방 단어를 써서 "
            f"이을 수 없는 글자를 줬어. 현재 감정: {mood}\n"
            f"규칙:\n"
            f"- 반말, 인터넷 말투 사용\n"
            f"- 15자 이내로 짧게\n"
            f"- 이모지 금지\n"
            f"- 예시: {examples}\n"
            f"- 리액션만 출력, 설명 금지"
        )
        user_prompt = f"상대가 '{user_word}'을 말해서 '{target_char}'(으)로 이어야 해. 한방 단어 {killer_count}번째 당함. 리액션해."

        async with self.client.messages.stream(
            model=self._model,
            max_tokens=30,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            timeout=self.STREAM_TIMEOUT,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def get_word(
        self, target_char: str, used_words: list[str], difficulty: str = "normal"
    ) -> str:
        """Get complete word from Claude."""
        system_prompt = PromptBuilder.build_system(difficulty)
        user_prompt = PromptBuilder.build_user(target_char, used_words, difficulty)

        message = await self.client.messages.create(
            model=self._model,
            max_tokens=100,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text.strip()
