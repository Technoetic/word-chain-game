# Step 09 - 설계 (1/3): Frontend 클래스

## 1. SpeechRecognitionManager
파일: src/js/stt/SpeechRecognitionManager.js

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| recognition | SpeechRecognition | 네이티브 객체 |
| isListening | boolean | 현재 듣고 있는지 |
| language | string | 'ko-KR' |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| constructor | language='ko-KR' | void | 초기화 |
| start | - | void | 음성 인식 시작 |
| stop | - | void | 중지 후 결과 반환 |
| abort | - | void | 중단 (결과 없음) |

### Events (CustomEvent dispatch)
- interim_result: {text: string}
- final_result: {text: string}
- stt_error: {error: string}
- listening_change: {isListening: boolean}

## 2. STTController
파일: src/js/stt/STTController.js

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| sttManager | SpeechRecognitionManager | STT 인스턴스 |
| wordInput | WordInput | 입력 컴포넌트 참조 |
| isEnabled | boolean | STT 사용 가능 여부 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| constructor | wordInput | void | 초기화 |
| toggleListening | - | void | STT 토글 |
| reset | - | void | 상태 초기화 |

## 3. GameEngine (Frontend)
파일: src/js/game/GameEngine.js

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| state | GameState | 게임 상태 |
| wsClient | WebSocketClient | 웹소켓 클라이언트 |
| eventBus | EventBus | 이벤트 버스 |
| isUserTurn | boolean | 사용자 턴 여부 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| constructor | wsClient, eventBus | void | 초기화 |
| startGame | difficulty='normal' | void | 게임 시작 요청 |
| submitWord | word: string | void | 단어 제출 |
| handleWordResult | data: object | void | 검증 결과 처리 |
| handleLLMTyping | data: object | void | LLM 타이핑 표시 |
| handleLLMComplete | data: object | void | LLM 응답 완료 |
| handleGameOver | data: object | void | 게임 종료 처리 |
| endGame | - | void | 게임 종료 |

## 4. GameState
파일: src/js/game/GameState.js

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| userScore | number | 사용자 점수 |
| llmScore | number | LLM 점수 |
| usedWords | Set | 사용된 단어 |
| combo | number | 연속 콤보 |
| lastWord | string | 마지막 단어 |
| turnCount | number | 턴 수 |
| isGameActive | boolean | 게임 진행 중 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| constructor | - | void | 초기 상태 |
| reset | - | void | 상태 초기화 |
| addWord | word, isUser | void | 단어 추가 |
| updateScore | isUser, points | void | 점수 갱신 |
| incrementCombo | - | void | 콤보 증가 |
| resetCombo | - | void | 콤보 초기화 |

## 5. ScoringSystem
파일: src/js/game/ScoringSystem.js

### Static Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| calculate | word, combo, timeLeft | number | 점수 계산 |
| getComboMultiplier | combo | number | 콤보 배율 |

### 점수 공식
- 기본: 단어길이 × 100
- 콤보: ×1, ×1.5, ×2, ×2.5, ×3 (max)
- 속도: 10초이상 +0, 5-10초 +200, 3-5초 +300, 3초미만 +500

## 6. WebSocketClient
파일: src/js/websocket/WebSocketClient.js

### Properties
| 이름 | 타입 | 설명 |
|------|------|------|
| socket | WebSocket | 네이티브 WS |
| url | string | 서버 URL |
| isConnected | boolean | 연결 상태 |
| handlers | Map | 메시지 핸들러 |
| reconnectAttempts | number | 재연결 시도 |

### Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| constructor | url | void | 초기화 |
| connect | - | Promise | 연결 |
| send | type, data | void | 메시지 전송 |
| on | type, handler | void | 핸들러 등록 |
| close | - | void | 연결 종료 |
| reconnect | - | Promise | 재연결 |

## 7. MessageHandler
파일: src/js/websocket/MessageHandler.js

### Static Methods
| 이름 | 파라미터 | 반환 | 설명 |
|------|----------|------|------|
| route | message, gameEngine | void | 메시지 라우팅 |

### 메시지 타입 상수
GAME_START, WORD_RESULT, LLM_TYPING, LLM_COMPLETE, GAME_OVER, ERROR, TIMER_UPDATE

## 8. UI 컴포넌트

### GameBoard (src/js/ui/GameBoard.js)
- container: HTMLElement
- components: {wordInput, wordHistory, timer, scoreBoard, comboDisplay}
- render(): 전체 UI 렌더링
- setupEventListeners(): 이벤트 바인딩

### WordInput (src/js/ui/WordInput.js)
- inputEl: HTMLInputElement
- submitBtn: HTMLButtonElement
- micBtn: HTMLButtonElement
- sttController: STTController
- setInterimText(text): 중간 결과 표시
- setFinalText(text): 확정 텍스트
- onSubmit(callback): 제출 콜백
- setEnabled(bool): 활성화 토글
- clear(): 입력 초기화
- shake(): 에러 애니메이션

### WordHistory (src/js/ui/WordHistory.js)
- container: HTMLElement
- words: Array
- addUserWord(word, score): 사용자 단어 추가
- addLLMTypingChar(char): LLM 타이핑 한글자
- finalizeLLMWord(word, score): LLM 단어 확정
- scrollToBottom(): 스크롤

### Timer (src/js/ui/Timer.js)
- element: HTMLElement
- duration: number (15)
- remaining: number
- intervalId: number
- start(): 카운트다운 시작
- stop(): 정지
- reset(): 초기화
- onExpired(callback): 만료 콜백
- (5초 이하: 빨간색+펄스, 3초 이하: 빠른 펄스+경고음)

### ScoreBoard (src/js/ui/ScoreBoard.js)
- userScoreEl, llmScoreEl: HTMLElement
- update(userScore, llmScore): 점수 갱신
- animateScore(element, oldVal, newVal): 점수 애니메이션

### ComboDisplay (src/js/ui/ComboDisplay.js)
- element: HTMLElement
- setCombo(count): 콤보 표시
- animate(): 펄스 애니메이션

### ParticleEffect (src/js/ui/ParticleEffect.js)
- static burst(x, y, color, count): 파티클 폭발
- static success(): 성공 파티클 (초록)
- static fail(): 실패 효과 (빨간 플래시)
- static combo(): 콤보 파티클 (황금)

### GameOverModal (src/js/ui/GameOverModal.js)
- overlay: HTMLElement
- show(result): 모달 표시 {winner, userScore, llmScore}
- hide(): 모달 숨기기
- onPlayAgain(callback): 재시작 콜백

## 9. 유틸리티

### EventBus (src/js/utils/eventBus.js)
- on(event, handler): 이벤트 구독
- off(event, handler): 구독 해제
- emit(event, data): 이벤트 발행

### KoreanUtils (src/js/utils/koreanUtils.js)
- getLastChar(word): 마지막 글자 추출
- applyDueum(char): 두음법칙 적용 (가능한 글자들 반환)
- isValidChain(prevWord, nextWord): 체인 유효성

### Constants (src/js/utils/constants.js)
- TIMER_DURATION, MAX_COMBO, WS_URL 등
