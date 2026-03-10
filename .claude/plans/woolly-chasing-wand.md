# 끝말잇기 vs LLM - 구현 계획

## Context
STT(Speech-to-Text) 기반 끝말잇기 대전 게임. 사용자가 마이크로 말하면 Web Speech API를 통해 실시간 입력되고, Claude Haiku가 스트리밍으로 응수하는 웹 게임.

## 아키텍처
- Frontend: Vanilla JS (src/js/, src/css/, src/index.html)
- Backend: FastAPI + WebSocket (backend/)
- LLM: Claude Haiku 4.5 (스트리밍)
- STT: Web Speech API (브라우저)
- 단어 검증: 국립국어원 API
- 빌드: html-bundler.ps1 → dist/index.html

## 파일 구조
```
src/
  index.html
  js/
    main.js, config.js
    game/    GameEngine.js, GameState.js, ScoringSystem.js
    stt/     SpeechRecognitionManager.js, STTController.js
    websocket/ WebSocketClient.js, MessageHandler.js
    ui/      GameBoard.js, WordInput.js, WordHistory.js, Timer.js,
             ScoreBoard.js, ComboDisplay.js, ParticleEffect.js, GameOverModal.js
    utils/   koreanUtils.js, eventBus.js, constants.js
  css/
    reset.css, theme.css, layout.css, animations.css
    components/ game-board.css, word-input.css, word-history.css,
                timer.css, score-board.css, modal.css

backend/
  main.py, requirements.txt
  game/    engine.py, rules.py, scoring.py, state.py
  llm/     service.py, prompt_builder.py
  dictionary/ validator.py, korean_api_client.py, cache.py
  websocket/  manager.py, handlers.py, messages.py
  utils/   korean.py, config.py
```

## 핵심 흐름
1. 사용자 음성 → SpeechRecognition → interim/final result → WordInput 표시
2. Enter 제출 → WebSocket → FastAPI → WordValidator(국어원API) → 점수 계산
3. LLM 턴 → Claude Haiku 스트리밍 → 한글자씩 WebSocket → 타이핑 효과
4. 15초 타이머, 콤보, 파티클, 게임오버 모달

## 검증
- Backend: pytest (game engine, word validator, korean rules)
- Frontend: Playwright E2E
- 빌드: html-bundler.ps1 → dist/index.html
