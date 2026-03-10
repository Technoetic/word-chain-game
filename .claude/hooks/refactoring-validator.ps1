# refactoring-validator.ps1
# Step 23 - 리팩토링 후 코드 무결성 검증

param(
    [string]$ProjectRoot = $PWD
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "=== 리팩토링 검증 시작 ===" -ForegroundColor Cyan
$failed = $false

# 1. 테스트 실행
if (Test-Path (Join-Path $ProjectRoot "package.json")) {
    $packageJson = Get-Content (Join-Path $ProjectRoot "package.json") -Raw -Encoding UTF8 | ConvertFrom-Json

    if ($packageJson.scripts.test) {
        Write-Host "`n[1/3] 테스트 실행..." -ForegroundColor Yellow
        Push-Location $ProjectRoot
        npm test 2>&1 | Out-String | Write-Host
        Pop-Location

        if ($LASTEXITCODE -ne 0) {
            Write-Host "  X 테스트 실패" -ForegroundColor Red
            $failed = $true
        } else {
            Write-Host "  OK 테스트 통과" -ForegroundColor Green
        }
    } else {
        Write-Host "`n[1/3] test 스크립트 없음 (건너뜀)" -ForegroundColor Gray
    }

    # 2. 빌드 확인
    if ($packageJson.scripts.build) {
        Write-Host "`n[2/3] 빌드 확인..." -ForegroundColor Yellow
        Push-Location $ProjectRoot
        npm run build 2>&1 | Out-String | Write-Host
        Pop-Location

        if ($LASTEXITCODE -ne 0) {
            Write-Host "  X 빌드 실패" -ForegroundColor Red
            $failed = $true
        } else {
            Write-Host "  OK 빌드 성공" -ForegroundColor Green
        }
    } else {
        Write-Host "`n[2/3] build 스크립트 없음 (건너뜀)" -ForegroundColor Gray
    }

    # 3. 린트 확인
    if ($packageJson.scripts.lint) {
        Write-Host "`n[3/3] 린트 확인..." -ForegroundColor Yellow
        Push-Location $ProjectRoot
        npm run lint 2>&1 | Out-String | Write-Host
        Pop-Location

        if ($LASTEXITCODE -ne 0) {
            Write-Host "  X 린트 실패" -ForegroundColor Red
            $failed = $true
        } else {
            Write-Host "  OK 린트 통과" -ForegroundColor Green
        }
    } else {
        Write-Host "`n[3/3] lint 스크립트 없음 (건너뜀)" -ForegroundColor Gray
    }
} else {
    Write-Host "package.json 없음 - 건너뜀" -ForegroundColor Gray
    exit 0
}

Write-Host "`n=== 리팩토링 검증 완료 ===" -ForegroundColor Cyan

if ($failed) {
    Write-Host "리팩토링 검증 실패: 테스트/빌드/린트 오류를 수정하세요" -ForegroundColor Red
    exit 1
}

Write-Host "모든 리팩토링 검증 통과" -ForegroundColor Green
exit 0
