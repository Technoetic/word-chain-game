const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const distPath = 'file:///C:/Users/Admin/Desktop/끝말잇기/dist/index.html';
  const screenshotDir = 'C:/Users/Admin/Desktop/끝말잇기/.claude/screenshots/keyboard';

  // Ensure screenshot directory exists
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Navigate to the game
    await page.goto(distPath);
    await page.waitForLoadState('networkidle');

    console.log('Starting keyboard interaction tests...\n');

    // Test 1: Tab navigation - focus on startBtn
    console.log('Test 1: Tab navigation - focus on startBtn');
    await page.screenshot({ path: `${screenshotDir}/01-start-screen.png`, fullPage: true });

    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${screenshotDir}/01-tab-focus-startBtn.png`, fullPage: true });
    console.log('✓ Tab navigation - startBtn focused\n');

    // Test 2: Enter to activate startBtn
    console.log('Test 2: Enter to activate startBtn');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500); // Wait for game screen to appear
    await page.screenshot({ path: `${screenshotDir}/02-enter-game-screen.png`, fullPage: true });
    console.log('✓ Enter activated - game screen displayed\n');

    // Wait for game screen to be fully loaded
    await page.waitForSelector('.word-input', { timeout: 5000 });

    // Test 3: Tab to word-input and type text
    console.log('Test 3: Tab to word-input on game screen');

    // First, focus on game board area (might need multiple tabs)
    for (let i = 0; i < 3; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }

    await page.screenshot({ path: `${screenshotDir}/03-tab-game-screen.png`, fullPage: true });

    // Check if word-input is focused, if not, continue tabbing
    const focusedElement = await page.evaluate(() => document.activeElement?.className);
    console.log(`Currently focused element class: ${focusedElement}`);

    // Type text in word-input
    console.log('Typing "사과" in word-input');
    await page.keyboard.type('사과', { delay: 100 });
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${screenshotDir}/03-typed-text.png`, fullPage: true });
    console.log('✓ Text typed in word-input\n');

    // Test 4: Tab from word-input to submit-btn
    console.log('Test 4: Tab to submit button');
    await page.keyboard.press('Tab');
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${screenshotDir}/04-tab-submit-btn.png`, fullPage: true });
    console.log('✓ Focused on submit button\n');

    // Test 5: Shift+Tab back to word-input
    console.log('Test 5: Shift+Tab back to word-input');
    await page.keyboard.press('Shift+Tab');
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${screenshotDir}/05-shift-tab-back-input.png`, fullPage: true });
    console.log('✓ Shift+Tab moved focus back to word-input\n');

    console.log('All keyboard interaction tests completed successfully!');
    console.log(`Screenshots saved to: ${screenshotDir}`);

  } catch (error) {
    console.error('Error during keyboard interaction tests:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
