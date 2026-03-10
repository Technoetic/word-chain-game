# Step 24 - Dead Code 점검 결과

## 발견 및 수정
1. `src/js/utils/eventBus.js:33` - 미사용 전역 `const eventBus = new EventBus()` 제거 (main.js에서 새 인스턴스 생성)

## 확인 후 유지
1. `backend/models/` - 빈 디렉토리, 향후 확장용으로 유지
2. `backend/game/rules.py` - GameRules 클래스는 engine.py에서 사용
3. `backend/utils/korean.py:get_initial_jamo` - rules.py에서 사용
4. `src/js/game/GameEngine.js:setupEventListeners` - 향후 사용 가능성 유지

## 검증
- 264 backend tests ALL PASS 유지
