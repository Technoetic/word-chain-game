<div align="center">

# 끝말잇기 vs AI

음성 기반 실시간 끝말잇기 대전

`사과 → 과일 → 일출 → ...`

<br>

<img src="https://img.shields.io/badge/Claude_Haiku-191919?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude"> <img src="https://img.shields.io/badge/Deepgram-13EF93?style=for-the-badge&logo=deepgram&logoColor=black" alt="Deepgram"> <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"> <img src="https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=socketdotio&logoColor=white" alt="WebSocket"> <img src="https://img.shields.io/badge/국립국어원-FFFFFF?style=for-the-badge" alt="국립국어원">

<br>

[![Live Demo](https://img.shields.io/badge/Live_Demo-FF6B6B?style=for-the-badge&logo=googlechrome&logoColor=white)](https://web-production-8d608.up.railway.app/) [![Deploy on Railway](https://img.shields.io/badge/Deploy_on_Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.com)

---

</div>

## Game Flow

```mermaid
flowchart LR
    A["🎤 음성 입력"] -->|15s 제한| B["검증"]
    B --> C["🤖 AI 스트리밍 응답"]
    C -->|15s 제한| A
```

- 한방 단어 → AI 리액션 (LLM 실시간 생성)
- 타임아웃 → 패배

## Architecture

```mermaid
flowchart TB
    subgraph Client
        STT["🎤 STT · Deepgram"]
        UI["🎮 Game UI · WebSocket"]
    end

    subgraph Server["⚙️ FastAPI"]
        PROXY["STT Proxy"]
        WS["WebSocket Handler"]
        ENGINE["Game Engine"]
    end

    subgraph External
        DG["Deepgram"]
        CL["Claude"]
        KR["국립국어원"]
    end

    STT -->|wss| PROXY
    UI -->|wss| WS
    WS --> ENGINE
    PROXY --> DG
    ENGINE --> CL
    ENGINE --> KR
```

## STT Pipeline

```mermaid
flowchart LR
    A["🎤 Record"] --> B["PCM Capture"] --> C["WebSocket"] --> D["Deepgram Nova-2"]
    D --> E["interim: 사 → 사과"]
    D --> F["final: 사과 ✅"]
```

## AI Response

```mermaid
flowchart TD
    A["Input: 사과"] --> B["Last char: 과"]
    B --> C["Claude Haiku generates noun starting with '과'"]
    C --> D["과 → 과일"]
    D --> E{"Valid in dictionary?"}
    E -->|Yes| F["Send"]
    E -->|No| G["Retry"]
    G --> C
```

## 💀 Killer Words

> `럽 릎 듐 륨 늄 늅 뀨 쀼 튐`

이 글자로 끝나는 단어를 사용하면 AI가 이을 수 없음 → LLM이 짜증 리액션 생성

```mermaid
flowchart LR
    A["시럽"] -->|ends with 럽| B["No words start with 럽"]
    B --> C["🤖 AI: 아 ㅅㅂ..."]
```

## WebSocket Protocol

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    C->>S: game_start
    S->>C: game_started {session_id}

    C->>S: word_submit {word}
    S->>C: word_result {valid, killer}

    rect rgb(180, 60, 60)
        Note over C,S: Killer word detected
        S->>C: ai_reaction START
        S->>C: ai_reaction 아
        S->>C: ai_reaction ㅅㅂ
        S->>C: ai_reaction END
    end

    S->>C: llm_typing START → 과 → 일
    S->>C: llm_complete 과일

    S->>C: game_over
```

## Word Validation

```mermaid
flowchart TD
    A["Input"] --> B{"length >= 2?"}
    B -->|No| X1["Reject"]
    B -->|Yes| C{"Already used?"}
    C -->|Yes| X2["Reject"]
    C -->|No| D{"Chain rule + 두음법칙"}
    D -->|No| X3["Reject"]
    D -->|Yes| E{"LRU Cache"}
    E -->|Hit| F["Pass"]
    E -->|Miss| G{"국립국어원 API"}
    G -->|No| X4["Not in dictionary"]
    G -->|Yes| H["✅ Valid"]
```

## 두음법칙 (Initial Sound Rule)

| Original | Allowed |
|:--------:|:-------:|
| 녀 → 여 | 뇨 → 요 |
| 뉴 → 유 | 니 → 이 |
| 라 → 나 | 려 → 여 |
| 례 → 예 | 료 → 요 |
| 류 → 유 | 리 → 이 |

`여료 → ends with 료 → 요리 (료→요) accepted`

## Project Structure

```
word-chain-game/
├── Procfile
├── requirements.txt
├── backend/
│   ├── main.py
│   ├── game/
│   │   ├── engine.py
│   │   ├── state.py
│   │   └── rules.py
│   ├── llm/
│   │   ├── service.py
│   │   └── prompt_builder.py
│   ├── dictionary/
│   │   ├── validator.py
│   │   ├── korean_api_client.py
│   │   └── cache.py
│   ├── websocket/
│   │   ├── handlers.py
│   │   ├── manager.py
│   │   └── messages.py
│   ├── stt/
│   │   └── deepgram_proxy.py
│   └── utils/
│       ├── korean.py
│       └── config.py
└── dist/
    └── index.html
```

## Stack

| Layer | Tech | Logo |
|-------|------|-|
| Frontend | Vanilla JS, Web Audio, WebSocket | <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white"> |
| Backend | FastAPI, Uvicorn, Pydantic | <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"> |
| AI | Claude Haiku | <img src="https://img.shields.io/badge/Anthropic-191919?style=flat-square&logo=anthropic&logoColor=white"> |
| STT | Deepgram Nova-2 | <img src="https://img.shields.io/badge/Deepgram-13EF93?style=flat-square&logo=deepgram&logoColor=black"> |
| Dictionary | 국립국어원 API | <img src="https://i.namu.wiki/i/y5Vr1DQWFUTnHc8pX3DLNoewkGpbnxSAnPlWdCrQapFPsfwBSXpSqxVEyZZoP9MjeTz9eeEdlfrijs4C8MIh4Q.svg" height="20"> |
| Deploy | Railway | <img src="https://img.shields.io/badge/Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white"> |

## Setup

```bash
pip install -r requirements.txt
cp backend/.env.example .env
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

| Env | Required | Description |
|-----|:--------:|-------------|
| `ANTHROPIC_API_KEY` | ✓ | <img src="https://img.shields.io/badge/Anthropic-191919?style=flat-square&logo=anthropic&logoColor=white"> |
| `KOREAN_DICT_API_KEY` | ✓ | <img src="https://i.namu.wiki/i/y5Vr1DQWFUTnHc8pX3DLNoewkGpbnxSAnPlWdCrQapFPsfwBSXpSqxVEyZZoP9MjeTz9eeEdlfrijs4C8MIh4Q.svg" height="16"> |
| `DEEPGRAM_API_KEY` | ✓ | <img src="https://img.shields.io/badge/Deepgram-13EF93?style=flat-square&logo=deepgram&logoColor=black"> |
| `ANTHROPIC_BASE_URL` | | Proxy URL |

## Rules

1. 상대 단어의 마지막 글자로 시작하는 2글자 이상의 명사
2. 국립국어원 사전 등재 단어만 유효
3. 중복 사용 불가
4. 두음법칙 허용
5. 제한시간 15초
6. AI 동일 규칙 적용
