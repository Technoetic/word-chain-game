from pydantic import BaseModel


class WSMessage(BaseModel):
    type: str


class GameStartMsg(WSMessage):
    type: str = "game_start"
    difficulty: str = "normal"


class WordSubmitMsg(WSMessage):
    type: str = "word_submit"
    word: str


class WordResultMsg(BaseModel):
    type: str = "word_result"
    valid: bool
    word: str
    score: int = 0
    message: str = ""


class LLMTypingMsg(BaseModel):
    type: str = "llm_typing"
    char: str


class LLMCompleteMsg(BaseModel):
    type: str = "llm_complete"
    word: str
    score: int


class GameOverMsg(BaseModel):
    type: str = "game_over"
    winner: str
    user_score: int
    llm_score: int


class ErrorMsg(BaseModel):
    type: str = "error"
    message: str
