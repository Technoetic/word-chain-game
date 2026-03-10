<div align="center">

# 끝말잇기 vs AI

음성으로 AI한테 끝말잇기 걸 수 있음

`"사과" → "과일" → "일출" → ...`

Claude Haiku · Deepgram STT · 국립국어원 사전 · FastAPI WebSocket

<br>

### [▶ 플레이](https://web-production-8d608.up.railway.app/)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com)

---

</div>

## 어떻게 돌아가냐면

```mermaid
flowchart LR
    A["마이크로 말함"] -->|15초 안에| B["서버에서 검증"]
    B --> C["AI가 한글자씩 응답"]
    C -->|다시 15초| A
```

- 한방 단어 쓰면 AI가 욕함 (LLM이 실시간 생성)
- 15초 넘기면 짐

## 구조

```mermaid
flowchart TB
    subgraph 브라우저
        STT["STT · Deepgram"]
        UI["게임 UI · WebSocket"]
    end

    subgraph 서버["FastAPI"]
        PROXY["STT Proxy"]
        WS["WebSocket Handler"]
        ENGINE["Game Engine"]
    end

    subgraph 외부
        DG["Deepgram API"]
        CL["Claude API"]
        KR["국립국어원 API"]
    end

    STT -->|wss| PROXY
    UI -->|wss| WS
    WS --> ENGINE
    PROXY --> DG
    ENGINE --> CL
    ENGINE --> KR
```

## 음성 인식

```mermaid
flowchart LR
    A["마이크 클릭"] --> B["PCM 캡처"] --> C["WebSocket"] --> D["Deepgram Nova-2"]
    D --> E["중간 결과: 사 → 사과"]
    D --> F["최종: 사과"]
```

## AI 응답

```mermaid
flowchart TD
    A["유저: 사과"] --> B["끝글자: 과"]
    B --> C["Claude Haiku가 '과'로 시작하는 명사 생성"]
    C --> D["과 → 과일"]
    D --> E{"사전에 있음?"}
    E -->|ㅇㅇ| F["보냄"]
    E -->|ㄴㄴ| G["다시 시도"]
    G --> C
```

## 한방 단어

럽, 릎, 듐, 륨, 늄, 늅, 뀨, 쀼, 튐

이 글자로 끝나는 단어 쓰면 AI가 이을 수가 없음 → 짜증 리액션 나옴

```mermaid
flowchart LR
    A["시럽"] -->|끝글자 럽| B["럽으로 시작하는 단어 없음"]
    B --> C["AI: 아 ㅅㅂ..."]
```

## WebSocket 프로토콜

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    C->>S: game_start
    S->>C: game_started + session_id

    C->>S: word_submit
    S->>C: word_result (valid/killer)

    rect rgb(255, 235, 238)
        Note over C,S: 한방 단어일 때
        S->>C: ai_reaction START
        S->>C: ai_reaction 아
        S->>C: ai_reaction ㅅㅂ
        S->>C: ai_reaction END
    end

    S->>C: llm_typing START → 과 → 일
    S->>C: llm_complete 과일

    S->>C: game_over
```

## 단어 검증

```mermaid
flowchart TD
    A["입력"] --> B{"2글자 이상?"}
    B -->|no| X1["탈락"]
    B -->|yes| C{"이미 쓴 단어?"}
    C -->|yes| X2["탈락"]
    C -->|no| D{"끝말잇기 규칙 + 두음법칙"}
    D -->|no| X3["탈락"]
    D -->|yes| E{"캐시에 있음?"}
    E -->|hit| F["바로 통과"]
    E -->|miss| G{"국립국어원 API"}
    G -->|no| X4["사전에 없음"]
    G -->|yes| H["통과"]
```

## 두음법칙

| 원래 | 변환 |
|:----:|:----:|
| 녀 | 여 |
| 뇨 | 요 |
| 뉴 | 유 |
| 니 | 이 |
| 라 | 나 |
| 려 | 여 |
| 례 | 예 |
| 료 | 요 |
| 류 | 유 |
| 리 | 이 |

예: "여료" → 료로 끝남 → "요리" (료→요) OK

## 파일 구조

```
word-chain-game/
├── Procfile                    # Railway 배포
├── requirements.txt            # Python 의존성
├── backend/
│   ├── main.py                 # FastAPI 진입점
│   ├── game/
│   │   ├── engine.py           # 게임 엔진
│   │   ├── state.py            # 상태 관리
│   │   └── rules.py            # 규칙 검증
│   ├── llm/
│   │   ├── service.py          # Claude 스트리밍
│   │   └── prompt_builder.py   # 프롬프트
│   ├── dictionary/
│   │   ├── validator.py        # 단어 검증
│   │   ├── korean_api_client.py # 국립국어원 API
│   │   └── cache.py            # LRU 캐시
│   ├── websocket/
│   │   ├── handlers.py         # 메시지 라우팅
│   │   ├── manager.py          # 연결 관리
│   │   └── messages.py         # 메시지 스키마
│   ├── stt/
│   │   └── deepgram_proxy.py   # Deepgram 프록시
│   └── utils/
│       ├── korean.py           # 한글 처리
│       └── config.py           # 환경 변수
└── dist/
    └── index.html              # 프론트엔드 번들
```

## 기술 스택

| 구분 | 사용 |
|------|------|
| Frontend | Vanilla JS, Web Audio API, WebSocket, CSS Animations |
| Backend | FastAPI, Uvicorn, Pydantic, aiohttp |
| AI | Claude Haiku (Anthropic) |
| STT | Deepgram Nova-2 |
| 사전 | 국립국어원 한국어기초사전 API |

## 실행

```bash
pip install -r requirements.txt
cp backend/.env.example .env   # API 키 넣기
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

http://localhost:8000 접속

### 환경 변수

| 변수 | 필수 | 용도 |
|------|:----:|------|
| `ANTHROPIC_API_KEY` | O | Claude API |
| `KOREAN_DICT_API_KEY` | O | 국립국어원 API |
| `DEEPGRAM_API_KEY` | O | Deepgram STT |
| `ANTHROPIC_BASE_URL` | | 프록시 쓸 때 |

## 규칙

1. 상대 단어 끝글자로 시작하는 2글자 이상 명사
2. 국립국어원 사전에 있는 단어만
3. 한번 쓴 단어 다시 못 씀
4. 두음법칙 적용됨
5. 15초 안에 못 대면 짐
6. AI도 같은 규칙
