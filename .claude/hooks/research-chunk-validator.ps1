# Step 03 조사 결과 청크 검증 (131-133번 줄)
# BOM/CRLF/줄수/파일크기 검증

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

Write-Host "`n=== 조사 결과 청크 검증: $FilePath ===" -ForegroundColor Cyan

$ErrorCount = 0

# 파일 존재 확인
if (-not (Test-Path $FilePath)) {
    Write-Host "❌ 파일이 존재하지 않음: $FilePath" -ForegroundColor Red
    exit 1
}

# 1. BOM 확인 (UTF-8 without BOM 강제)
Write-Host "`n[1/4] BOM 확인..." -ForegroundColor Yellow
$bytes = [System.IO.File]::ReadAllBytes($FilePath)

if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "❌ UTF-8 BOM 발견 - UTF-8 without BOM으로 저장 필요" -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "✅ BOM 없음 (올바름)" -ForegroundColor Green
}

# 2. CRLF 확인 (Windows 스타일 줄바꿈)
Write-Host "`n[2/4] 줄바꿈 형식 확인..." -ForegroundColor Yellow
$content = Get-Content $FilePath -Raw -Encoding UTF8

if ($content -match "`r`n") {
    Write-Host "✅ CRLF 사용 (Windows 스타일)" -ForegroundColor Green
} elseif ($content -match "`n") {
    Write-Host "⚠️  LF만 사용 (Unix 스타일) - CRLF 권장" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  줄바꿈 없음 (단일 라인 파일?)" -ForegroundColor Yellow
}

# 3. 줄 수 확인 (500줄 이하)
Write-Host "`n[3/4] 줄 수 확인..." -ForegroundColor Yellow
$lines = Get-Content $FilePath -Encoding UTF8
$lineCount = $lines.Count

if ($lineCount -le 500) {
    Write-Host "✅ 줄 수: $lineCount / 500 (허용)" -ForegroundColor Green
} else {
    Write-Host "❌ 줄 수: $lineCount / 500 (초과) - 500줄 이하로 분할 필요" -ForegroundColor Red
    $ErrorCount++
}

# 4. 파일 크기 확인 (권장: 100KB 이하)
Write-Host "`n[4/4] 파일 크기 확인..." -ForegroundColor Yellow
$fileInfo = Get-Item $FilePath
$fileSizeKB = [math]::Round($fileInfo.Length / 1KB, 2)

if ($fileSizeKB -le 100) {
    Write-Host "✅ 파일 크기: $fileSizeKB KB (권장 범위)" -ForegroundColor Green
} elseif ($fileSizeKB -le 200) {
    Write-Host "⚠️  파일 크기: $fileSizeKB KB (경고: 100KB 초과)" -ForegroundColor Yellow
} else {
    Write-Host "❌ 파일 크기: $fileSizeKB KB (너무 큼: 200KB 초과)" -ForegroundColor Red
    $ErrorCount++
}

# 최종 결과
Write-Host "`n=== 검증 결과 ===" -ForegroundColor Cyan

if ($ErrorCount -eq 0) {
    Write-Host "✅ 청크 검증 통과!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ $ErrorCount 개 항목 실패" -ForegroundColor Red
    exit 1
}
