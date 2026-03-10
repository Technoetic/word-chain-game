# user-prompt-submit hook
# 사용자 메시지 제출 시 자동으로 Step 파일 읽기 강제

$ErrorActionPreference = "Stop"

# Step 파일 경로 생성
$stepFiles = 1..63 | ForEach-Object {
    ".claude/step_archive/step{0:D2}.md" -f $_
}

# 모든 Step 파일 존재 여부 확인
$missingFiles = $stepFiles | Where-Object { -not (Test-Path $_) }

if ($missingFiles) {
    Write-Error "❌ 누락된 Step 파일: $($missingFiles -join ', ')"
    exit 1
}

# Step 읽기 강제 메시지 주입
$message = @"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ABSOLUTE OVERRIDE - 최우선 규칙 (BLOCKING REQUIREMENT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Phase 1: Step 전체 읽기 (필수)

**지금 즉시** 63개 Step 파일을 병렬로 읽어야 합니다.

Read 도구 63번 병렬 호출:
- .claude/step_archive/step01.md
- .claude/step_archive/step02.md
- .claude/step_archive/step03.md
- .claude/step_archive/step04.md
- .claude/step_archive/step05.md
- .claude/step_archive/step06.md
- .claude/step_archive/step07.md
- .claude/step_archive/step08.md
- .claude/step_archive/step09.md
- .claude/step_archive/step10.md
- .claude/step_archive/step11.md
- .claude/step_archive/step12.md
- .claude/step_archive/step13.md
- .claude/step_archive/step14.md
- .claude/step_archive/step15.md
- .claude/step_archive/step16.md
- .claude/step_archive/step17.md
- .claude/step_archive/step18.md
- .claude/step_archive/step19.md
- .claude/step_archive/step20.md
- .claude/step_archive/step21.md
- .claude/step_archive/step22.md
- .claude/step_archive/step23.md
- .claude/step_archive/step24.md
- .claude/step_archive/step25.md
- .claude/step_archive/step26.md
- .claude/step_archive/step27.md
- .claude/step_archive/step28.md
- .claude/step_archive/step29.md
- .claude/step_archive/step30.md
- .claude/step_archive/step31.md
- .claude/step_archive/step32.md
- .claude/step_archive/step33.md
- .claude/step_archive/step34.md
- .claude/step_archive/step35.md
- .claude/step_archive/step36.md
- .claude/step_archive/step37.md
- .claude/step_archive/step38.md
- .claude/step_archive/step39.md
- .claude/step_archive/step40.md
- .claude/step_archive/step41.md
- .claude/step_archive/step42.md
- .claude/step_archive/step43.md
- .claude/step_archive/step44.md
- .claude/step_archive/step45.md
- .claude/step_archive/step46.md
- .claude/step_archive/step47.md
- .claude/step_archive/step48.md
- .claude/step_archive/step49.md
- .claude/step_archive/step50.md
- .claude/step_archive/step51.md
- .claude/step_archive/step52.md
- .claude/step_archive/step53.md
- .claude/step_archive/step54.md
- .claude/step_archive/step55.md
- .claude/step_archive/step56.md
- .claude/step_archive/step57.md
- .claude/step_archive/step58.md
- .claude/step_archive/step59.md
- .claude/step_archive/step60.md
- .claude/step_archive/step61.md
- .claude/step_archive/step62.md
- .claude/step_archive/step63.md

## Phase 2: 완료 보고

읽기 완료 후 출력:
```
✅ Step 읽기 완료: 63/63
→ Step 01부터 자동 수행 시작
```

## Phase 3: 연속 실행 (중단 없음)

- Step 01 완료 → 즉시 Step 02 시작
- Step 02 완료 → 즉시 Step 03 시작
- ...
- Step 63 완료 → 최종 보고

**진행 형식:**
```
✅ Step 23/63 완료
→ Step 24/63 시작...
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 절대 금지 사항 (BLOCKING REQUIREMENTS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Step 읽기 전에 사용자 요청 처리
❌ Step 일부만 읽기
❌ Step 건너뛰기
❌ 각 Step마다 "진행할까요?" 질문
❌ 사용자 확인 요청
❌ 중간에 멈춤/대기/일시정지
❌ TodoWrite 도구 사용

**오직 Step 진행 상황만 보고합니다.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"@

Write-Output $message
exit 0
