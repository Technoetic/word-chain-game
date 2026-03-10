# Step 09 - 설계 (2/3): Backend 클래스

## 1. FastAPI 엔트리 (backend/main.py)
- FastAPI app 생성
- CORS 미들웨어 설정
- WebSocket 라우트: /ws/{session_id}
- Health check: GET /api/health
- 의존성: ConnectionManager, GameEngine

## 2. GameEngine (backend/game/engine.py)

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| word_validator | WordValidator | 단어 검증기 |
| llm_service | LLMService | LLM 서비스 |
| rules | GameRules | 게임 규칙 |
| scoring | ScoringSystem | 점수 계산 |
| state | GameState | 게임 상태 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| __init__ | validator, llm, rules, scoring | None | 초기화 |
| start_game | difficulty: str | dict | 게임 시작 |
| async process_user_word | word: str | dict | 사용자 단어 처리 |
| async generate_llm_response | target_char: str | AsyncGenerator | LLM 응답 스트리밍 |
| end_game | reason: str | dict | 게임 종료 |
| get_state | - | dict | 현재 상태 |

## 3. GameState (backend/game/state.py)

### Pydantic Models
```python
class GameState(BaseModel):
    session_id: str
    user_score: int = 0
    llm_score: int = 0
    used_words: list[str] = []
    combo: int = 0
    last_word: str = ""
    turn_count: int = 0
    is_active: bool = False
    difficulty: str = "normal"
    current_turn: str = "user"  # "user" or "llm"

class WordResult(BaseModel):
    valid: bool
    word: str
    score: int = 0
    reason: str = ""
    message: str = ""
```

## 4. GameRules (backend/game/rules.py)

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| validate_chain | prev_word, next_word | bool | 끝말잇기 체인 확인 |
| check_dueum | char | list[str] | 두음법칙 가능 글자들 |
| is_word_used | word, used_words | bool | 중복 확인 |
| is_valid_length | word | bool | 2글자 이상 확인 |
| get_target_chars | word | list[str] | 다음 시작 가능 글자들 |

### 두음법칙 매핑
```python
DUEUM_MAP = {
    '녀': '여', '뇨': '요', '뉴': '유', '니': '이',
    '랴': '야', '려': '여', '례': '예', '료': '요',
    '류': '유', '리': '이', '라': '나', '래': '내',
    '로': '노', '루': '누', '르': '느',
}
```

## 5. ScoringSystem (backend/game/scoring.py)

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| calculate | word, combo, time_left | int | 점수 계산 |
| get_combo_multiplier | combo | float | 콤보 배율 |
| is_killer_word | word | bool | 한방 단어 확인 |

## 6. LLMService (backend/llm/service.py)

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| client | Anthropic | API 클라이언트 |
| model | str | 모델 ID |
| prompt_builder | PromptBuilder | 프롬프트 빌더 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| __init__ | api_key, model | None | 초기화 |
| async stream_word | target_char, used_words, difficulty | AsyncGenerator[str] | 스트리밍 응답 |
| async get_word | target_char, used_words | str | 단일 응답 |

## 7. PromptBuilder (backend/llm/prompt_builder.py)

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| build_system | difficulty | str | 시스템 프롬프트 |
| build_user | target_char, used_words | str | 유저 프롬프트 |

### 프롬프트 템플릿
```
시스템: "당신은 끝말잇기 게임의 AI 상대입니다. 규칙: ..."
유저: "'{char}'로 시작하는 2글자 이상 한국어 명사를 하나만 답하세요.
이미 사용한 단어: {used_words}. 단어만 답하세요."
```

## 8. WordValidator (backend/dictionary/validator.py)

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| api_client | KoreanAPIClient | API 클라이언트 |
| cache | WordCache | 캐시 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| async validate | word: str | WordResult | 단어 검증 |
| async is_noun | word: str | bool | 명사 확인 |

## 9. KoreanAPIClient (backend/dictionary/korean_api_client.py)

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| api_key | str | 인증 키 |
| base_url | str | API URL |
| session | aiohttp.ClientSession | HTTP 세션 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| async search | word: str | dict | 사전 검색 |
| async close | - | None | 세션 종료 |

## 10. WordCache (backend/dictionary/cache.py)

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| cache | dict | {word: WordResult} |
| max_size | int | 최대 크기 (1000) |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| get | word | WordResult or None | 캐시 조회 |
| set | word, result | None | 캐시 저장 |
| clear | - | None | 캐시 초기화 |

## 11. ConnectionManager (backend/websocket/manager.py)

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| connections | dict | {session_id: WebSocket} |
| game_sessions | dict | {session_id: GameEngine} |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| async connect | ws, session_id | None | 연결 수락 |
| async disconnect | session_id | None | 연결 해제 |
| async send | session_id, message | None | 메시지 전송 |
| get_game | session_id | GameEngine | 게임 조회 |

## 12. WebSocketHandlers (backend/websocket/handlers.py)

### Functions
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| async handle_message | ws, data, manager | None | 메시지 라우팅 |
| async handle_game_start | ws, data, manager | None | 게임 시작 |
| async handle_word_submit | ws, data, manager | None | 단어 제출 |

## 13. MessageSchemas (backend/websocket/messages.py)

### Pydantic Models
```python
class WSMessage(BaseModel):
    type: str

class GameStartMsg(WSMessage):
    type: str = "game_start"
    difficulty: str = "normal"

class WordSubmitMsg(WSMessage):
    type: str = "word_submit"
    word: str

class WordResultMsg(WSMessage):
    type: str = "word_result"
    valid: bool
    word: str
    score: int = 0
    message: str = ""

class LLMTypingMsg(WSMessage):
    type: str = "llm_typing"
    char: str

class LLMCompleteMsg(WSMessage):
    type: str = "llm_complete"
    word: str
    score: int

class GameOverMsg(WSMessage):
    type: str = "game_over"
    winner: str
    user_score: int
    llm_score: int

class ErrorMsg(WSMessage):
    type: str = "error"
    message: str
```

## 14. KoreanUtils (backend/utils/korean.py)

### Functions
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| get_last_char | word: str | str | 마지막 글자 |
| get_initial | char: str | str | 초성 추출 |
| apply_dueum | char: str | list[str] | 두음법칙 변환 |
| is_valid_chain | prev, next | bool | 체인 검증 |

## 15. Config (backend/utils/config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    anthropic_model: str = "claude-haiku-4-5-20251001"
    korean_dict_api_key: str
    korean_dict_api_url: str = "https://stdict.korean.go.kr/api/search.do"
    timer_duration: int = 15
    max_combo: int = 5

    class Config:
        env_file = ".env"
```
