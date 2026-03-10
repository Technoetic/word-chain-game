<div align="center">

# 끝말잇기 vs AI

### 음성으로 AI와 대결하는 한국어 끝말잇기

<br>

🎙️ **"사과"** → 🤖 **"과일"** → 🎙️ **"일출"** → **...**

**Claude Haiku** | **Deepgram STT** | **국립국어원 사전** | **FastAPI WebSocket**

<br>

### [🎮 지금 플레이하기](https://web-production-8d608.up.railway.app/)

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com)

---

</div>

<br>

## 게임 흐름

```mermaid
flowchart LR
    subgraph Player ["🎙️ 플레이어"]
        A["음성으로\n단어 입력"]
    end

    subgraph Timer ["⏱️ 타이머"]
        B["15초"]
    end

    subgraph AI ["🤖 AI (Claude)"]
        C["스트리밍\n한글자씩 응답"]
    end

    subgraph Validate1 ["검증"]
        D["국립국어원\n사전 검증"]
    end

    subgraph Validate2 ["검증"]
        E["국립국어원\n사전 검증"]
    end

    A -->|단어 제출| B --> C
    A --> D
    C --> E

    style Player fill:#4fc3f7,color:#000
    style AI fill:#ff7043,color:#000
    style Timer fill:#ffd54f,color:#000
```

> 💀 **한방 단어** 사용 시 → AI가 짜증 리액션 생성!
> ⏰ **15초** 초과 시 → 패배

<br>

## 시스템 아키텍처

```mermaid
flowchart TB
    subgraph Browser ["📱 브라우저 (Frontend)"]
        STT_UI["🎙️ STT\nDeepgram"]
        GAME_UI["🎮 게임 UI\nWebSocket"]
    end

    subgraph Server ["⚡ FastAPI Backend"]
        STT_PROXY["STT Proxy"]
        WS_HANDLER["WebSocket\nHandlers"]
        ENGINE["Game Engine\n(State / Rules / Korean)"]
    end

    subgraph APIs ["External APIs"]
        DEEPGRAM["Deepgram API"]
        CLAUDE["Claude API"]
        DICT["국립국어원\n사전 API"]
    end

    STT_UI -->|wss://| STT_PROXY
    GAME_UI -->|wss://| WS_HANDLER
    WS_HANDLER --> ENGINE
    STT_PROXY --> DEEPGRAM
    ENGINE --> CLAUDE
    ENGINE --> DICT

    style Browser fill:#e3f2fd,color:#000
    style Server fill:#fff3e0,color:#000
    style APIs fill:#fce4ec,color:#000
```

<br>

## 핵심 기능

### 🎙️ 음성 입력 (STT)

```mermaid
flowchart LR
    A["🎙️ 마이크 클릭"] --> B["PCM 오디오\n캡처"] --> C["WebSocket"] --> D["Deepgram\nNova-2"]
    D --> E["interim:\n사 → 사과"]
    D --> F["final:\n사과 ✅"]

    style A fill:#4fc3f7,color:#000
    style D fill:#66bb6a,color:#000
    style F fill:#66bb6a,color:#000
```

### 🤖 AI 응답 (스트리밍)

```mermaid
flowchart TD
    A["사용자: 사과"] --> B["마지막 글자: 과"]
    B --> C["Claude Haiku\n'과'로 시작하는 명사 생성"]
    C --> D["과 → 과일"]
    D --> E{"사전 검증\n통과?"}
    E -->|✅ Yes| F["전송"]
    E -->|❌ No| G["재시도\n(15초까지 반복)"]
    G --> C

    style C fill:#ff7043,color:#000
    style F fill:#66bb6a,color:#000
    style G fill:#ef5350,color:#fff
```

### 💀 한방 단어 시스템

```mermaid
flowchart LR
    subgraph Killer ["한방 글자"]
        K["럽 릎 듐 륨 늄 늅 뀨 쀼 튐"]
    end

    A["사용자: 시럽"] -->|끝글자 '럽'| B{"'럽'으로 시작하는\n단어가 거의 없음!"}
    B --> C["🤖 AI: 아 ㅅㅂ...\n(LLM이 생성)"]

    style Killer fill:#ef5350,color:#fff
    style C fill:#ff7043,color:#000
```

<br>

## 메시지 프로토콜 (WebSocket)

```mermaid
sequenceDiagram
    participant C as 📱 Client
    participant S as 🖥️ Server

    C->>S: game_start {difficulty}
    S->>C: game_started {session_id}

    C->>S: word_submit {word}
    S->>C: word_result {valid, killer}

    rect rgb(255, 235, 238)
        Note over C,S: 한방 단어인 경우
        S->>C: ai_reaction {START}
        S->>C: ai_reaction {"아"}
        S->>C: ai_reaction {"ㅅㅂ"}
        S->>C: ai_reaction {END}
    end

    S->>C: llm_typing {START}
    S->>C: llm_typing {"과"}
    S->>C: llm_typing {"일"}
    S->>C: llm_complete {"과일"}

    Note over C,S: ... 반복 ...

    S->>C: game_over {winner, reason}
```

<br>

## 단어 검증 파이프라인

```mermaid
flowchart TD
    A["입력: 사과"] --> B{"2글자 이상?"}
    B -->|❌| X1["거부"]
    B -->|✅| C{"이미 사용?"}
    C -->|❌ 사용됨| X2["거부"]
    C -->|✅ 미사용| D{"끝말잇기 규칙 충족?\n(두음법칙)"}
    D -->|❌| X3["거부"]
    D -->|✅| E{"LRU 캐시"}
    E -->|HIT| F["즉시 반환"]
    E -->|MISS| G{"국립국어원 API 조회\n(명사 확인)"}
    G -->|❌| X4["거부: 사전에 없는 단어"]
    G -->|✅| H["✅ 유효한 단어!"]

    style A fill:#4fc3f7,color:#000
    style H fill:#66bb6a,color:#000
    style X1 fill:#ef5350,color:#fff
    style X2 fill:#ef5350,color:#fff
    style X3 fill:#ef5350,color:#fff
    style X4 fill:#ef5350,color:#fff
```

<br>

## 두음법칙 처리

| 원래 글자 | 허용되는 시작 글자 |
|:---------:|:-----------------:|
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

> **예시:** "여료" → '료'로 끝남 → "요리" (료→요) 허용! ✅

<br>

## 프로젝트 구조

```
word-chain-game/
│
├── 📄 Procfile                 ← Railway 배포 설정
├── 📄 requirements.txt         ← Python 의존성
│
├── 📁 backend/
│   ├── 🚀 main.py              ← FastAPI 앱 진입점
│   │
│   ├── 📁 game/                 ← 게임 로직
│   │   ├── engine.py            ← 게임 엔진 (턴 관리, AI 응답)
│   │   ├── state.py             ← 게임 상태 (Pydantic 모델)
│   │   └── rules.py             ← 게임 규칙 검증
│   │
│   ├── 📁 llm/                  ← AI 연동
│   │   ├── service.py           ← Claude API 스트리밍
│   │   └── prompt_builder.py    ← 프롬프트 생성기
│   │
│   ├── 📁 dictionary/           ← 사전 검증
│   │   ├── validator.py         ← 단어 유효성 검사
│   │   ├── korean_api_client.py ← 국립국어원 API
│   │   └── cache.py             ← LRU 캐시
│   │
│   ├── 📁 websocket/            ← 실시간 통신
│   │   ├── handlers.py          ← 메시지 라우터
│   │   ├── manager.py           ← 연결 관리자
│   │   └── messages.py          ← 메시지 스키마
│   │
│   ├── 📁 stt/                  ← 음성 인식
│   │   └── deepgram_proxy.py    ← Deepgram WebSocket 프록시
│   │
│   └── 📁 utils/                ← 유틸리티
│       ├── korean.py            ← 한글 처리 (두음법칙, 한방글자)
│       └── config.py            ← 환경 변수 설정
│
└── 📁 dist/
    └── index.html               ← 프론트엔드 번들 (단일 파일)
```

<br>

## 기술 스택

```mermaid
block-beta
    columns 3

    block:frontend["Frontend"]:3
        A["Vanilla JS"] B["Web Audio API"] C["WebSocket Client"] D["CSS Animations"]
    end

    block:backend["Backend"]:3
        E["FastAPI"] F["Uvicorn ASGI"] G["Pydantic Settings"] H["aiohttp"]
    end

    block:apis["External APIs"]:3
        I["Claude Haiku\n(Anthropic)\nAI 단어생성"]
        J["Deepgram Nova-2\n(STT)\n음성→텍스트"]
        K["국립국어원\n한국어기초사전\n단어 검증"]
    end

    style frontend fill:#e3f2fd,color:#000
    style backend fill:#fff3e0,color:#000
    style apis fill:#fce4ec,color:#000
```

<br>

## 배포

### Railway (권장)

```bash
# 1. GitHub 리포 연결 후 환경 변수 설정
ANTHROPIC_API_KEY=sk-...
ANTHROPIC_BASE_URL=              # 선택사항 (프록시 사용 시)
DEEPGRAM_API_KEY=...
KOREAN_DICT_API_KEY=...
```

### 로컬 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp backend/.env.example .env
# .env 파일에 API 키 입력

# 3. 서버 실행
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 4. 브라우저에서 접속
# http://localhost:8000
```

### 환경 변수

| 변수 | 필수 | 설명 |
|------|:----:|------|
| `ANTHROPIC_API_KEY` | ✅ | Claude API 키 |
| `KOREAN_DICT_API_KEY` | ✅ | 국립국어원 API 키 |
| `DEEPGRAM_API_KEY` | ✅ | Deepgram STT API 키 |
| `ANTHROPIC_BASE_URL` | | API 프록시 URL (선택) |

<br>

## 게임 규칙

1. 상대방 단어의 마지막 글자로 시작하는 **2글자 이상**의 한국어 명사를 말한다
2. **국립국어원 사전**에 등재된 단어만 인정
3. 이미 사용한 단어는 **재사용 불가**
4. **두음법칙** 적용 (려→여, 류→유 등)
5. **15초** 안에 답하지 못하면 패배
6. AI도 동일한 규칙 적용 — 15초 타임아웃

<br>

---

<div align="center">

Built with **Claude Haiku** + **FastAPI** + **Deepgram**

</div>
