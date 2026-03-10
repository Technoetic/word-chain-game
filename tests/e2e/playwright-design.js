const { chromium } = require('playwright');
const path = require('path');

const screenshotDir = path.join(__dirname, '../../.claude/screenshots/design');

const viewports = [
  { name: '1280', width: 1280, height: 720 },
  { name: '768', width: 768, height: 1024 },
  { name: '375', width: 375, height: 667 }
];

const htmlPath = 'file:///C:/Users/Admin/Desktop/끝말잇기/dist/index.html';

async function captureScreenshots() {
  const browser = await chromium.launch();

  try {
    console.log('Starting design verification screenshots...');
    console.log(`HTML path: ${htmlPath}`);
    console.log(`Screenshot directory: ${screenshotDir}\n`);

    // 1. Start screen at 1280x720
    console.log('Capturing: Start screen at 1280x720');
    let page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    await page.goto(htmlPath);
    await page.screenshot({ path: `${screenshotDir}/start-1280.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: start-1280.png\n');

    // 2. Start screen at 768x1024 (tablet)
    console.log('Capturing: Start screen at 768x1024 (tablet)');
    page = await browser.newPage({ viewport: { width: 768, height: 1024 } });
    await page.goto(htmlPath);
    await page.screenshot({ path: `${screenshotDir}/start-768.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: start-768.png\n');

    // 3. Start screen at 375x667 (mobile)
    console.log('Capturing: Start screen at 375x667 (mobile)');
    page = await browser.newPage({ viewport: { width: 375, height: 667 } });
    await page.goto(htmlPath);
    await page.screenshot({ path: `${screenshotDir}/start-375.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: start-375.png\n');

    // 4. Game screen at 1280x720
    console.log('Capturing: Game screen at 1280x720');
    page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    await page.goto(htmlPath);
    const startBtn = await page.$('#startBtn');
    if (startBtn) {
      await startBtn.click();
      await page.waitForTimeout(500);
    }
    await page.screenshot({ path: `${screenshotDir}/game-1280.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: game-1280.png\n');

    // 5. Game screen at 768x1024
    console.log('Capturing: Game screen at 768x1024');
    page = await browser.newPage({ viewport: { width: 768, height: 1024 } });
    await page.goto(htmlPath);
    const startBtn2 = await page.$('#startBtn');
    if (startBtn2) {
      await startBtn2.click();
      await page.waitForTimeout(500);
    }
    await page.screenshot({ path: `${screenshotDir}/game-768.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: game-768.png\n');

    // 6. Game screen at 375x667
    console.log('Capturing: Game screen at 375x667');
    page = await browser.newPage({ viewport: { width: 375, height: 667 } });
    await page.goto(htmlPath);
    const startBtn3 = await page.$('#startBtn');
    if (startBtn3) {
      await startBtn3.click();
      await page.waitForTimeout(500);
    }
    await page.screenshot({ path: `${screenshotDir}/game-375.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: game-375.png\n');

    // 7. Game screen with text typed "사과" at 1280x720
    console.log('Capturing: Game screen with typed text "사과" at 1280x720');
    page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
    await page.goto(htmlPath);
    const startBtn4 = await page.$('#startBtn');
    if (startBtn4) {
      await startBtn4.click();
      await page.waitForTimeout(500);
    }

    // Enable the input field if it's disabled
    await page.evaluate(() => {
      const input = document.querySelector('.word-input');
      if (input) {
        input.disabled = false;
      }
    });

    // Focus on input and type text
    const wordInput = await page.$('.word-input');
    if (wordInput) {
      await wordInput.click();
      await page.keyboard.type('사과');
    }

    await page.screenshot({ path: `${screenshotDir}/input-1280.png`, fullPage: true });
    await page.close();
    console.log('✓ Saved: input-1280.png\n');

    console.log('All screenshots captured successfully!');
    console.log(`Files saved to: ${screenshotDir}`);

  } catch (error) {
    console.error('Error capturing screenshots:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

captureScreenshots();
