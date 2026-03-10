# Step 07 - API 계약 문서 조사 결과

## 출처
- 스크린샷: .claude/screenshots/research-api1.png
- 원본 데이터: .claude/research-raw-api1.txt
- 수집 방법: Playwright (chromium)

## 1. Anthropic Claude API (Messages)

출처: https://docs.anthropic.com/en/api/messages

### 엔드포인트
- `POST /v1/messages` - 메시지 생성 (LLM 호출)
- `POST /v1/messages/count_tokens` - 토큰 카운트

### 요청 형식
```json
{
  "model": "claude-haiku-4-5-20251001",
  "max_tokens": 100,
  "stream": true,
  "messages": [
    {"role": "user", "content": "끝말잇기에서 '사과'의 마지막 글자 '과'로 시작하는 명사를 하나만 말해주세요."}
  ]
}
```

### 응답 형식 (비스트리밍)
```json
{
  "id": "msg_...",
  "model": "claude-haiku-4-5-20251001",
  "role": "assistant",
  "content": [{"type": "text", "text": "과학"}],
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 50, "output_tokens": 5}
}
```

### 스트리밍 이벤트
- message_start → content_block_start → content_block_delta (text) → content_block_stop → message_delta → message_stop

### 인증
- `x-api-key` 헤더에 API 키
- `anthropic-version` 헤더 필수

### 모델 선택
- claude-haiku-4-5-20251001 (빠른 응답, 끝말잇기에 적합)

## 2. 국립국어원 표준국어대사전 API

(Step 04에서 조사 완료, 요약 재기술)

### 엔드포인트
- `GET https://stdict.korean.go.kr/api/search.do`

### 요청 파라미터
- key: 인증 키 (필수)
- q: 검색어 (필수)
- req_type: json (선택)
- method: exact (정확 검색)
- advanced: y (자세히 찾기)
- pos: 1 (명사 필터)

### 프로젝트 활용
- 단어 존재 확인: method=exact
- 명사 확인: pos 필터
- JSON 응답: req_type=json

## 3. WebSocket 메시지 계약 (자체 정의)

### 클라이언트 → 서버
```json
{"type": "game_start", "difficulty": "normal"}
{"type": "word_submit", "word": "사과"}
```

### 서버 → 클라이언트
```json
{"type": "word_result", "valid": true, "word": "사과", "score": 200}
{"type": "llm_typing", "char": "과"}
{"type": "llm_complete", "word": "과학", "score": 200}
{"type": "game_over", "winner": "user", "total_score": 5000}
{"type": "error", "message": "사전에 없는 단어입니다"}
{"type": "timer_update", "remaining": 10}
```

## 4. REST API (보조)
- `GET /api/health` - 서버 상태 확인
- `GET /api/leaderboard` - 리더보드 (향후)
