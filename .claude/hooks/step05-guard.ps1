# Step 05 Guard Hook
# step05 조사결과 파일이 없으면 도구를 차단한다.
# 단, step05 조사결과 파일 자체를 Write하는 경우는 허용한다.

$hookData = $null
try {
    $inputJson = [Console]::In.ReadToEnd()
    $hookData = $inputJson | ConvertFrom-Json
} catch { exit 0 }

$toolName = $hookData.tool_name
$toolInput = $hookData.tool_input

if ($toolName -eq "Write" -and $toolInput.file_path -match "step05_조사결과_chunk") { exit 0 }
if ($toolName -eq "Edit" -and $toolInput.file_path -match "step05\.md") { exit 0 }
if ($toolName -eq "Write" -and $toolInput.file_path -match "step05-guard\.ps1") { exit 0 }
if ($toolName -eq "Edit" -and $toolInput.file_path -match "step05-guard\.ps1") { exit 0 }

# 상대 경로로 프로젝트 루트 기준 탐색
$chunkFile = Join-Path $PWD ".claude\step05_조사결과_chunk1.md"
if (-not (Test-Path $chunkFile)) {
    Write-Error "Step 05 조사가 완료되지 않았습니다. 스킵 불가."
    exit 2
}
exit 0
