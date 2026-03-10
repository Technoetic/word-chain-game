const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const distPath = path.resolve(__dirname, '../../dist/index.html');
  const fileUrl = 'file:///' + distPath.replace(/\\/g, '/');
  const ssDir = path.resolve(__dirname, '../../.claude/screenshots');

  await page.goto(fileUrl);
  await page.waitForTimeout(500);

  // Screenshot 1: Start screen
  await page.screenshot({ path: path.join(ssDir, 'e2e-01-start-screen.png'), fullPage: true });
  console.log('Screenshot 1: Start screen captured');

  // Screenshot 2: After clicking start
  await page.click('#startBtn');
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(ssDir, 'e2e-02-game-screen.png'), fullPage: true });
  console.log('Screenshot 2: Game screen captured');

  // Screenshot 3: Type a word in input
  await page.fill('#wordInput', '사과');
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(ssDir, 'e2e-03-word-input.png'), fullPage: true });
  console.log('Screenshot 3: Word input captured');

  // Screenshot 4: Press Enter (submit)
  await page.press('#wordInput', 'Enter');
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(ssDir, 'e2e-04-word-submitted.png'), fullPage: true });
  console.log('Screenshot 4: Word submitted captured');

  await browser.close();
  console.log('Screenshot E2E tests complete.');
})();
