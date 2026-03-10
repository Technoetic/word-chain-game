# Step 18 - 코드 리뷰 결과

## Critical Issues (즉시 수정 필요)

### Backend
1. **engine.py**: GameState.used_words가 list인데 .add() 호출 → list.append()로 변경 또는 Set 사용
2. **engine.py**: self.state.is_user_turn 미존재 → current_turn 사용
3. **engine.py**: scoring.calculate_score() → calculate()로 메서드명 수정
4. **engine.py**: validator 결과가 dict인데 bool로 체크 → result['valid'] 사용
5. **engine.py**: apply_dueum() 반환이 list인데 string으로 사용 → [0] 또는 적절히 처리
6. **service.py**: 동기 Anthropic client를 async 함수에서 사용 → 블로킹 I/O 문제

### Frontend
7. **GameBoard.js**: STTController 메서드명 불일치 (onInterimText→존재하지 않음)
8. **main.js**: wsClient.onError(), onClose() 미존재 → on() 메서드 사용
9. **모든 UI 컴포넌트**: DOM querySelector null 체크 누락

## Major Issues
1. **messages.py**: WSMessage 상속 불일치
2. **manager.py**: word_validator, llm_service 속성 미정의
3. **handlers.py**: manager.word_validator 동적 접근
4. **WebSocketClient.js**: reconnect 재귀 스택오버플로 가능
5. **GameEngine.js**: 이벤트명 불일치

## 수정 우선순위
1. engine.py (6개 critical)
2. main.js + GameBoard.js (메서드명 불일치)
3. service.py (async/sync 이슈)
4. UI 컴포넌트 null 체크
