# Hook Step 2 - 조사 결과 파일 자동 검증
# postToolExecution 시 실행 (Write/Edit 후)

param(
    [string]$ToolName,
    [string]$FilePath
)

# 조사 결과 파일 (청크 포함) 대상
if ($FilePath -notmatch "step\d+_조사결과(_chunk\d+)?\.md$") {
    exit 0
}

# 컬러 출력 함수
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "Yellow")
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "`n🔍 [Research Validator] 조사 결과 검증..." "Cyan"

$violations = @()
$content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue

if (-not $content) {
    Write-ColorOutput "   ⚠️  파일이 비어있습니다" "Yellow"
    exit 0
}

# ============================================
# Rule 1: 동적 줄 수 제한
# ============================================
$lines = Get-Content $FilePath
$lineCount = $lines.Count

# 동적 제한: 청크 파일만 500줄
$limit = 500

if ($lineCount -gt $limit) {
    $violations += "Rule 1: 줄 수 초과 ($lineCount/$limit) - 요약 또는 분할 필요"
} else {
    Write-ColorOutput "   ✅ 줄 수 적정 ($lineCount/$limit)" "Green"
}

# ============================================
# Rule 2: BOM 인코딩 금지
# ============================================
$bytes = [System.IO.File]::ReadAllBytes($FilePath)
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    $violations += "Rule 2: BOM 인코딩 감지 - UTF-8 without BOM 필요"
}

# ============================================
# Rule 3: CRLF 줄바꿈 (Windows)
# ============================================
$lfOnly = ($content -match "`n" -and $content -notmatch "`r`n")
if ($lfOnly) {
    $violations += "Rule 3: LF 줄바꿈 감지 - CRLF 필요 (Windows)"
}

# ============================================
# Rule 4: 파일 크기 (50KB)
# ============================================
$fileSize = (Get-Item $FilePath).Length
if ($fileSize -gt 51200) {
    $sizeKB = [math]::Round($fileSize / 1024, 1)
    $violations += "Rule 4: 파일 크기 초과 ($sizeKB KB / 50 KB)"
}

# ============================================
# Rule 5: 필수 섹션 확인
# ============================================
if ($content -notmatch "##\s+조사 내용" -and $content -notmatch "##\s+결과") {
    $violations += "Rule 5: 필수 섹션 누락 (## 조사 내용 또는 ## 결과)"
}

# ============================================
# 결과 출력 및 실패 처리
# ============================================
if ($violations.Count -eq 0) {
    Write-ColorOutput "   ✅ 모든 검증 규칙 준수" "Green"
    Write-Host ""
    exit 0
} else {
    Write-ColorOutput "   ❌ 검증 실패 - 파일 거부됨:" "Red"
    foreach ($violation in $violations) {
        Write-ColorOutput "      💡 $violation" "Yellow"
    }
    Write-Host ""
    exit 1  # 실패 코드 → Claude에게 오류 전달
}
