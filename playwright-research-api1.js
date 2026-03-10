const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Visit the Anthropic API Messages endpoint documentation
    await page.goto('https://docs.anthropic.com/en/api/messages', {
      waitUntil: 'networkidle'
    });

    // Create screenshots directory if it doesn't exist
    const screenshotDir = path.join(process.cwd(), '.claude', 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Take full page screenshot
    const screenshotPath = path.join(screenshotDir, 'research-api1.png');
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });
    console.log(`Screenshot saved to: ${screenshotPath}`);

    // Extract all text content from the page
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Create research output directory if it doesn't exist
    const outputDir = path.join(process.cwd(), '.claude');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Save extracted text content
    const textFilePath = path.join(outputDir, 'research-raw-api1.txt');
    fs.writeFileSync(textFilePath, content, 'utf8');
    console.log(`Text content saved to: ${textFilePath}`);

    await browser.close();
    console.log('Playwright script completed successfully');
  } catch (error) {
    console.error('Error during script execution:', error);
    await browser.close();
    process.exit(1);
  }
})();
