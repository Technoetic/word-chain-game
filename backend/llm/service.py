"""LLM service for word chain game using Claude API."""

import asyncio
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
        self.client: anthropic.Anthropic = anthropic.Anthropic(**kwargs)

    STREAM_TIMEOUT = 10  # seconds

    async def stream_word(
        self, target_char: str, used_words: list[str], difficulty: str = "normal"
    ) -> AsyncGenerator[str, None]:
        """Stream word generation from Claude, yielding character deltas."""
        system_prompt = PromptBuilder.build_system(difficulty)
        user_prompt = PromptBuilder.build_user(target_char, used_words, difficulty)

        loop = asyncio.get_event_loop()

        def _stream_sync():
            chunks = []
            with self.client.messages.stream(
                model=self._model,
                max_tokens=100,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    chunks.append(text)
            return chunks

        chunks = await asyncio.wait_for(
            loop.run_in_executor(None, _stream_sync),
            timeout=self.STREAM_TIMEOUT,
        )
        for chunk in chunks:
            yield chunk

    async def stream_reaction(
        self, user_word: str, target_char: str
    ) -> AsyncGenerator[str, None]:
        """Stream a short frustrated reaction when user plays a killer word."""
        system_prompt = (
            "너는 끝말잇기 AI 플레이어야. 상대가 한방 단어를 써서 "
            "이을 수 없는 글자를 줬어. 짧게 욕/짜증 리액션을 해. "
            "규칙:\n"
            "- 반말, 인터넷 말투 사용\n"
            "- 10자 이내로 매우 짧게\n"
            "- 이모지 금지\n"
            "- 예시: 'ㅋㅋ 미쳤냐', '아 ㅅㅂ', '야 그건 좀...', 'ㄹㅇ 어쩌라고'\n"
            "- 단어만 출력, 설명 금지"
        )
        user_prompt = f"상대가 '{user_word}'을 말해서 '{target_char}'(으)로 이어야 해. 리액션해."

        loop = asyncio.get_event_loop()

        def _stream_sync():
            chunks = []
            with self.client.messages.stream(
                model=self._model,
                max_tokens=30,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for text in stream.text_stream:
                    chunks.append(text)
            return chunks

        chunks = await asyncio.wait_for(
            loop.run_in_executor(None, _stream_sync),
            timeout=self.STREAM_TIMEOUT,
        )
        for chunk in chunks:
            yield chunk

    async def get_word(
        self, target_char: str, used_words: list[str], difficulty: str = "normal"
    ) -> str:
        """Get complete word from Claude."""
        system_prompt = PromptBuilder.build_system(difficulty)
        user_prompt = PromptBuilder.build_user(target_char, used_words, difficulty)

        loop = asyncio.get_event_loop()

        def _create_sync():
            message = self.client.messages.create(
                model=self._model,
                max_tokens=100,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text.strip()

        return await loop.run_in_executor(None, _create_sync)
