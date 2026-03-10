# Full HTML Interaction Tester
# 마우스, 키보드, 폼, 스크롤 인터랙션 전체 테스트

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

# JavaScript 테스트 파일 생성
$jsContent = @"
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const screenshotDir = '$jsScreenshotDir';
  const fileUrl = '$fileUrl';
  const results = [];
  let allPassed = true;

  function addResult(test, element, status, error = null) {
    results.push({ test, element, status, error });
    if (status === 'fail') allPassed = false;
  }

  try {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

    console.log('🌐 Loading:', fileUrl);
    await page.goto(fileUrl, { waitUntil: 'load', timeout: 10000 });

    // Initial screenshot
    await page.screenshot({ path: path.join(screenshotDir, '00_initial.png'), fullPage: true });
    console.log('📸 Initial screenshot saved');

    // ================================================================
    // 요소 탐지
    // ================================================================
    const elements = await page.evaluate(() => {
      return {
        clickable: Array.from(document.querySelectorAll('button, a, [onclick], [role="button"]')).slice(0, 5).map((el, i) => ({
          selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.split(' ')[0] : ''),
          index: i,
          text: el.textContent.trim().substring(0, 30)
        })),
        draggable: Array.from(document.querySelectorAll('[draggable="true"]')).slice(0, 3).map((el, i) => ({
          selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
          index: i
        })),
        inputs: Array.from(document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea')).slice(0, 3).map((el, i) => ({
          selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
          type: el.type || 'textarea',
          index: i
        })),
        checkboxes: Array.from(document.querySelectorAll('input[type="checkbox"]')).slice(0, 3).map((el, i) => ({
          selector: 'input[type="checkbox"]' + (el.id ? '#' + el.id : ''),
          index: i
        })),
        radios: Array.from(document.querySelectorAll('input[type="radio"]')).slice(0, 3).map((el, i) => ({
          selector: 'input[type="radio"]' + (el.id ? '#' + el.id : ''),
          index: i
        })),
        selects: Array.from(document.querySelectorAll('select')).slice(0, 3).map((el, i) => ({
          selector: 'select' + (el.id ? '#' + el.id : ''),
          index: i
        })),
        scrollable: document.body.scrollHeight > window.innerHeight
      };
    });

    console.log('🔍 Found elements:', JSON.stringify(elements));

    // ================================================================
    // 1. 마우스 인터랙션
    // ================================================================
    console.log('\\n🖱️  === 마우스 인터랙션 테스트 ===');

    // 1.1 Hover
    console.log('\\n1.1 Hover...');
    for (let i = 0; i < Math.min(3, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.hover(el.selector);
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, ``01_hover_`${i}.png``) });
        console.log(``  ✅ Hover: `${el.selector}``);
        addResult('hover', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Hover FAIL: `${err.message}``);
        addResult('hover', 'unknown', 'fail', err.message);
      }
    }

    // 1.2 Click
    console.log('\\n1.2 Click...');
    for (let i = 0; i < Math.min(3, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.click(el.selector);
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, ``02_click_`${i}.png``) });
        console.log(``  ✅ Click: `${el.selector}``);
        addResult('click', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Click FAIL: `${err.message}``);
        addResult('click', 'unknown', 'fail', err.message);
      }
    }

    // 1.3 Double-click
    console.log('\\n1.3 Double-click...');
    for (let i = 0; i < Math.min(2, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.dblclick(el.selector);
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, ``03_dblclick_`${i}.png``) });
        console.log(``  ✅ Double-click: `${el.selector}``);
        addResult('doubleclick', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Double-click FAIL: `${err.message}``);
        addResult('doubleclick', 'unknown', 'fail', err.message);
      }
    }

    // 1.4 Right-click
    console.log('\\n1.4 Right-click...');
    for (let i = 0; i < Math.min(2, elements.clickable.length); i++) {
      try {
        const el = elements.clickable[i];
        await page.click(el.selector, { button: 'right' });
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, ``04_rightclick_`${i}.png``) });
        console.log(``  ✅ Right-click: `${el.selector}``);
        addResult('rightclick', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Right-click FAIL: `${err.message}``);
        addResult('rightclick', 'unknown', 'fail', err.message);
      }
    }

    // 1.5 Drag
    console.log('\\n1.5 Drag...');
    for (let i = 0; i < elements.draggable.length; i++) {
      try {
        const el = elements.draggable[i];
        const box = await page.locator(el.selector).boundingBox();
        if (box) {
          await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
          await page.mouse.down();
          await page.mouse.move(box.x + box.width / 2 + 100, box.y + box.height / 2 + 50, { steps: 10 });
          await page.mouse.up();
          await page.waitForTimeout(300);
          await page.screenshot({ path: path.join(screenshotDir, ``05_drag_`${i}.png``) });
          console.log(``  ✅ Drag: `${el.selector}``);
          addResult('drag', el.selector, 'pass');
        }
      } catch (err) {
        console.log(``  ❌ Drag FAIL: `${err.message}``);
        addResult('drag', 'unknown', 'fail', err.message);
      }
    }

    // ================================================================
    // 2. 키보드 인터랙션
    // ================================================================
    console.log('\\n⌨️  === 키보드 인터랙션 테스트 ===');

    // 2.1 Type (텍스트 입력)
    console.log('\\n2.1 Type...');
    for (let i = 0; i < elements.inputs.length; i++) {
      try {
        const el = elements.inputs[i];
        await page.fill(el.selector, '');
        await page.type(el.selector, 'Test Input 123');
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, ``06_type_`${i}.png``) });
        console.log(``  ✅ Type: `${el.selector}``);
        addResult('type', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Type FAIL: `${err.message}``);
        addResult('type', 'unknown', 'fail', err.message);
      }
    }

    // 2.2 Press (키 누르기)
    console.log('\\n2.2 Press Keys...');
    const keysToTest = ['Enter', 'Escape', 'Tab'];
    for (const key of keysToTest) {
      try {
        await page.keyboard.press(key);
        await page.waitForTimeout(200);
        await page.screenshot({ path: path.join(screenshotDir, ``07_press_`${key}.png``) });
        console.log(``  ✅ Press: `${key}``);
        addResult('press', key, 'pass');
      } catch (err) {
        console.log(``  ❌ Press `${key} FAIL: `${err.message}``);
        addResult('press', key, 'fail', err.message);
      }
    }

    // 2.3 Focus/Blur
    console.log('\\n2.3 Focus/Blur...');
    if (elements.inputs.length > 0) {
      try {
        const el = elements.inputs[0];
        await page.focus(el.selector);
        await page.waitForTimeout(200);
        await page.screenshot({ path: path.join(screenshotDir, '08_focus.png') });
        console.log(``  ✅ Focus: `${el.selector}``);
        addResult('focus', el.selector, 'pass');

        await page.evaluate(() => document.activeElement.blur());
        await page.waitForTimeout(200);
        await page.screenshot({ path: path.join(screenshotDir, '09_blur.png') });
        console.log('  ✅ Blur');
        addResult('blur', 'document.activeElement', 'pass');
      } catch (err) {
        console.log(``  ❌ Focus/Blur FAIL: `${err.message}``);
        addResult('focus', 'unknown', 'fail', err.message);
      }
    }

    // ================================================================
    // 3. 폼 인터랙션
    // ================================================================
    console.log('\\n📝 === 폼 인터랙션 테스트 ===');

    // 3.1 Checkbox
    console.log('\\n3.1 Checkbox...');
    for (let i = 0; i < elements.checkboxes.length; i++) {
      try {
        const el = elements.checkboxes[i];
        await page.check(el.selector);
        await page.waitForTimeout(200);
        await page.screenshot({ path: path.join(screenshotDir, ``10_checkbox_check_`${i}.png``) });
        console.log(``  ✅ Check: `${el.selector}``);
        addResult('checkbox-check', el.selector, 'pass');

        await page.uncheck(el.selector);
        await page.waitForTimeout(200);
        await page.screenshot({ path: path.join(screenshotDir, ``11_checkbox_uncheck_`${i}.png``) });
        console.log(``  ✅ Uncheck: `${el.selector}``);
        addResult('checkbox-uncheck', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Checkbox FAIL: `${err.message}``);
        addResult('checkbox', 'unknown', 'fail', err.message);
      }
    }

    // 3.2 Radio button
    console.log('\\n3.2 Radio button...');
    for (let i = 0; i < elements.radios.length; i++) {
      try {
        const el = elements.radios[i];
        await page.check(el.selector);
        await page.waitForTimeout(200);
        await page.screenshot({ path: path.join(screenshotDir, ``12_radio_`${i}.png``) });
        console.log(``  ✅ Radio: `${el.selector}``);
        addResult('radio', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Radio FAIL: `${err.message}``);
        addResult('radio', 'unknown', 'fail', err.message);
      }
    }

    // 3.3 Select (드롭다운)
    console.log('\\n3.3 Select...');
    for (let i = 0; i < elements.selects.length; i++) {
      try {
        const el = elements.selects[i];
        const options = await page.locator(el.selector + ' option').all();
        if (options.length > 1) {
          const value = await options[1].getAttribute('value');
          await page.selectOption(el.selector, value);
          await page.waitForTimeout(200);
          await page.screenshot({ path: path.join(screenshotDir, ``13_select_`${i}.png``) });
          console.log(``  ✅ Select: `${el.selector} = `${value}``);
          addResult('select', el.selector, 'pass');
        }
      } catch (err) {
        console.log(``  ❌ Select FAIL: `${err.message}``);
        addResult('select', 'unknown', 'fail', err.message);
      }
    }

    // ================================================================
    // 4. 스크롤 인터랙션
    // ================================================================
    console.log('\\n📜 === 스크롤 인터랙션 테스트 ===');

    // 4.1 Scroll down
    console.log('\\n4.1 Scroll down...');
    if (elements.scrollable) {
      try {
        await page.evaluate(() => window.scrollBy(0, 300));
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, '14_scroll_down.png') });
        console.log('  ✅ Scroll down');
        addResult('scroll-down', 'window', 'pass');
      } catch (err) {
        console.log(``  ❌ Scroll down FAIL: `${err.message}``);
        addResult('scroll-down', 'window', 'fail', err.message);
      }
    }

    // 4.2 Scroll up
    console.log('\\n4.2 Scroll up...');
    if (elements.scrollable) {
      try {
        await page.evaluate(() => window.scrollBy(0, -300));
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, '15_scroll_up.png') });
        console.log('  ✅ Scroll up');
        addResult('scroll-up', 'window', 'pass');
      } catch (err) {
        console.log(``  ❌ Scroll up FAIL: `${err.message}``);
        addResult('scroll-up', 'window', 'fail', err.message);
      }
    }

    // 4.3 Scroll to element
    console.log('\\n4.3 Scroll to element...');
    if (elements.clickable.length > 0) {
      try {
        const el = elements.clickable[0];
        await page.locator(el.selector).scrollIntoViewIfNeeded();
        await page.waitForTimeout(300);
        await page.screenshot({ path: path.join(screenshotDir, '16_scroll_to_element.png') });
        console.log(``  ✅ Scroll to element: `${el.selector}``);
        addResult('scroll-to-element', el.selector, 'pass');
      } catch (err) {
        console.log(``  ❌ Scroll to element FAIL: `${err.message}``);
        addResult('scroll-to-element', 'unknown', 'fail', err.message);
      }
    }

    // 4.4 Mouse wheel
    console.log('\\n4.4 Mouse wheel...');
    try {
      await page.mouse.wheel(0, 200);
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(screenshotDir, '17_mouse_wheel.png') });
      console.log('  ✅ Mouse wheel');
      addResult('mouse-wheel', 'page', 'pass');
    } catch (err) {
      console.log(``  ❌ Mouse wheel FAIL: `${err.message}``);
      addResult('mouse-wheel', 'page', 'fail', err.message);
    }

    // Final screenshot
    await page.screenshot({ path: path.join(screenshotDir, '99_final.png'), fullPage: true });

    await browser.close();

    // ================================================================
    // 결과 출력
    // ================================================================
    console.log('\\n' + '='.repeat(60));
    console.log('📊 테스트 결과 요약');
    console.log('='.repeat(60));
    console.log(``Total: `${results.length}, Pass: `${results.filter(r => r.status === 'pass').length}, Fail: `${results.filter(r => r.status === 'fail').length}``);
    console.log('='.repeat(60));
    console.log('JSON_RESULT_START');
    console.log(JSON.stringify({ success: allPassed, results: results }));
    console.log('JSON_RESULT_END');

    process.exit(allPassed ? 0 : 1);

  } catch (error) {
    console.error('❌ FATAL:', error.message);
    console.log('JSON_RESULT_START');
    console.log(JSON.stringify({ success: false, error: error.message, results: [] }));
    console.log('JSON_RESULT_END');
    process.exit(1);
  }
})();
"@

$jsFile = Join-Path $PWD ".claude\playwright-test-full-temp.js"
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
        $passCount = $testResults.results | Where-Object { $_.status -eq 'pass' } | Measure-Object | Select-Object -ExpandProperty Count
        $failCount = $testResults.results | Where-Object { $_.status -eq 'fail' } | Measure-Object | Select-Object -ExpandProperty Count

        $reportContent = @"
# HTML Full Interaction Test Report

## File: ``$HtmlFilePath``
- Time: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- Status: $(if ($testResults.success) { '✅ PASS' } else { '❌ FAIL' })

## Summary
- Total: $($testResults.results.Count)
- Pass: $passCount ✅
- Fail: $failCount ❌

## Results by Category

### 🖱️ 마우스 인터랙션
$(foreach ($r in $testResults.results | Where-Object { $_.test -in @('hover', 'click', 'doubleclick', 'rightclick', 'drag') }) {
"- **$($r.test)** [$($r.element)]: $(if ($r.status -eq 'pass') { '✅' } else { '❌' }) $(if ($r.error) { "Error: $($r.error)" })
"
})

### ⌨️ 키보드 인터랙션
$(foreach ($r in $testResults.results | Where-Object { $_.test -in @('type', 'press', 'focus', 'blur') }) {
"- **$($r.test)** [$($r.element)]: $(if ($r.status -eq 'pass') { '✅' } else { '❌' }) $(if ($r.error) { "Error: $($r.error)" })
"
})

### 📝 폼 인터랙션
$(foreach ($r in $testResults.results | Where-Object { $_.test -in @('checkbox-check', 'checkbox-uncheck', 'radio', 'select') }) {
"- **$($r.test)** [$($r.element)]: $(if ($r.status -eq 'pass') { '✅' } else { '❌' }) $(if ($r.error) { "Error: $($r.error)" })
"
})

### 📜 스크롤 인터랙션
$(foreach ($r in $testResults.results | Where-Object { $_.test -in @('scroll-down', 'scroll-up', 'scroll-to-element', 'mouse-wheel') }) {
"- **$($r.test)** [$($r.element)]: $(if ($r.status -eq 'pass') { '✅' } else { '❌' }) $(if ($r.error) { "Error: $($r.error)" })
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
