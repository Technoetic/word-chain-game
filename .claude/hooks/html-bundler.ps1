# html-bundler.ps1
# JS/CSS 분리 파일을 단일 index.html로 번들링

param(
    [string]$ProjectRoot = $PWD,
    [string]$ToolName = "",
    [string]$ToolInput = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "=== HTML Bundler Start ===" -ForegroundColor Cyan

$projectRoot = $ProjectRoot
$srcDir      = Join-Path $projectRoot 'src'
$srcHtml     = Join-Path $srcDir 'index.html'
$distDir     = Join-Path $projectRoot 'dist'
$distHtml    = Join-Path $distDir 'index.html'

if (-not (Test-Path $srcHtml)) {
    Write-Host "src/index.html not found - skipping" -ForegroundColor Gray
    exit 0
}

if (-not (Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

$html = Get-Content $srcHtml -Raw -Encoding UTF8

# 1. Inline CSS
$cssPattern = '<link[^>]+rel=["'']stylesheet["''][^>]+href=["'']([^"'']+)["''][^>]*/?>'
$html = [regex]::Replace($html, $cssPattern, {
    param($m)
    $href = $m.Groups[1].Value
    $cssPath = Join-Path $srcDir $href
    if (Test-Path $cssPath) {
        $css = Get-Content $cssPath -Raw -Encoding UTF8
        Write-Host "  CSS inline: $href" -ForegroundColor Gray
        return "<style>`n$css`n</style>"
    }
    return $m.Value
})

# 2. Inline JS
$jsPattern = '<script[^>]+src=["'']([^"'']+\.js)["''][^>]*></script>'
$html = [regex]::Replace($html, $jsPattern, {
    param($m)
    $src = $m.Groups[1].Value
    $jsPath = Join-Path $srcDir $src
    if (Test-Path $jsPath) {
        $js = Get-Content $jsPath -Raw -Encoding UTF8
        $js = $js -replace '^\s*export\s+(default\s+)?', ''
        $js = $js -replace "^import\s+.+from\s+['""].+['""];?\s*`n", ''
        Write-Host "  JS inline: $src" -ForegroundColor Gray
        return "<script>`n$js`n</script>"
    }
    return $m.Value
})

[System.IO.File]::WriteAllText($distHtml, $html, [System.Text.Encoding]::UTF8)

Write-Host "Bundle complete: dist/index.html" -ForegroundColor Green
Write-Host "=== HTML Bundler Done ===" -ForegroundColor Cyan
exit 0
