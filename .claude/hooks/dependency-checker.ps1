# ================================================================
# Dependency Checker Hook
# ================================================================
# 목적: Step 09 (환경 준비)에서 자동 실행
# 기능: 프로젝트 의존성 자동 검증 및 설치 제안
# ================================================================

param(
    [string]$ProjectRoot = $PWD
)

$ErrorActionPreference = "Stop"
$LogFile = Join-Path $ProjectRoot ".claude\hooks\dependency-checker.log"

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

Write-Log "=== Dependency Checker 시작 ===" "INFO"

# ================================================================
# 1. package.json 확인
# ================================================================
$packageJsonPath = Join-Path $ProjectRoot "package.json"
if (-not (Test-Path $packageJsonPath)) {
    Write-Log "package.json이 없습니다. Node.js 프로젝트가 아닙니다." "WARN"
    exit 0
}

Write-Log "package.json 발견: $packageJsonPath" "INFO"
$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json

# ================================================================
# 2. Playwright 의존성 확인
# ================================================================
$missingDeps = @()
$playwrightRequired = $false

# devDependencies에서 playwright 확인
if ($packageJson.devDependencies -and $packageJson.devDependencies.playwright) {
    $playwrightRequired = $true
    Write-Log "Playwright가 devDependencies에 정의되어 있습니다." "INFO"
}

# dependencies에서 playwright 확인
if ($packageJson.dependencies -and $packageJson.dependencies.playwright) {
    $playwrightRequired = $true
    Write-Log "Playwright가 dependencies에 정의되어 있습니다." "INFO"
}

if ($playwrightRequired) {
    # Playwright 설치 확인
    try {
        $playwrightVersion = npx playwright --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Playwright 설치 확인: $playwrightVersion" "INFO"
        } else {
            Write-Log "Playwright가 설치되지 않았습니다." "ERROR"
            $missingDeps += "playwright"
        }
    } catch {
        Write-Log "Playwright 실행 실패: $_" "ERROR"
        $missingDeps += "playwright"
    }

    # 브라우저 설치 확인
    try {
        $browserCheck = npx playwright install --dry-run chromium 2>&1
        if ($browserCheck -match "is already installed") {
            Write-Log "Chromium 브라우저가 이미 설치되어 있습니다." "INFO"
        } else {
            Write-Log "Chromium 브라우저가 설치되지 않았습니다." "WARN"
            $missingDeps += "playwright-browsers"
        }
    } catch {
        Write-Log "브라우저 확인 실패: $_" "WARN"
    }
}

# ================================================================
# 3. 기타 의존성 확인 (확장 가능)
# ================================================================
# 향후 다른 패키지 검증 로직 추가 가능

# ================================================================
# 4. 미설치 패키지 처리
# ================================================================
if ($missingDeps.Count -gt 0) {
    Write-Log "=== 미설치 패키지 발견 ===" "ERROR"
    Write-Log "다음 명령어로 설치하세요:" "ERROR"

    if ($missingDeps -contains "playwright") {
        Write-Log "  npm install -D playwright" "ERROR"
    }

    if ($missingDeps -contains "playwright-browsers") {
        Write-Log "  npx playwright install" "ERROR"
    }

    Write-Log "=== Dependency Checker 실패 ===" "ERROR"
    exit 1
} else {
    Write-Log "=== 모든 의존성이 정상입니다 ===" "INFO"
    Write-Log "=== Dependency Checker 완료 ===" "INFO"
    exit 0
}
