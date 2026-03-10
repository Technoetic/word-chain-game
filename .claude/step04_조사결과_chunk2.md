# Step 04 - 전체 조사 결과 (2/2)

## 3. Claude API 스트리밍

출처: https://docs.anthropic.com/en/api/messages-streaming
스크린샷: .claude/screenshots/research-3.png
원본: .claude/research-raw-3.txt

### 핵심 정보
- `"stream": true` 설정으로 SSE(Server-Sent Events) 스트리밍
- Python, TypeScript, Go, Java 등 다양한 SDK 지원

### 이벤트 흐름
1. `message_start` - 초기 Message 객체
2. `content_block_start` - 콘텐츠 블록 시작
3. `content_block_delta` - 텍스트 델타 (한 글자씩)
4. `content_block_stop` - 블록 종료
5. `message_delta` - 토큰 사용량 등
6. `message_stop` - 완료
7. `ping` - 연결 유지

### 텍스트 델타 형식
```json
{"type": "text_delta", "text": "..."}
```

### 프로젝트 적용
- Python SDK로 스트리밍 호출
- 한 글자씩 WebSocket으로 클라이언트에 전달 (타이핑 효과)
- Claude Haiku 4.5 사용 (빠른 응답 속도)

## 4. 한국어 끝말잇기 규칙

출처: https://ko.wikipedia.org/wiki/끝말잇기
스크린샷: .claude/screenshots/research-4.png
원본: .claude/research-raw-4.txt

### 기본 규칙
- 이전 단어의 마지막 글자로 시작하는 명사를 말하는 놀이
- 한 번 말한 단어 재사용 불가
- 국어사전에 없는 단어 불가
- 고유명사 불가
- 한 글자 단어 불가

### 두음법칙 (핵심)
- 한국어는 ㄴ/ㄹ/ㅇ 초성으로 시작하는 단어가 적음
- 두음법칙 적용 선택적
- ㄴ → ㅇ: 녀→여, 뇨→요, 뉴→유, 니→이
- ㄹ → ㅇ/ㄴ: 려→여, 례→예, 료→요, 류→유, 리→이, 라→나, 래→내
- 예: 스위스→스릴→일거리, 법도→도로→노동자

### 공격 단어 (한 방 단어)
- 마지막 글자로 시작하는 단어가 없는/적은 단어
- 예: 부엌, 북녘, 새벽녘, 소듐, 이리듐

### 방어 단어
- 공격 단어에 대응하는 희귀 단어
- 예: 슭곰, 븨피, 늣치

### 프로젝트 적용
- 두음법칙 기본 적용 (선택 옵션)
- 명사만 허용, 동사/형용사 제외
- 2글자 이상만 허용
- 한 방 단어 보너스 점수 시스템

## 5. 국립국어원 표준국어대사전 API

출처: https://stdict.korean.go.kr/openapi/openApiInfo.do
스크린샷: .claude/screenshots/research-5.png
원본: .claude/research-raw-5.txt

### API 엔드포인트
- URL: https://stdict.korean.go.kr/api/search.do
- 인증: 16진수 32자리 인증 키 필수

### 주요 요청 변수
| 변수 | 타입 | 필수 | 설명 |
|------|------|------|------|
| key | string | 필수 | 인증 키 |
| q | string | 필수 | 검색어 (UTF-8) |
| req_type | string | 선택 | xml 또는 json (기본: xml) |
| start | integer | 선택 | 시작 번호 1~1000 (기본: 1) |
| num | integer | 선택 | 결과 건수 10~100 (기본: 10) |

### 자세히 찾기 (advanced=y)
- target: 찾을 대상 (1:표제어, 8:뜻풀이 등)
- method: 검색 방식 (exact/include/start/end/wildcard)
- pos: 품사 (15개 카테고리)

### 프로젝트 적용
- `method=exact`로 정확한 단어 존재 확인
- `req_type=json`으로 JSON 응답
- 품사(pos) 필터로 명사만 검증
- 인증 키 발급 필요 (환경변수로 관리)

### 에러 코드
- 020: 미등록 키
- 100: 잘못된 검색어
- 102~217: 각종 파라미터 오류
