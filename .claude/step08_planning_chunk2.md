# Step 08 - 기획 보완 (STT 통합 + 파일 구조)

## STT 통합 설계

### Web Speech API 흐름
1. 사용자가 마이크 버튼 클릭 → SpeechRecognition.start()
2. continuous: true, interimResults: true, lang: 'ko-KR'
3. interim result → 입력 필드에 실시간 표시 (회색 텍스트)
4. final result → 입력 필드에 확정 표시 (검은 텍스트)
5. Enter 키 또는 제출 버튼 → WebSocket으로 전송

### STT 클래스
- SpeechRecognitionManager: Web Speech API 래퍼
- STTController: STT 상태 관리 + WordInput 연동

## 파일 구조 확정

### Frontend (src/)
- index.html (엔트리)
- js/main.js, config.js
- js/game/ (GameEngine, GameState, ScoringSystem)
- js/stt/ (SpeechRecognitionManager, STTController)
- js/websocket/ (WebSocketClient, MessageHandler)
- js/ui/ (GameBoard, WordInput, WordHistory, Timer, ScoreBoard, ComboDisplay, ParticleEffect, GameOverModal)
- js/utils/ (koreanUtils, eventBus, constants)
- css/ (reset, theme, layout, animations, components/)

### Backend (backend/)
- main.py, requirements.txt
- game/ (engine, rules, scoring, state)
- llm/ (service, prompt_builder)
- dictionary/ (validator, korean_api_client, cache)
- websocket/ (manager, handlers, messages)
- utils/ (korean, config)

## 환경 변수
- ANTHROPIC_API_KEY
- KOREAN_DICT_API_KEY
- TIMER_DURATION=15
