# Step 03 검증 체크리스트 (70-77번 줄)
# 조사 완료 전 다음을 확인

param(
    [string]$ProjectRoot = $PWD
)

$ErrorCount = 0

Write-Host "`n=== Step 03 검증 시작 ===" -ForegroundColor Cyan

# 1. .claude/screenshots/ 디렉토리에 스크린샷 존재
Write-Host "`n[1/4] 스크린샷 디렉토리 확인..." -ForegroundColor Yellow
$screenshotsDir = Join-Path $ProjectRoot ".claude\screenshots"

if (Test-Path $screenshotsDir) {
    $screenshots = Get-ChildItem -Path $screenshotsDir -Filter "*.png"
    if ($screenshots.Count -gt 0) {
        Write-Host "✅ 스크린샷 발견: $($screenshots.Count)개" -ForegroundColor Green
        foreach ($file in $screenshots) {
            Write-Host "   - $($file.Name) ($([math]::Round($file.Length/1KB, 2)) KB)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ .claude/screenshots/ 디렉토리는 있지만 PNG 파일 없음" -ForegroundColor Red
        $ErrorCount++
    }
} else {
    Write-Host "❌ .claude/screenshots/ 디렉토리 없음" -ForegroundColor Red
    $ErrorCount++
}

# 2. .claude/research-raw-*.txt 파일들 존재
Write-Host "`n[2/4] 원본 데이터 파일 확인..." -ForegroundColor Yellow
$claudeDir = Join-Path $ProjectRoot ".claude"

if (Test-Path $claudeDir) {
    $rawFiles = Get-ChildItem -Path $claudeDir -Filter "research-raw-*.txt"
    if ($rawFiles.Count -gt 0) {
        Write-Host "✅ 원본 데이터 파일 발견: $($rawFiles.Count)개" -ForegroundColor Green
        foreach ($file in $rawFiles) {
            Write-Host "   - $($file.Name) ($([math]::Round($file.Length/1KB, 2)) KB)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ research-raw-*.txt 파일 없음" -ForegroundColor Red
        $ErrorCount++
    }
} else {
    Write-Host "❌ .claude/ 디렉토리 없음" -ForegroundColor Red
    $ErrorCount++
}

# 3. playwright-research-*.js 스크립트 파일 존재
Write-Host "`n[3/4] Playwright 스크립트 파일 확인..." -ForegroundColor Yellow
$scriptFiles = Get-ChildItem -Path $ProjectRoot -Filter "playwright-research-*.js"

if ($scriptFiles.Count -gt 0) {
    Write-Host "✅ Playwright 스크립트 발견: $($scriptFiles.Count)개" -ForegroundColor Green
    foreach ($file in $scriptFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor Gray

        # 스크립트 내용 검증
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        $required = @(
            "require('playwright')",
            "chromium.launch()",
            "page.goto(",
            "page.screenshot(",
            "fullPage: true",
            ".claude/screenshots/",
            "document.body.innerText",
            "fs.writeFileSync(",
            ".claude/research-raw-",
            "browser.close()"
        )

        $missing = @()
        foreach ($item in $required) {
            if ($content -notlike "*$item*") {
                $missing += $item
            }
        }

        if ($missing.Count -gt 0) {
            Write-Host "     ⚠️  필수 요소 누락: $($missing -join ', ')" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "❌ playwright-research-*.js 파일 없음" -ForegroundColor Red
    $ErrorCount++
}

# 4. WebFetch/WebSearch 도구 사용하지 않음 (수동 확인 필요)
Write-Host "`n[4/4] WebFetch/WebSearch 사용 여부 (수동 확인 필요)..." -ForegroundColor Yellow
Write-Host "⚠️  Hook 시스템이 작동하지 않으므로, Claude가 스스로 확인 필요" -ForegroundColor Yellow
Write-Host "⚠️  최근 로그를 확인하여 WebFetch/WebSearch 호출 기록 점검" -ForegroundColor Yellow

# 최종 결과
Write-Host "`n=== 검증 결과 ===" -ForegroundColor Cyan

if ($ErrorCount -eq 0) {
    Write-Host "✅ 모든 검증 통과! 조사 결과 유효" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ $ErrorCount 개 항목 실패 - 조사 무효!" -ForegroundColor Red
    Write-Host "`n💡 스크린샷과 원본 데이터가 없으면 조사 무효! (79번 줄)" -ForegroundColor Yellow
    exit 1
}
