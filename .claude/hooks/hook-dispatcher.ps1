# ================================================================
# Hook Dispatcher (범용)
# ================================================================
# 어떤 프로젝트 폴더에서든 .claude/hooks/ 아래의 Hook을 자동 발동시킨다.
# 글로벌 settings.json에 이 파일 경로 대신, 이 디스패처를 등록하면
# 프로젝트를 복붙해도 Hook이 그대로 동작한다.
#
# 사용법 (글로벌 settings.json):
#   "command": "powershell -ExecutionPolicy Bypass -File .claude/hooks/hook-dispatcher.ps1 -HookName <이름>"
#
# Claude Code는 Hook 실행 시 CWD를 프로젝트 루트로 설정하므로
# 상대 경로 ".claude/hooks/..." 가 자동으로 현재 프로젝트를 가리킨다.
# ================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$HookName,

    [string]$ToolName = "",
    [string]$ToolArgs = "",
    [string]$FilePath = ""
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# 프로젝트 루트 = CWD (Claude Code가 보장)
$ProjectRoot = $PWD.Path
$HooksDir = Join-Path $ProjectRoot ".claude\hooks"

# Hook 파일 경로 결정
$HookScript = Join-Path $HooksDir "$HookName.ps1"

if (-not (Test-Path $HookScript)) {
    # Hook 파일이 없으면 조용히 통과 (다른 프로젝트에서는 해당 Hook이 없을 수 있음)
    exit 0
}

# Hook 실행 (파라미터 전달)
$params = @{
    ProjectRoot = $ProjectRoot
}

if ($ToolName) { $params.ToolName = $ToolName }
if ($ToolArgs) { $params.ToolArgs = $ToolArgs }
if ($FilePath) { $params.FilePath = $FilePath }

# powershell -File로 호출해야 $PSScriptRoot이 Hook 파일 위치로 올바르게 설정됨
$argList = @("-ExecutionPolicy", "Bypass", "-File", $HookScript)

foreach ($key in $params.Keys) {
    $argList += "-$key"
    $argList += $params[$key]
}

try {
    & powershell $argList
    exit $LASTEXITCODE
} catch {
    Write-Error "Hook 실행 실패 [$HookName]: $_"
    exit 1
}
