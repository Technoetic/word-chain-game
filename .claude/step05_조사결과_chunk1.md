# Step 05 - UX/UI 조사 결과

## 출처
- 스크린샷: .claude/screenshots/research-ux1.png ~ research-ux3.png
- 원본 데이터: .claude/research-raw-ux1.txt ~ research-raw-ux3.txt
- 수집 방법: Playwright (chromium)

## 1. 워드 게임 UI 디자인 트렌드

출처: https://dribbble.com/search/word-game-ui
스크린샷: .claude/screenshots/research-ux1.png
원본: .claude/research-raw-ux1.txt

### 주요 트렌드
- 모바일 퍼스트 디자인
- 밝고 활기찬 색상 팔레트
- 카드 기반 레이아웃
- 게이미피케이션 요소 (점수, 배지, 콤보)
- 그리드 레이아웃으로 단어 표시

### 대표 프로젝트 패턴
- WARDY: 게이미파이드 워드 게임
- Word-Match: 매칭 기반 UI
- Word Puzzle Game: 퍼즐 형태

### 시각 스타일
- 컬러풀한 카드
- 모던 글래스모피즘
- 3D 컨셉
- 플레이풀한 브랜딩

## 2. CSS 애니메이션 (타이머/긴박감 UX)

출처: https://developer.mozilla.org/en-US/docs/Web/CSS/animation
스크린샷: .claude/screenshots/research-ux2.png
원본: .claude/research-raw-ux2.txt

### 타이머 UX 핵심 속성
- `animation-duration`: 카운트다운 시간 제어
- `animation-timing-function`: ease, steps(), cubic-bezier() 등
- `animation-play-state`: running/paused (일시정지/재개)
- `animation-iteration-count`: infinite (무한 반복, 펄스 효과)
- `animation-direction`: alternate (왕복 애니메이션)
- `animation-fill-mode`: forwards (완료 후 최종 상태 유지)

### 긴박감 연출 기법
- 타이머 5초 이하: 빨간색 + 펄스 애니메이션
- `steps()` 함수로 디지털 카운트다운 효과
- `cubic-bezier()` 커스텀 이징으로 가속감 표현

### 성능 최적화
- box model 속성 대신 `transform` 사용
- `will-change` 속성으로 성능 힌트
- `prefers-reduced-motion` 미디어 쿼리로 접근성 배려

## 3. Flexbox 레이아웃 (채팅 UI)

출처: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox
스크린샷: .claude/screenshots/research-ux3.png
원본: .claude/research-raw-ux3.txt

### 채팅 UI 핵심 패턴
- `display: flex` + `flex-direction: column` → 메시지 세로 스택
- `align-items: flex-start` → 사용자 메시지 왼쪽 정렬
- `align-items: flex-end` → AI 메시지 오른쪽 정렬
- `gap` 속성으로 메시지 간 간격

### 프로젝트 적용 레이아웃
```
┌─────────────────────────┐
│ 상단바 (점수/콤보/타이머) │  ← flex-direction: row
├─────────────────────────┤
│                         │
│ 사용자: "사과" →        │  ← align-self: flex-start
│         ← AI: "과학"    │  ← align-self: flex-end
│                         │  ← flex-direction: column
│                         │     flex: 1 (스크롤 영역)
├─────────────────────────┤
│ 입력 필드 + 제출 버튼    │  ← flex-direction: row
└─────────────────────────┘
```

### 반응형 고려사항
- `flex-wrap: wrap` → 긴 메시지 줄바꿈
- `flex: 1` → 메시지 영역 확장
- `flex-basis` → 기본 크기 설정
