# Step 04 - 전체 조사 결과 (1/2)

## 출처
- 스크린샷: .claude/screenshots/research-1.png ~ research-5.png
- 원본 데이터: .claude/research-raw-1.txt ~ research-raw-5.txt
- 수집 방법: Playwright (chromium)

## 1. Web Speech API (SpeechRecognition)

출처: https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition
스크린샷: .claude/screenshots/research-1.png
원본: .claude/research-raw-1.txt

### 핵심 정보
- SpeechRecognition은 Web Speech API의 음성인식 컨트롤러 인터페이스
- Chrome에서는 서버 기반 인식 엔진 사용 (오프라인 미지원)
- EventTarget을 상속

### 주요 속성
- `lang`: 인식 언어 설정 (한국어: 'ko-KR')
- `continuous`: 연속 인식 여부 (기본값 false)
- `interimResults`: 중간 결과 반환 여부 (기본값 false)
- `maxAlternatives`: 대안 결과 최대 수 (기본값 1)
- `processLocally` (실험적): 로컬 장치에서 인식 수행

### 주요 메서드
- `start()`: 음성 인식 시작
- `stop()`: 인식 중지 후 결과 반환
- `abort()`: 인식 중단 (결과 없음)

### 이벤트 (11개)
- 라이프사이클: start, audiostart, soundstart, speechstart, speechend, soundend, audioend, end
- 결과: result, nomatch, error

### 프로젝트 적용
- `continuous: true`로 연속 인식
- `interimResults: true`로 실시간 중간 결과 표시
- `lang: 'ko-KR'`로 한국어 설정
- `result` 이벤트에서 transcript 추출

## 2. FastAPI WebSocket

출처: https://fastapi.tiangolo.com/advanced/websockets/
스크린샷: .claude/screenshots/research-2.png
원본: .claude/research-raw-2.txt

### 핵심 정보
- `pip install websockets` 필요
- `@app.websocket("/ws")` 데코레이터로 엔드포인트 생성
- `await websocket.accept()` → `receive_text()` → `send_text()` 패턴

### ConnectionManager 패턴
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket):
        await websocket.send_text(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_text(message)
```

### 연결 해제 처리
- `WebSocketDisconnect` 예외 catch
- 다중 클라이언트 관리 가능

### 프로젝트 적용
- 게임 세션당 1개 WebSocket 연결
- JSON 메시지 교환 (game_start, word_submit, llm_response 등)
- ConnectionManager로 연결 관리
