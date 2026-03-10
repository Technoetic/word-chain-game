# console-error-checker.ps1
# dist/index.html 생성 후 Playwright로 콘솔 에러 자동 수집
# 에러 0개 확인 (Step 44를 기다리지 않고 즉시 감지)

param(
    [string]$ProjectRoot = $PWD,
    [string]$FilePath = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# dist/index.html 대상만
$distIndex = Join-Path $ProjectRoot "dist\index.html"
if (-not (Test-Path $distIndex)) { exit 0 }

# Playwright 설치 확인
$pwCheck = npx playwright --version 2>&1
if ($LASTEXITCODE -ne 0) { exit 0 }

$fileUrl = "file:///$($distIndex -replace '\\', '/')"

$jsScript = @"
const { chromium } = require('playwright');

(async () => {
  const errors = [];
  const browser = await chromium.launch();
  const page = await browser.newPage();

  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  page.on('pageerror', err => {
    errors.push('[UNCAUGHT] ' + err.message);
  });

  page.on('requestfailed', req => {
    errors.push('[NETWORK] ' + req.url() + ' - ' + (req.failure() ? req.failure().errorText : 'unknown'));
  });

  try {
    await page.goto('$fileUrl', { waitUntil: 'load', timeout: 10000 });
    await page.waitForTimeout(2000);
  } catch (e) {
    errors.push('[LOAD] ' + e.message);
  }

  await browser.close();

  if (errors.length > 0) {
    console.log('ERRORS_FOUND');
    errors.forEach(e => console.log(e));
    process.exit(1);
  } else {
    console.log('NO_ERRORS');
    process.exit(0);
  }
})();
"@

$jsFile = Join-Path $ProjectRoot ".claude\console-check-temp.js"
Set-Content -Path $jsFile -Value $jsScript -Encoding UTF8

try {
    $output = node $jsFile 2>&1 | Out-String

    if ($LASTEXITCODE -ne 0) {
        Write-Output ""
        Write-Output "[CONSOLE ERRORS] dist/index.html"
        # NO_ERRORS/ERRORS_FOUND 헤더 제거하고 에러만 출력
        $lines = $output.Trim() -split "`n" | Where-Object { $_ -ne "ERRORS_FOUND" -and $_.Trim() -ne "" }
        foreach ($line in $lines) {
            Write-Output "  $($line.Trim())"
        }
        Write-Output ""
        exit 1
    }
} finally {
    if (Test-Path $jsFile) {
        Remove-Item $jsFile -Force
    }
}

exit 0
