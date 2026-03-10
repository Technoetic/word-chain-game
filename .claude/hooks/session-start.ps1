# ================================================================
# Session Start Hook
# ================================================================
# 목적: Claude Code 세션 시작 시 자동 실행
# 기능: 프로젝트 규모 파악 및 환경 검증
# ================================================================

param(
    [string]$ProjectRoot = $PWD
)

$ErrorActionPreference = "Continue"
$LogFile = Join-Path $ProjectRoot ".claude\hooks\session-start.log"

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

Write-Log "=== Session Start Hook 시작 ===" "INFO"

# ================================================================
# 1. 프로젝트 규모 파악 (Step 01에서 사용)
# ================================================================
Write-Log "프로젝트 규모 분석 중..." "INFO"

try {
    # 파일 개수 확인
    $fileCount = (Get-ChildItem -Path $ProjectRoot -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Log "총 파일 개수: $fileCount" "INFO"

    # 프로젝트 크기 확인
    $projectSize = (Get-ChildItem -Path $ProjectRoot -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $projectSizeMB = [math]::Round($projectSize / 1MB, 2)
    Write-Log "프로젝트 크기: $projectSizeMB MB" "INFO"

    # 서브에이전트 권장 개수 산출
    $recommendedAgents = if ($fileCount -ge 1000) { "20개 이상" }
                        elseif ($fileCount -ge 100) { "10-20개" }
                        else { "5-10개" }
    Write-Log "권장 서브에이전트 개수: $recommendedAgents" "INFO"

} catch {
    Write-Log "프로젝트 규모 분석 실패: $_" "WARN"
}

# ================================================================
# 2. Git 저장소 확인
# ================================================================
try {
    if (Test-Path (Join-Path $ProjectRoot ".git")) {
        $gitStatus = git status --short 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Git 저장소 확인됨" "INFO"
            $modifiedFiles = ($gitStatus | Measure-Object).Count
            if ($modifiedFiles -gt 0) {
                Write-Log "수정된 파일: $modifiedFiles 개" "INFO"
            }
        }
    } else {
        Write-Log "Git 저장소가 아닙니다." "INFO"
    }
} catch {
    Write-Log "Git 확인 실패: $_" "WARN"
}

# ================================================================
# 3. Playwright 환경 빠른 검증
# ================================================================
Write-Log "Playwright 환경 검증 중..." "INFO"

try {
    # package.json 확인
    $packageJsonPath = Join-Path $ProjectRoot "package.json"
    if (Test-Path $packageJsonPath) {
        $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json

        # Playwright 의존성 확인
        $hasPw = ($packageJson.devDependencies -and $packageJson.devDependencies.playwright) -or
                 ($packageJson.dependencies -and $packageJson.dependencies.playwright)

        if ($hasPw) {
            # Playwright 버전 확인 (빠른 체크)
            $pwVersion = npx playwright --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Playwright 설치 확인: $pwVersion" "INFO"
            } else {
                Write-Log "Playwright가 설치되지 않았습니다. 'npm install' 실행 필요" "WARN"
            }
        } else {
            Write-Log "Playwright 의존성이 없습니다." "INFO"
        }
    } else {
        Write-Log "package.json이 없습니다." "INFO"
    }
} catch {
    Write-Log "Playwright 검증 실패: $_" "WARN"
}

# ================================================================
# 4. Node.js 환경 확인
# ================================================================
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Node.js 버전: $nodeVersion" "INFO"
    }

    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Log "npm 버전: $npmVersion" "INFO"
    }
} catch {
    Write-Log "Node.js 확인 실패: $_" "WARN"
}

# ================================================================
# 5. .claude 디렉토리 확인
# ================================================================
$claudeDir = Join-Path $ProjectRoot ".claude"
if (-not (Test-Path $claudeDir)) {
    Write-Log ".claude 디렉토리가 없습니다. 생성합니다." "WARN"
    New-Item -Path $claudeDir -ItemType Directory -Force | Out-Null
}

# Step 파일 확인
$stepFiles = Get-ChildItem -Path $claudeDir -Filter "step*.md" -ErrorAction SilentlyContinue
if ($stepFiles) {
    Write-Log "Step 파일 발견: $($stepFiles.Count)개" "INFO"
}

# ================================================================
# 6. 요약 출력
# ================================================================
Write-Log "=== 세션 시작 정보 요약 ===" "INFO"
Write-Log "프로젝트: $ProjectRoot" "INFO"
if ($fileCount) { Write-Log "파일: $fileCount 개" "INFO" }
if ($projectSizeMB) { Write-Log "크기: $projectSizeMB MB" "INFO" }
if ($recommendedAgents) { Write-Log "권장 서브에이전트: $recommendedAgents" "INFO" }

Write-Log "=== Session Start Hook 완료 ===" "INFO"
exit 0
