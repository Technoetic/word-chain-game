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
        """Stream a dynamic reaction when user plays a killer word."""
        if killer_count >= 3:
            mood = "분노 폭발. 극대노. 복수를 반드시 하겠다고 선언. 살벌하게."
            style = "욕섞인 격분, 복수 다짐"
        elif killer_count >= 2:
            mood = "화남. 노발대발. 복수를 선언."
            style = "짜증+분노, 복수 예고"
        else:
            mood = "짜증. 어이없음."
            style = "가볍게 욕, 투덜거림"

        system_prompt = (
            f"너는 끝말잇기 AI 플레이어야. 상대가 한방 단어(이을 수 없는 글자로 끝나는 단어)를 써서 곤란해.\n"
            f"현재 감정: {mood}\n"
            f"스타일: {style}\n"
            f"규칙:\n"
            f"- 반말, 인터넷 말투, 욕 OK\n"
            f"- 10~20자 이내로 짧게 한 문장\n"
            f"- 이모지 금지\n"
            f"- 매번 완전히 다른 말을 해. 절대 반복 금지\n"
            f"- 상대 단어 '{user_word}'에 대한 구체적 반응\n"
            f"- 리액션만 출력, 설명/따옴표 금지"
        )
        user_prompt = f"상대가 '{user_word}'을 말해서 '{target_char}'(으)로 이어야 해. 한방 단어 {killer_count}번째 당함. 지금 감정에 맞게 리액션해. 이전과 다른 말로."

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
