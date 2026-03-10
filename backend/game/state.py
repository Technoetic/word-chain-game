from typing import List
from pydantic import BaseModel, Field


class GameState(BaseModel):
    session_id: str
    used_words: List[str] = Field(default_factory=list)
    last_word: str = ""
    turn_count: int = 0
    is_active: bool = False
    difficulty: str = "normal"
    current_turn: str = "user"  # "user" or "llm"


class WordResult(BaseModel):
    valid: bool
    word: str
    reason: str
    message: str
