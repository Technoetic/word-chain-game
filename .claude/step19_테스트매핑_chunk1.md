# Step 19 - 테스트 파일 매핑 (Backend)

## 테스트 프레임워크
- Backend: pytest + pytest-asyncio
- Mock: unittest.mock (AsyncMock)

## Backend 테스트 매핑

### Group A: 순수 함수 (외부 의존성 없음, Mock 불필요)

| # | 구현 파일 | 테스트 파일 | 복잡도 | 핵심 테스트 |
|---|-----------|-------------|--------|------------|
| 1 | backend/utils/korean.py | tests/backend/test_korean.py | 낮음 | get_last_char, get_initial_jamo, apply_dueum, is_valid_chain |
| 2 | backend/game/scoring.py | tests/backend/test_scoring.py | 낮음 | calculate, get_combo_multiplier, is_killer_word |
| 3 | backend/game/rules.py | tests/backend/test_rules.py | 낮음 | validate_chain, is_word_used, is_valid_length |
| 4 | backend/game/state.py | tests/backend/test_state.py | 낮음 | GameState 기본값, WordResult 생성 |
| 5 | backend/llm/prompt_builder.py | tests/backend/test_prompt_builder.py | 낮음 | build_system, build_user |

### Group B: Mock 필요 (외부 API/서비스 의존)

| # | 구현 파일 | 테스트 파일 | 복잡도 | Mock 대상 |
|---|-----------|-------------|--------|-----------|
| 6 | backend/dictionary/cache.py | tests/backend/test_cache.py | 낮음 | 없음 (순수) |
| 7 | backend/dictionary/validator.py | tests/backend/test_validator.py | 중간 | KoreanAPIClient, WordCache |
| 8 | backend/dictionary/korean_api_client.py | tests/backend/test_korean_api_client.py | 중간 | aiohttp.ClientSession |
| 9 | backend/llm/service.py | tests/backend/test_llm_service.py | 높음 | anthropic.Anthropic |
| 10 | backend/game/engine.py | tests/backend/test_engine.py | 높음 | WordValidator, LLMService |
| 11 | backend/websocket/manager.py | tests/backend/test_manager.py | 중간 | WebSocket |
| 12 | backend/websocket/handlers.py | tests/backend/test_handlers.py | 높음 | WebSocket, ConnectionManager |

## 서브에이전트 배정: 12개 (backend)
