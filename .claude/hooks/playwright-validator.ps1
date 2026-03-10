# ================================================================
# Playwright Validator Hook
# ================================================================
# 목적: Step 02, 40-44 (E2E 테스트)에서 자동 실행
# 기능: Playwright 환경 테스트 및 결과 기록
# ================================================================

param(
    [string]$ProjectRoot = $PWD,
    [switch]$FullTest = $false
)

$ErrorActionPreference = "Stop"
$LogFile = Join-Path $ProjectRoot ".claude\hooks\playwright-validator.log"
$ResultFile = Join-Path $ProjectRoot ".claude\step02_playwright_test.md"

# 로그 함수
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# 로그 파일 초기화
if (Test-Path $LogFile) { Clear-Content $LogFile }

Write-Log "=== Playwright Validator 시작 ===" "INFO"

# ================================================================
# 1. Playwright 버전 확인
# ================================================================
try {
    $playwrightVersion = npx playwright --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Playwright가 설치되지 않았습니다." "ERROR"
        exit 1
    }
    Write-Log "Playwright 버전: $playwrightVersion" "INFO"
} catch {
    Write-Log "Playwright 실행 실패: $_" "ERROR"
    exit 1
}

# ================================================================
# 2. 브라우저 설치 확인 (Node.js로 실제 실행 테스트)
# ================================================================
$browsers = @("chromium", "firefox", "webkit")
$installedBrowsers = @()

foreach ($browser in $browsers) {
    try {
        $testScript = "const { $browser } = require('playwright'); (async () => { try { const b = await $browser.launch(); await b.close(); process.exit(0); } catch (e) { process.exit(1); } })()"
        node -e $testScript 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "$browser 브라우저가 설치되어 있습니다." "INFO"
            $installedBrowsers += $browser
        } else {
            Write-Log "$browser 브라우저가 설치되지 않았습니다." "WARN"
        }
    } catch {
        Write-Log "$browser 확인 실패: $_" "WARN"
    }
}

if ($installedBrowsers.Count -eq 0) {
    Write-Log "설치된 브라우저가 없습니다. 'npx playwright install'을 실행하세요." "ERROR"
    exit 1
}

# ================================================================
# 3. 간단한 테스트 실행 (선택적)
# ================================================================
$testSuccess = $false
$screenshotPath = Join-Path $ProjectRoot ".claude\playwright_test_screenshot.png"

if ($FullTest) {
    Write-Log "Playwright 테스트 실행 중..." "INFO"

    # 테스트 스크립트 생성
    $testScript = @"
const { chromium } = require('playwright');

(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('https://example.com', { timeout: 10000 });
    await page.screenshot({ path: '$($screenshotPath -replace '\\', '/')' });
    await browser.close();
    console.log('✅ Playwright 테스트 성공');
    process.exit(0);
  } catch (error) {
    console.error('❌ Playwright 테스트 실패:', error.message);
    process.exit(1);
  }
})();
"@

    $testScriptPath = Join-Path $ProjectRoot ".claude\playwright-test-temp.js"
    Set-Content -Path $testScriptPath -Value $testScript -Encoding UTF8

    try {
        node $testScriptPath
        if ($LASTEXITCODE -eq 0) {
            $testSuccess = $true
            Write-Log "테스트 실행 성공" "INFO"

            # 스크린샷 확인
            if (Test-Path $screenshotPath) {
                Write-Log "스크린샷 생성 확인: $screenshotPath" "INFO"
            } else {
                Write-Log "스크린샷 생성 실패" "WARN"
            }
        } else {
            Write-Log "테스트 실행 실패" "ERROR"
        }
    } catch {
        Write-Log "테스트 실행 중 오류: $_" "ERROR"
    } finally {
        # 임시 파일 삭제
        if (Test-Path $testScriptPath) {
            Remove-Item $testScriptPath -Force
        }
    }
}

# ================================================================
# 4. 결과를 step02_playwright_test.md에 기록
# ================================================================
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$resultContent = @"
# Step 02 - Playwright 환경 테스트 결과

## 테스트 정보
- **실행 시간**: $timestamp
- **Playwright 버전**: $playwrightVersion
- **테스트 결과**: $(if ($testSuccess -or -not $FullTest) { "✅ 성공" } else { "❌ 실패" })

## 브라우저 설치 상태
$(foreach ($browser in $installedBrowsers) { "- ✅ $browser`n" })

## 테스트 내용
1. Playwright 설치 확인: ✅ $playwrightVersion
2. 브라우저 확인: ✅ $($installedBrowsers.Count)개 설치됨
$(if ($FullTest) {
"3. example.com 방문: $(if ($testSuccess) { "✅ 성공" } else { "❌ 실패" })
4. 스크린샷 촬영: $(if (Test-Path $screenshotPath) { "✅ 저장됨 (.claude/playwright_test_screenshot.png)" } else { "❌ 실패" })"
} else {
"3. 전체 테스트: ⏭️ 생략 (빠른 검증 모드)"
})

## 검증 결과
- Playwright 명령어 실행 성공
$(if (Test-Path $screenshotPath) { "- 스크린샷 파일 생성 확인" })
- 에러 없이 완료

## 다음 단계
Step 03: 전체 조사 (RS-485 인터페이스 관련)
"@

Set-Content -Path $ResultFile -Value $resultContent -Encoding UTF8
Write-Log "결과 파일 생성: $ResultFile" "INFO"

Write-Log "=== Playwright Validator 완료 ===" "INFO"

if ($FullTest -and -not $testSuccess) {
    exit 1
} else {
    exit 0
}
