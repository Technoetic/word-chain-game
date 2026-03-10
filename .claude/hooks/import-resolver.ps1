# import-resolver.ps1
# src/ 파일의 require/import 경로가 실제 존재하는지 확인
# 모듈화(Step 15) 시 경로 오타 즉시 감지

param(
    [string]$ProjectRoot = $PWD,
    [string]$FilePath = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

if (-not $FilePath -or -not (Test-Path $FilePath)) { exit 0 }
if ($FilePath -notmatch '\.js$') { exit 0 }

$content = Get-Content $FilePath -Raw -Encoding UTF8
$fileDir = Split-Path $FilePath -Parent
$failed = $false

# require('./xxx') 패턴 추출
$requireMatches = [regex]::Matches($content, "require\(\s*['""](\./[^'""]+)['""]\s*\)")

foreach ($match in $requireMatches) {
    $reqPath = $match.Groups[1].Value
    $resolvedBase = Join-Path $fileDir $reqPath

    # .js 확장자 붙여서 확인
    $candidates = @(
        $resolvedBase,
        "$resolvedBase.js",
        (Join-Path $resolvedBase "index.js")
    )

    $found = $false
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $found = $true
            break
        }
    }

    if (-not $found) {
        Write-Output "[MISSING] require('$reqPath') -> 파일 없음"
        Write-Output "  위치: $FilePath"
        Write-Output "  탐색: $($candidates -join ', ')"
        $failed = $true
    }
}

# import ... from './xxx' 패턴 추출
$importMatches = [regex]::Matches($content, "from\s+['""](\./[^'""]+)['""]")

foreach ($match in $importMatches) {
    $impPath = $match.Groups[1].Value
    $resolvedBase = Join-Path $fileDir $impPath

    $candidates = @(
        $resolvedBase,
        "$resolvedBase.js",
        (Join-Path $resolvedBase "index.js")
    )

    $found = $false
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $found = $true
            break
        }
    }

    if (-not $found) {
        Write-Output "[MISSING] import from '$impPath' -> 파일 없음"
        Write-Output "  위치: $FilePath"
        Write-Output "  탐색: $($candidates -join ', ')"
        $failed = $true
    }
}

if ($failed) {
    Write-Output ""
    exit 1
}

exit 0
