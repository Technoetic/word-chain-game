# Step 09 - 설계 (3/3): 통합 및 데이터 흐름

## 1. WebSocket 메시지 프로토콜

### 클라이언트 → 서버
```json
// 게임 시작
{"type": "game_start", "difficulty": "normal"}

// 단어 제출
{"type": "word_submit", "word": "사과"}
```

### 서버 → 클라이언트
```json
// 게임 시작 응답
{"type": "game_started", "session_id": "abc123", "first_word": "사과"}

// 단어 검증 결과 (성공)
{"type": "word_result", "valid": true, "word": "사과", "score": 200, "message": ""}

// 단어 검증 결과 (실패)
{"type": "word_result", "valid": false, "word": "ㅋㅋ", "score": 0, "message": "사전에 없는 단어입니다"}

// LLM 타이핑 (한글자씩)
{"type": "llm_typing", "char": "과"}

// LLM 응답 완료
{"type": "llm_complete", "word": "과학", "score": 200}

// 타이머 갱신
{"type": "timer_update", "remaining": 10}

// 게임 종료
{"type": "game_over", "winner": "user", "user_score": 3000, "llm_score": 2500}

// 에러
{"type": "error", "message": "서버 오류가 발생했습니다"}
```

## 2. 게임 시퀀스 다이어그램

```
[사용자]          [Frontend]         [WebSocket]        [Backend]          [Claude API]    [사전 API]
  |                  |                   |                  |                   |              |
  | 게임 시작 클릭    |                   |                  |                   |              |
  |----------------->|                   |                  |                   |              |
  |                  |--game_start------>|                  |                   |              |
  |                  |                   |--game_start----->|                   |              |
  |                  |                   |                  | GameEngine.start  |              |
  |                  |                   |<-game_started----|                   |              |
  |                  |<--game_started----|                  |                   |              |
  |                  | Timer.start()     |                  |                   |              |
  |                  |                   |                  |                   |              |
  | 마이크로 "사과"   |                   |                  |                   |              |
  |----------------->|                   |                  |                   |              |
  |                  | STT interim "사"  |                  |                   |              |
  |  <입력필드 갱신>  |                   |                  |                   |              |
  |                  | STT final "사과"  |                  |                   |              |
  |                  |                   |                  |                   |              |
  | Enter 제출       |                   |                  |                   |              |
  |----------------->|                   |                  |                   |              |
  |                  |--word_submit----->|                  |                   |              |
  |                  |                   |--word_submit---->|                   |              |
  |                  |                   |                  |--validate-------->|              |
  |                  |                   |                  |                   |  search(사과)|
  |                  |                   |                  |                   |              |
  |                  |                   |                  |<--valid, 명사-----|              |
  |                  |                   |                  | score = 200      |              |
  |                  |                   |<-word_result-----|                   |              |
  |                  |<--word_result-----|                  |                   |              |
  |  <점수+히스토리>  |                   |                  |                   |              |
  |                  |                   |                  |                   |              |
  |                  |                   |                  |--stream_word('과')-->|           |
  |                  |                   |                  |<--'과'(delta)-------|           |
  |                  |                   |<-llm_typing------|                   |              |
  |                  |<--llm_typing------|                  |<--'학'(delta)-------|           |
  |                  |                   |<-llm_typing------|                   |              |
  |  <AI 타이핑 효과> |                   |                  |<--완료-------------|           |
  |                  |                   |                  |--validate-------->|              |
  |                  |                   |                  |                   |  search(과학)|
  |                  |                   |                  |<--valid-----------|              |
  |                  |                   |<-llm_complete----|                   |              |
  |                  |<--llm_complete----|                  |                   |              |
  |  <AI 단어 확정>   |                   |                  |                   |              |
  |                  | Timer.reset()     |                  |                   |              |
  |                  | Timer.start()     |                  |                   |              |
  |                  |                   |                  |                   |              |
  | ... 반복 ...      |                   |                  |                   |              |
  |                  |                   |                  |                   |              |
  |  타이머 만료      |                   |                  |                   |              |
  |                  |--timer_expired--->|                  |                   |              |
  |                  |                   |--timer_expired-->|                   |              |
  |                  |                   |<-game_over-------|                   |              |
  |                  |<--game_over-------|                  |                   |              |
  |  <게임오버 모달>  |                   |                  |                   |              |
```

## 3. STT → 제출 → 검증 흐름

```
1. 사용자가 마이크 버튼 클릭
   → STTController.toggleListening()
   → SpeechRecognitionManager.start()

2. 음성 인식 중 (interim)
   → result 이벤트 (isFinal=false)
   → SpeechRecognitionManager emit 'interim_result'
   → STTController → WordInput.setInterimText("사")
   → 입력 필드에 회색 텍스트 표시

3. 음성 인식 완료 (final)
   → result 이벤트 (isFinal=true)
   → SpeechRecognitionManager emit 'final_result'
   → STTController → WordInput.setFinalText("사과")
   → 입력 필드에 확정 텍스트

4. 제출
   → Enter 키 또는 제출 버튼
   → WordInput.onSubmit()
   → EventBus.emit('word_submitted', {word: '사과'})
   → GameEngine.submitWord('사과')
   → WebSocketClient.send('word_submit', {word: '사과'})

5. 백엔드 검증
   → WebSocketHandlers.handle_word_submit()
   → GameEngine.process_user_word('사과')
   → GameRules.validate_chain(lastWord, '사과')
   → GameRules.is_word_used('사과', usedWords)
   → WordValidator.validate('사과')
   → KoreanAPIClient.search('사과') → 사전 API 호출
   → 명사 확인 → 점수 계산

6. 결과 전송
   → ConnectionManager.send(session_id, word_result)
```

## 4. 에러 처리 전략

### Frontend
| 에러 유형 | 처리 방법 |
|-----------|-----------|
| STT 미지원 브라우저 | 알림 표시, 키보드 입력만 사용 |
| STT 권한 거부 | 알림 표시, 키보드 입력 안내 |
| WS 연결 실패 | 재연결 시도 (5회, 지수 백오프) |
| WS 연결 끊김 | 오버레이 표시 + 재연결 |
| 유효하지 않은 단어 | 입력 흔들림 + 빨간 플래시 + 메시지 |
| 타이머 만료 | 자동 게임 종료 |

### Backend
| 에러 유형 | 처리 방법 |
|-----------|-----------|
| 사전 API 오류 | 캐시 조회 → 없으면 에러 메시지 |
| 사전 API 타임아웃 | 3초 타임아웃, 재시도 1회 |
| Claude API 오류 | AI 포기 처리 (사용자 승리) |
| Claude API Rate Limit | 대기 후 재시도 → 실패 시 포기 |
| 잘못된 WS 메시지 | 에러 메시지 응답 |
| 세션 없음 | 새 세션 생성 안내 |

## 5. 타이머 동기화

### 프론트엔드 타이머
- JavaScript setInterval (1초 간격)
- UI 업데이트 (원형 프로그레스, 숫자)
- 5초 이하: 빨간색 + 펄스
- 0초: game_over 전송

### 백엔드 검증
- 단어 제출 시 서버 타임스탬프 확인
- 턴 시작 시간 기록
- 제출 시간 - 시작 시간 > 15초 → 거부
- 클라이언트 타이머와 1-2초 오차 허용

## 6. 색상 테마 (CSS 변수)

```css
:root {
  --bg-primary: #0f0f23;
  --bg-secondary: #1a1a2e;
  --text-primary: #e0e0e0;
  --user-color: #4fc3f7;
  --ai-color: #ff7043;
  --success: #66bb6a;
  --error: #ef5350;
  --combo: #ffd54f;
  --timer-safe: #66bb6a;
  --timer-warn: #ffa726;
  --timer-danger: #ef5350;
}
```
