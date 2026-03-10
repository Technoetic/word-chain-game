# Step 06 - GitHub 조사 결과

## 출처
- 원본 데이터: .claude/research-raw-github1.txt ~ github3.txt
- 수집 방법: curl (GitHub API)

## 1. 한국어 끝말잇기 관련 레포지토리

검색어: 끝말잇기 (289개 결과)

### 주요 레포
| 레포 | 스타 | 언어 | 설명 |
|------|------|------|------|
| sam351/ggutmal | - | - | 팀원과 함께하는 끝말잇기 |
| Astro36/word-chain-bot | 7 | JavaScript | Korean Word Chain Bot |
| cheesedongjin/WordChainer | 1 | Python | AI 봇이 있는 끝말잇기 |
| pulqum/python-korean-word-chain-game | 0 | Jupyter | 파이썬 끝말잇기 (2020) |

### 참고할 패턴
- JavaScript 기반 봇 구현 (word-chain-bot)
- Python AI 기반 변형 (WordChainer)
- 교육용 프로젝트 (Jupyter notebook)

## 2. FastAPI WebSocket 게임 레포지토리

검색어: fastapi websocket game (76개 결과)

### 주요 레포
| 레포 | 스타 | 언어 | 설명 |
|------|------|------|------|
| olzhasar/pyws-chess | 39 | JS | 실시간 체스 (FastAPI + WebSocket) |
| datastaxdevs/workshop-streaming-game | 31 | Python | 멀티플레이어 게임 (FastAPI + React + WS) |
| beatcode-official/server | 21 | Python | LeetCode PvP (FastAPI + WebSocket) |
| VaiBhaVSinGh91/Art-Heist-Game | 10 | JS | 실시간 멀티플레이어 (FastAPI + React + WS) |
| tojatos/laser-tactics | 3 | Python | 웹 게임 (FastAPI + WebSocket) |

### 참고할 아키텍처 패턴
- FastAPI + React 조합이 가장 일반적
- WebSocket으로 실시간 플레이어 통신
- 인게임 채팅 지원
- Docker 컨테이너화 배포

## 3. 프로젝트 적용 시사점

- 끝말잇기 레포가 적고 스타도 낮아 독자적 구현 필요
- FastAPI WebSocket 게임 아키텍처는 검증된 패턴 존재
- React/JS 프론트 + FastAPI 백엔드 조합이 표준적
- ConnectionManager 패턴으로 WebSocket 연결 관리
- Docker 배포 고려
