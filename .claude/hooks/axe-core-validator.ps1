# ================================================================
# axe-core Validator Hook
# ================================================================
# 목적: Step 03 (@axe-core/playwright 환경 설치 검증)
# 기능: @axe-core/playwright 패키지 설치 확인 및 테스트 결과 기록
# ================================================================

param(
    [string]$ProjectRoot = $PWD,
    [switch]$FullTest = $false
)

$ErrorActionPreference = "Stop"
$LogFile = Join-Path $ProjectRoot ".claude\hooks\axe-core-validator.log"
$ResultFile = Join-Path $ProjectRoot ".claude\step03_axe_core_test.md"

# UTF-8 인코딩 강제
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

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

Write-Log "=== axe-core Validator 시작 ===" "INFO"

# ================================================================
# 1. package.json 존재 확인
# ================================================================
$packageJsonPath = Join-Path $ProjectRoot "package.json"
if (-not (Test-Path $packageJsonPath)) {
    Write-Log "package.json이 존재하지 않습니다. 웹 프로젝트가 아닙니다." "ERROR"
    exit 1
}

# ================================================================
# 2. @axe-core/playwright 설치 확인
# ================================================================
$axeCoreInstalled = $false
$axeCoreVersion = ""

try {
    $packageJson = Get-Content $packageJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

    # dependencies 확인
    $inDeps = $false
    $inDevDeps = $false

    if ($packageJson.dependencies -and $packageJson.dependencies.'@axe-core/playwright') {
        $inDeps = $true
        $axeCoreVersion = $packageJson.dependencies.'@axe-core/playwright'
    }

    if ($packageJson.devDependencies -and $packageJson.devDependencies.'@axe-core/playwright') {
        $inDevDeps = $true
        $axeCoreVersion = $packageJson.devDependencies.'@axe-core/playwright'
    }

    if ($inDeps -or $inDevDeps) {
        Write-Log "@axe-core/playwright가 package.json에 등록되어 있습니다. (버전: $axeCoreVersion)" "INFO"
    } else {
        Write-Log "@axe-core/playwright가 package.json에 없습니다." "WARN"
    }
} catch {
    Write-Log "package.json 파싱 실패: $_" "ERROR"
}

# ================================================================
# 3. node_modules에서 실제 설치 확인
# ================================================================
$axeCoreModulePath = Join-Path $ProjectRoot "node_modules\@axe-core\playwright"
if (Test-Path $axeCoreModulePath) {
    $axeCoreInstalled = $true

    # 실제 설치된 버전 확인
    $axeCorePackageJson = Join-Path $axeCoreModulePath "package.json"
    if (Test-Path $axeCorePackageJson) {
        try {
            $axeCorePkg = Get-Content $axeCorePackageJson -Raw -Encoding UTF8 | ConvertFrom-Json
            $axeCoreVersion = $axeCorePkg.version
            Write-Log "@axe-core/playwright 설치 확인 (실제 버전: $axeCoreVersion)" "INFO"
        } catch {
            Write-Log "@axe-core/playwright 버전 확인 실패" "WARN"
        }
    }
} else {
    Write-Log "@axe-core/playwright가 node_modules에 설치되지 않았습니다." "ERROR"
    Write-Log "설치 명령: npm install -D @axe-core/playwright" "INFO"
}

# ================================================================
# 4. axe-core 기본 의존성 확인
# ================================================================
$axeCoreBasePath = Join-Path $ProjectRoot "node_modules\axe-core"
$axeCoreBaseInstalled = Test-Path $axeCoreBasePath
if ($axeCoreBaseInstalled) {
    Write-Log "axe-core 기본 패키지 설치 확인" "INFO"
} else {
    Write-Log "axe-core 기본 패키지 미설치" "WARN"
}

# ================================================================
# 5. Playwright 의존성 확인
# ================================================================
$playwrightInstalled = $false
try {
    $playwrightVersion = npx playwright --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $playwrightInstalled = $true
        Write-Log "Playwright 설치 확인: $playwrightVersion" "INFO"
    }
} catch {
    Write-Log "Playwright 확인 실패: $_" "WARN"
}

# ================================================================
# 6. require 테스트 (실제 import 가능 여부)
# ================================================================
$requireSuccess = $false
if ($axeCoreInstalled) {
    try {
        $testScript = "try { require('@axe-core/playwright'); console.log('OK'); process.exit(0); } catch(e) { console.error(e.message); process.exit(1); }"
        $result = node -e $testScript 2>&1
        if ($LASTEXITCODE -eq 0) {
            $requireSuccess = $true
            Write-Log "@axe-core/playwright require 성공" "INFO"
        } else {
            Write-Log "@axe-core/playwright require 실패: $result" "ERROR"
        }
    } catch {
        Write-Log "require 테스트 실행 오류: $_" "ERROR"
    }
}

# ================================================================
# 7. 간단한 axe-core 분석 테스트 (선택적)
# ================================================================
$analysisSuccess = $false
if ($FullTest -and $axeCoreInstalled -and $playwrightInstalled) {
    Write-Log "axe-core 분석 테스트 실행 중..." "INFO"

    $testScript = @"
const { chromium } = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;

(async () => {
  try {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.setContent('<html lang="ko"><head><title>Test</title></head><body><h1>axe-core test</h1></body></html>');

    const results = await new AxeBuilder({ page }).analyze();
    console.log('violations: ' + results.violations.length);
    console.log('passes: ' + results.passes.length);

    await browser.close();
    process.exit(0);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
})();
"@

    $testScriptPath = Join-Path $ProjectRoot ".claude\axe-core-test-temp.js"
    Set-Content -Path $testScriptPath -Value $testScript -Encoding UTF8

    try {
        $output = node $testScriptPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            $analysisSuccess = $true
            Write-Log "axe-core 분석 테스트 성공: $output" "INFO"
        } else {
            Write-Log "axe-core 분석 테스트 실패: $output" "ERROR"
        }
    } catch {
        Write-Log "axe-core 분석 테스트 오류: $_" "ERROR"
    } finally {
        if (Test-Path $testScriptPath) {
            Remove-Item $testScriptPath -Force
        }
    }
}

# ================================================================
# 8. 결과를 step03_axe_core_test.md에 기록
# ================================================================
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$overallSuccess = $axeCoreInstalled -and $requireSuccess -and $playwrightInstalled

$resultContent = @"
# Step 03 - @axe-core/playwright 환경 테스트 결과

## 테스트 정보
- **실행 시간**: $timestamp
- **@axe-core/playwright 버전**: $axeCoreVersion
- **전체 결과**: $(if ($overallSuccess) { "Pass" } else { "Fail" })

## 설치 상태
- @axe-core/playwright 패키지: $(if ($axeCoreInstalled) { "설치됨" } else { "미설치" })
- axe-core 기본 패키지: $(if ($axeCoreBaseInstalled) { "설치됨" } else { "미설치" })
- Playwright 의존성: $(if ($playwrightInstalled) { "설치됨" } else { "미설치" })

## 검증 항목
1. package.json 등록 확인: $(if ($axeCoreVersion) { "등록됨 ($axeCoreVersion)" } else { "미등록" })
2. node_modules 설치 확인: $(if ($axeCoreInstalled) { "설치됨" } else { "미설치" })
3. require 테스트: $(if ($requireSuccess) { "성공" } else { "실패" })
4. Playwright 연동: $(if ($playwrightInstalled) { "정상" } else { "Playwright 미설치" })
$(if ($FullTest) {
"5. axe-core 분석 테스트: $(if ($analysisSuccess) { "성공" } else { "실패" })"
} else {
"5. axe-core 분석 테스트: 생략 (빠른 검증 모드)"
})

## 미설치 시 설치 명령
``````
npm install -D @axe-core/playwright
``````

## 다음 단계
Step 04: 전체 조사
"@

Set-Content -Path $ResultFile -Value $resultContent -Encoding UTF8
Write-Log "결과 파일 생성: $ResultFile" "INFO"

Write-Log "=== axe-core Validator 완료 ===" "INFO"

if (-not $overallSuccess) {
    Write-Log "@axe-core/playwright 환경이 준비되지 않았습니다." "ERROR"
    exit 1
} else {
    Write-Log "모든 검증 통과" "INFO"
    exit 0
}
