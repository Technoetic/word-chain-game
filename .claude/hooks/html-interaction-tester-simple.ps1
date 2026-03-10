# Simple HTML Interaction Tester
param(
    [Parameter(Mandatory=$true)]
    [string]$HtmlFilePath
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$safeFileName = [System.IO.Path]::GetFileNameWithoutExtension($HtmlFilePath) -replace '[^a-zA-Z0-9]', '_'
$ScreenshotDir = Join-Path $PWD ".claude\screenshots\interactions\$safeFileName"
$ResultFile = Join-Path $PWD ".claude\html_interaction_test_${safeFileName}_${timestamp}.md"

# 디렉토리 생성
New-Item -ItemType Directory -Force -Path $ScreenshotDir | Out-Null

# HTML 파일 절대 경로
$absoluteHtmlPath = Resolve-Path $HtmlFilePath
$fileUrl = "file:///$($absoluteHtmlPath -replace '\\', '/')"
$jsScreenshotDir = $ScreenshotDir -replace '\\', '/'

# JavaScript 파일 생성 (Here-String 문제 회피)
$jsContent = @"
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const screenshotDir = '$jsScreenshotDir';
  const fileUrl = '$fileUrl';
  const results = [];
  let allPassed = true;

  try {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

    console.log('Loading:', fileUrl);
    await page.goto(fileUrl, { waitUntil: 'load', timeout: 10000 });

    // Initial screenshot
    await page.screenshot({ path: path.join(screenshotDir, '00_initial.png'), fullPage: true });
    console.log('Initial screenshot saved');

    // Find interactive elements
    const elements = await page.evaluate(() => {
      const clickables = document.querySelectorAll('button, a, [onclick], [role="button"]');
      const draggables = document.querySelectorAll('[draggable="true"]');

      return {
        clickable: Array.from(clickables).slice(0, 5).map((el, i) => ({
          selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
          index: i,
          text: el.textContent.trim().substring(0, 30)
        })),
        draggable: Array.from(draggables).slice(0, 3).map((el, i) => ({
          selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
          index: i
        }))
      };
    });

    console.log('Found elements:', JSON.stringify(elements));

    // Hover test
    console.log('\\nHover test...');
    for (let i = 0; i < Math.min(3, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.hover(el.selector);
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, ``01_hover_`${i}.png``) });
        console.log(``Hover OK: `${el.selector}``);
        results.push({ test: 'hover', element: el.selector, status: 'pass' });
      } catch (err) {
        console.log(``Hover FAIL: `${err.message}``);
        results.push({ test: 'hover', element: 'unknown', status: 'fail', error: err.message });
        allPassed = false;
      }
    }

    // Click test
    console.log('\\nClick test...');
    for (let i = 0; i < Math.min(3, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.click(el.selector);
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, ``02_click_`${i}.png``) });
        console.log(``Click OK: `${el.selector}``);
        results.push({ test: 'click', element: el.selector, status: 'pass' });
      } catch (err) {
        console.log(``Click FAIL: `${err.message}``);
        results.push({ test: 'click', element: 'unknown', status: 'fail', error: err.message });
        allPassed = false;
      }
    }

    // Double-click test
    console.log('\\nDouble-click test...');
    for (let i = 0; i < Math.min(2, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.dblclick(el.selector);
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, ``03_dblclick_`${i}.png``) });
        console.log(``Double-click OK: `${el.selector}``);
        results.push({ test: 'doubleclick', element: el.selector, status: 'pass' });
      } catch (err) {
        console.log(``Double-click FAIL: `${err.message}``);
        results.push({ test: 'doubleclick', element: 'unknown', status: 'fail', error: err.message });
        allPassed = false;
      }
    }

    // Drag test
    console.log('\\nDrag test...');
    for (let i = 0; i < elements.draggable.length; i++) {
      try {
        const el = elements.draggable[i];
        const box = await page.locator(el.selector).boundingBox();
        if (box) {
          await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
          await page.mouse.down();
          await page.mouse.move(box.x + box.width / 2 + 100, box.y + box.height / 2 + 50, { steps: 10 });
          await page.mouse.up();
          await page.waitForTimeout(500);
          await page.screenshot({ path: path.join(screenshotDir, ``04_drag_`${i}.png``) });
          console.log(``Drag OK: `${el.selector}``);
          results.push({ test: 'drag', element: el.selector, status: 'pass' });
        }
      } catch (err) {
        console.log(``Drag FAIL: `${err.message}``);
        results.push({ test: 'drag', element: 'unknown', status: 'fail', error: err.message });
        allPassed = false;
      }
    }

    // Final screenshot
    await page.screenshot({ path: path.join(screenshotDir, '99_final.png'), fullPage: true });

    await browser.close();

    // Output results
    console.log('\\n' + '='.repeat(60));
    console.log(``Total: `${results.length}, Pass: `${results.filter(r => r.status === 'pass').length}, Fail: `${results.filter(r => r.status === 'fail').length}``);
    console.log('='.repeat(60));
    console.log('JSON_RESULT_START');
    console.log(JSON.stringify({ success: allPassed, results: results }));
    console.log('JSON_RESULT_END');

    process.exit(allPassed ? 0 : 1);

  } catch (error) {
    console.error('FATAL:', error.message);
    console.log('JSON_RESULT_START');
    console.log(JSON.stringify({ success: false, error: error.message, results: [] }));
    console.log('JSON_RESULT_END');
    process.exit(1);
  }
})();
"@

$jsFile = Join-Path $PWD ".claude\playwright-test-temp.js"
Set-Content -Path $jsFile -Value $jsContent -Encoding UTF8

# Run test
try {
    $output = node $jsFile 2>&1 | Out-String
    Write-Host $output

    # Parse JSON result
    if ($output -match '(?s)JSON_RESULT_START\s*\n(.+?)\n\s*JSON_RESULT_END') {
        $jsonResult = $matches[1]
        $testResults = $jsonResult | ConvertFrom-Json

        # Generate report
        $reportContent = @"
# HTML Interaction Test Report

## File: ``$HtmlFilePath``
- Time: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- Status: $(if ($testResults.success) { '✅ PASS' } else { '❌ FAIL' })

## Results
- Total: $($testResults.results.Count)
- Pass: $($testResults.results | Where-Object { $_.status -eq 'pass' } | Measure-Object | Select-Object -ExpandProperty Count)
- Fail: $($testResults.results | Where-Object { $_.status -eq 'fail' } | Measure-Object | Select-Object -ExpandProperty Count)

## Details

$(foreach ($r in $testResults.results) {
"- **$($r.test.ToUpper())** [$($r.element)]: $(if ($r.status -eq 'pass') { '✅' } else { '❌' }) $(if ($r.error) { "Error: $($r.error)" })
"
})

## Screenshots
Directory: ``$ScreenshotDir``

"@
        Set-Content -Path $ResultFile -Value $reportContent -Encoding UTF8

        if ($testResults.success) {
            exit 0
        } else {
            exit 1
        }
    } else {
        Write-Error "Failed to parse test results"
        exit 1
    }
} finally {
    # Clean up
    if (Test-Path $jsFile) {
        Remove-Item $jsFile -Force
    }
}
