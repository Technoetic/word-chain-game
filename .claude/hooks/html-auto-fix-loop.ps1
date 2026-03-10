# ================================================================
# HTML Auto-Fix Loop Hook
# ================================================================
# 목적: HTML 인터랙션 테스트 실패 시 자동 수정 및 재테스트
# 기능: 성공할 때까지 무한 반복
# ================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$HtmlFilePath,

    [string]$ProjectRoot = $PWD
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$safeFileName = [System.IO.Path]::GetFileNameWithoutExtension($HtmlFilePath) -replace '[^a-zA-Z0-9]', '_'
$LogFile = Join-Path $ProjectRoot ".claude\hooks\html-auto-fix-loop_${safeFileName}_${timestamp}.log"
$FixRequestFile = Join-Path $ProjectRoot ".claude\html_fix_request_${safeFileName}.md"

# 로그 함수
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage -Encoding UTF8
}

Write-Log "=== HTML Auto-Fix Loop 시작 ===" "INFO"
Write-Log "대상 파일: $HtmlFilePath" "INFO"
Write-Log "모드: 무한 반복 (성공할 때까지)" "INFO"

# ================================================================
# 자동 수정 루프 (무한 반복)
# ================================================================
$attemptCount = 0
$testPassed = $false
$testerScript = Join-Path $PSScriptRoot "html-interaction-tester-full.ps1"

# full 버전이 없으면 simple 버전으로 fallback
if (-not (Test-Path $testerScript)) {
    $testerScript = Join-Path $PSScriptRoot "html-interaction-tester-simple.ps1"
    Write-Log "full 테스터 없음 -> simple 버전 사용: $testerScript" "WARN"
}

if (-not (Test-Path $testerScript)) {
    Write-Log "테스터 스크립트를 찾을 수 없습니다 (full/simple 모두 없음)" "ERROR"
    exit 1
}

while (-not $testPassed) {
    $attemptCount++
    Write-Log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "INFO"
    Write-Log "시도 #$attemptCount" "INFO"
    Write-Log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "INFO"

    # ================================================================
    # 1. Playwright 인터랙션 테스트 실행
    # ================================================================
    Write-Log "Playwright 인터랙션 테스트 실행 중..." "INFO"

    try {
        & powershell -File $testerScript -HtmlFilePath $HtmlFilePath | Out-Null

        if ($LASTEXITCODE -eq 0) {
            $testPassed = $true
            Write-Log "✅ 테스트 통과!" "INFO"
            Write-Host "`n✅ HTML 인터랙션 테스트 통과 (시도: $attemptCount회)"
            Write-Host "📸 스크린샷 저장 완료`n"
            break
        } else {
            Write-Log "❌ 테스트 실패" "WARN"
        }
    } catch {
        Write-Log "테스트 실행 중 오류: $_" "ERROR"
    }

    # ================================================================
    # 2. 테스트 실패 시 → 최신 리포트 찾기
    # ================================================================
    if (-not $testPassed) {
        Write-Log "실패 원인 분석 중..." "INFO"

        # 최신 테스트 리포트 찾기
        $reportPattern = Join-Path $ProjectRoot ".claude\html_interaction_test_${safeFileName}_*.md"
        $latestReport = Get-ChildItem -Path $reportPattern -ErrorAction SilentlyContinue |
                        Sort-Object LastWriteTime -Descending |
                        Select-Object -First 1

        if (-not $latestReport) {
            Write-Log "테스트 리포트를 찾을 수 없습니다" "ERROR"
            break
        }

        Write-Log "리포트 발견: $($latestReport.FullName)" "INFO"

        # 리포트 읽기
        $reportContent = Get-Content -Path $latestReport.FullName -Raw -Encoding UTF8

        # ================================================================
        # 3. Claude에게 수정 요청 생성
        # ================================================================
        Write-Log "Claude 수정 요청 생성 중..." "INFO"

        $fixRequest = @"
# 🔧 HTML 자동 수정 요청 (시도 #$attemptCount)

## 🎯 목표
``$HtmlFilePath`` 파일의 인터랙션 오류를 수정하세요.

## 📋 테스트 실패 리포트

$reportContent

## ⚠️ 중요 지침

**BLOCKING REQUIREMENT:**

1. **리포트 분석**: 위 테스트 리포트에서 실패한 인터랙션을 확인
2. **HTML 수정**: Edit 또는 Write 도구로 ``$HtmlFilePath`` 수정
3. **자동 재테스트**: 파일 수정 시 자동으로 Playwright 테스트 재실행
4. **반복**: 테스트 통과할 때까지 계속 수정

## 🚨 금지 사항

❌ 사용자에게 "수정할까요?" 질문 금지
❌ 사용자 확인 대기 금지
❌ 즉시 수정 시작

## ✅ 예상 결과

- 모든 Hover 테스트 통과
- 모든 Click 테스트 통과
- 모든 Double-click 테스트 통과
- 모든 Drag 테스트 통과

---

**지금 즉시 수정을 시작하세요!**
"@

        Set-Content -Path $FixRequestFile -Value $fixRequest -Encoding UTF8
        Write-Log "수정 요청 파일 생성: $FixRequestFile" "INFO"

        # ================================================================
        # 4. Claude에게 메시지 출력 (Hook 메시지로 전달)
        # ================================================================
        Write-Output ""
        Write-Output "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        Write-Output "🔧 HTML 인터랙션 테스트 실패 - 자동 수정 시작 (시도 #$attemptCount)"
        Write-Output "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        Write-Output ""
        Write-Output "📋 수정 요청을 읽고 즉시 HTML 파일을 수정하세요:"
        Write-Output ""
        Write-Output "   Read: $FixRequestFile"
        Write-Output ""
        Write-Output "파일 수정 후 자동으로 재테스트됩니다."
        Write-Output ""
        Write-Output "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        Write-Output ""

        # ================================================================
        # 5. 대기 (Claude가 수정할 시간)
        # ================================================================
        # Hook은 동기적으로 실행되므로, 여기서는 메시지만 출력하고 종료
        # 실제 수정은 Claude가 다음 턴에서 수행
        # 수정 후 다시 이 Hook이 발동됨 (tool-result.ps1에서)

        Write-Log "Claude의 수정을 기다립니다..." "INFO"

        # 이 시도에서는 일단 종료
        # 다음 수정 시 다시 Hook 발동 → 재테스트
        break
    }
}

# ================================================================
# 최종 결과
# ================================================================
if ($testPassed) {
    Write-Log "=== 성공: $attemptCount번 시도 만에 테스트 통과 ===" "INFO"
    exit 0
} else {
    Write-Log "=== 대기: Claude의 수정 필요 ===" "INFO"
    exit 2  # 대기 상태
}
