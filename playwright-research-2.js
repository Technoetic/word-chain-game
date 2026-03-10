const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Create screenshots directory if it doesn't exist
    const screenshotDir = path.join(process.cwd(), '.claude', 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Visit the FastAPI WebSocket documentation
    console.log('Navigating to FastAPI WebSocket documentation...');
    await page.goto('https://fastapi.tiangolo.com/advanced/websockets/', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });

    // Wait a bit for dynamic content to load
    await page.waitForTimeout(3000);

    // Take a full page screenshot
    const screenshotPath = path.join(screenshotDir, 'research-2.png');
    console.log(`Taking screenshot to ${screenshotPath}...`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    // Extract all text content from the page
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Save extracted text to file
    const textDir = path.join(process.cwd(), '.claude');
    if (!fs.existsSync(textDir)) {
      fs.mkdirSync(textDir, { recursive: true });
    }

    const textFilePath = path.join(textDir, 'research-raw-2.txt');
    console.log(`Saving extracted text to ${textFilePath}...`);
    fs.writeFileSync(textFilePath, content, 'utf8');

    console.log('Successfully completed research!');
    console.log(`Screenshot: ${screenshotPath}`);
    console.log(`Text content: ${textFilePath}`);

  } catch (error) {
    console.error('Error during research:', error);
  } finally {
    await browser.close();
  }
})();
