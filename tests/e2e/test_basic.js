const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const distPath = path.resolve(__dirname, '../../dist/index.html');
  const fileUrl = 'file:///' + distPath.replace(/\\/g, '/');

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => {
    errors.push(`[UNCAUGHT] ${err.message}`);
  });

  console.log('Loading:', fileUrl);
  await page.goto(fileUrl);
  await page.waitForTimeout(1000);

  // Test 1: Start screen visible
  const startScreen = await page.$('#startScreen');
  const startVisible = await startScreen.evaluate(el => el.style.display !== 'none');
  console.log('Test 1 - Start screen visible:', startVisible ? 'PASS' : 'FAIL');

  // Test 2: Game screen hidden
  const gameScreen = await page.$('#gameScreen');
  const gameHidden = await gameScreen.evaluate(el => el.style.display === 'none');
  console.log('Test 2 - Game screen hidden:', gameHidden ? 'PASS' : 'FAIL');

  // Test 3: Start button exists
  const startBtn = await page.$('#startBtn');
  console.log('Test 3 - Start button exists:', startBtn ? 'PASS' : 'FAIL');

  // Test 4: Title text
  const title = await page.$eval('.start-screen__title', el => el.textContent);
  console.log('Test 4 - Title is correct:', title === '끝말잇기' ? 'PASS' : 'FAIL');

  // Test 5: Click start button
  await startBtn.click();
  await page.waitForTimeout(500);
  const gameVisible = await gameScreen.evaluate(el => el.style.display !== 'none');
  console.log('Test 5 - Game screen after click:', gameVisible ? 'PASS' : 'FAIL');

  // Test 6: Word input exists and enabled
  const wordInput = await page.$('#wordInput');
  const inputDisabled = await wordInput.evaluate(el => el.disabled);
  console.log('Test 6 - Word input enabled:', !inputDisabled ? 'PASS' : 'FAIL');

  // Test 7: Timer visible
  const timer = await page.$('.timer__text');
  const timerText = await timer.evaluate(el => el.textContent);
  console.log('Test 7 - Timer shows 15:', timerText === '15' ? 'PASS' : 'FAIL');

  // Report console errors
  if (errors.length > 0) {
    console.log('\n=== CONSOLE ERRORS ===');
    errors.forEach(e => console.log(e));
  } else {
    console.log('\nNo console errors detected.');
  }

  await page.screenshot({ path: path.resolve(__dirname, '../../.claude/screenshots/e2e-basic.png'), fullPage: true });

  await browser.close();
  console.log('\nE2E tests complete.');
})();
