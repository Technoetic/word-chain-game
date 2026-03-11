import asyncio
from uuid import uuid4
from typing import AsyncGenerator
from backend.game.state import GameState
from backend.game.rules import GameRules
from backend.utils.korean import is_valid_chain, apply_dueum, is_killer_char


class GameEngine:
    def __init__(self, word_validator, llm_service, rules=None):
        self.word_validator = word_validator
        self.llm_service = llm_service
        self.rules = rules or GameRules()
        self.state = GameState(session_id=str(uuid4()))

    def start_game(self, difficulty: str = "normal") -> dict:
        self.state.difficulty = difficulty
        self.state.is_active = True
        self.state.current_turn = "user"
        return {
            "type": "game_started",
            "session_id": self.state.session_id,
            "difficulty": difficulty,
        }

    async def process_user_word(self, word: str, time_left: int = 15) -> dict:
        if not self.state.is_active:
            return {
                "type": "word_result",
                "valid": False,
                "word": word,
                "message": "Game is not active",
            }

        if self.state.current_turn != "user":
            return {
                "type": "word_result",
                "valid": False,
                "word": word,
                "message": "Not your turn",
            }

        if len(word) < 2:
            return {
                "type": "word_result",
                "valid": False,
                "word": word,
                "message": "Word must be at least 2 characters",
            }

        if word in self.state.used_words:
            return {
                "type": "word_result",
                "valid": False,
                "word": word,
                "message": "Word already used",
            }

        if self.state.last_word and not is_valid_chain(self.state.last_word, word):
            return {
                "type": "word_result",
                "valid": False,
                "word": word,
                "message": "Word does not follow chain rules",
            }

        validation = await self.word_validator.validate(word)
        if (
            not validation.get("valid", False)
            if isinstance(validation, dict)
            else not validation
        ):
            return {
                "type": "word_result",
                "valid": False,
                "word": word,
                "message": validation.get("message", "사전에 없는 단어") if isinstance(validation, dict) else "사전에 없는 단어",
            }

        self.state.used_words.append(word)
        self.state.last_word = word
        self.state.turn_count += 1
        self.state.current_turn = "llm"

        last_char = word[-1]
        killer = is_killer_char(last_char)

        return {
            "type": "word_result",
            "valid": True,
            "word": word,
            "message": "Valid word",
            "killer_word": killer,
        }

    MAX_LLM_RETRIES = 10

    async def generate_llm_response(self, target_char: str) -> AsyncGenerator:
        dueum_chars = apply_dueum(target_char)
        search_char = dueum_chars[0] if isinstance(dueum_chars, list) else dueum_chars

        for _attempt in range(self.MAX_LLM_RETRIES):
            collected_word = ""
            try:
                yield {"type": "llm_typing", "char": "START"}
                async for char in self.llm_service.stream_word(
                    search_char, self.state.used_words, self.state.difficulty
                ):
                    collected_word += char
                    yield {"type": "llm_typing", "char": char}
            except (asyncio.CancelledError, GeneratorExit):
                raise
            except Exception:
                continue

            llm_word = collected_word.strip()

            if not llm_word or llm_word in self.state.used_words:
                continue

            if not is_valid_chain(self.state.last_word, llm_word):
                continue

            validation = await self.word_validator.validate(llm_word)
            is_valid = (
                validation.get("valid", False)
                if isinstance(validation, dict)
                else bool(validation)
            )

            if is_valid:
                self.state.used_words.append(llm_word)
                self.state.last_word = llm_word
                self.state.turn_count += 1
                self.state.current_turn = "user"
                yield {"type": "llm_complete", "word": llm_word}
                return

        # All retries exhausted — AI gives up
        self.state.is_active = False
        yield {"type": "game_over", "winner": "user", "reason": "AI가 단어를 찾지 못했습니다"}

    def end_game(self, reason: str) -> dict:
        self.state.is_active = False
        if self.state.current_turn == "user":
            winner = "llm"
        else:
            winner = "user"
        return {
            "type": "game_over",
            "winner": winner,
            "reason": reason,
        }
