# Step 10 - 구현 파일 인덱스

## 신규 파일 목록 (전부 신규, Write로 생성)

### 그룹 A: Backend 핵심 (서브에이전트 1)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| A1 | backend/utils/config.py | 30 | 낮음 |
| A2 | backend/utils/korean.py | 80 | 중간 |
| A3 | backend/game/state.py | 40 | 낮음 |
| A4 | backend/game/rules.py | 100 | 중간 |
| A5 | backend/game/scoring.py | 50 | 낮음 |

### 그룹 B: Backend API/서비스 (서브에이전트 2)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| B1 | backend/dictionary/cache.py | 40 | 낮음 |
| B2 | backend/dictionary/korean_api_client.py | 60 | 중간 |
| B3 | backend/dictionary/validator.py | 80 | 중간 |
| B4 | backend/llm/prompt_builder.py | 40 | 낮음 |
| B5 | backend/llm/service.py | 80 | 높음 |

### 그룹 C: Backend WebSocket/Main (서브에이전트 3)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| C1 | backend/websocket/messages.py | 60 | 낮음 |
| C2 | backend/websocket/manager.py | 60 | 중간 |
| C3 | backend/websocket/handlers.py | 120 | 높음 |
| C4 | backend/game/engine.py | 150 | 높음 |
| C5 | backend/main.py | 80 | 중간 |
| C6 | backend/requirements.txt | 10 | 낮음 |

### 그룹 D: Frontend 유틸/게임 (서브에이전트 4)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| D1 | src/js/utils/constants.js | 30 | 낮음 |
| D2 | src/js/utils/eventBus.js | 30 | 낮음 |
| D3 | src/js/utils/koreanUtils.js | 60 | 중간 |
| D4 | src/js/game/GameState.js | 60 | 낮음 |
| D5 | src/js/game/ScoringSystem.js | 40 | 낮음 |
| D6 | src/js/game/GameEngine.js | 120 | 높음 |
| D7 | src/js/config.js | 20 | 낮음 |

### 그룹 E: Frontend STT/WebSocket (서브에이전트 5)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| E1 | src/js/stt/SpeechRecognitionManager.js | 100 | 높음 |
| E2 | src/js/stt/STTController.js | 60 | 중간 |
| E3 | src/js/websocket/WebSocketClient.js | 100 | 높음 |
| E4 | src/js/websocket/MessageHandler.js | 60 | 중간 |

### 그룹 F: Frontend UI 컴포넌트 (서브에이전트 6)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| F1 | src/js/ui/Timer.js | 80 | 중간 |
| F2 | src/js/ui/ScoreBoard.js | 50 | 낮음 |
| F3 | src/js/ui/ComboDisplay.js | 50 | 낮음 |
| F4 | src/js/ui/ParticleEffect.js | 100 | 중간 |
| F5 | src/js/ui/WordHistory.js | 80 | 중간 |
| F6 | src/js/ui/WordInput.js | 100 | 높음 |
| F7 | src/js/ui/GameOverModal.js | 60 | 낮음 |
| F8 | src/js/ui/GameBoard.js | 120 | 높음 |
| F9 | src/js/main.js | 60 | 중간 |

### 그룹 G: CSS (서브에이전트 7)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| G1 | src/css/reset.css | 30 | 낮음 |
| G2 | src/css/theme.css | 50 | 낮음 |
| G3 | src/css/layout.css | 80 | 중간 |
| G4 | src/css/animations.css | 100 | 중간 |
| G5 | src/css/components/game-board.css | 40 | 낮음 |
| G6 | src/css/components/word-input.css | 60 | 중간 |
| G7 | src/css/components/word-history.css | 60 | 중간 |
| G8 | src/css/components/timer.css | 60 | 중간 |
| G9 | src/css/components/score-board.css | 40 | 낮음 |
| G10 | src/css/components/modal.css | 50 | 낮음 |

### 그룹 H: HTML (서브에이전트 8)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| H1 | src/index.html | 120 | 중간 |

### 그룹 I: 환경 설정 (서브에이전트 9)
| # | 파일 | 예상 줄수 | 복잡도 |
|---|------|----------|--------|
| I1 | backend/.env.example | 10 | 낮음 |
| I2 | .editorconfig | 15 | 낮음 |
| I3 | .gitignore | 20 | 낮음 |

### __init__.py 파일 (자동 생성)
- backend/__init__.py
- backend/game/__init__.py
- backend/llm/__init__.py
- backend/dictionary/__init__.py
- backend/websocket/__init__.py
- backend/utils/__init__.py
- backend/models/__init__.py

## 의존성 순서
1. I (환경설정) → 독립
2. A (Backend 핵심) → 독립
3. B (Backend API) → A에 의존
4. C (Backend WS/Main) → A, B에 의존
5. D (Frontend 유틸/게임) → 독립
6. E (Frontend STT/WS) → D에 의존
7. G (CSS) → 독립
8. F (Frontend UI) → D, E, G에 의존
9. H (HTML) → G에 의존

## 서브에이전트 배정 요약
- 총 9개 그룹, 9개 서브에이전트
- 독립 그룹 (A, D, G, I) 병렬 실행 가능
- 의존 그룹은 순차 실행
