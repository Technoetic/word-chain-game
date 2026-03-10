# src-lint-on-save.ps1
# src/ 파일 수정 시 Node.js 구문 검증 (syntax error 즉시 감지)
# ESLint/Prettier 불필요, Node.js만 있으면 동작

param(
    [string]$ProjectRoot = $PWD,
    [string]$FilePath = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

if (-not $FilePath -or -not (Test-Path $FilePath)) { exit 0 }

# .js 파일만 대상
if ($FilePath -notmatch '\.js$') { exit 0 }

# node --check로 구문 검증 (실행 없이 파싱만)
$output = node --check $FilePath 2>&1 | Out-String

if ($LASTEXITCODE -ne 0) {
    Write-Output ""
    Write-Output "[SYNTAX ERROR] $FilePath"
    Write-Output $output.Trim()
    Write-Output ""
    exit 1
}

exit 0
