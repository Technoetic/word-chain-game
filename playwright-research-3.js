const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    console.log('Navigating to Anthropic API streaming documentation...');
    await page.goto('https://docs.anthropic.com/en/api/messages-streaming', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    console.log('Page loaded. Taking full page screenshot...');

    // Create screenshots directory if it doesn't exist
    const screenshotDir = path.join(__dirname, '.claude', 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Take full page screenshot
    const screenshotPath = path.join(screenshotDir, 'research-3.png');
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });
    console.log(`Screenshot saved to: ${screenshotPath}`);

    console.log('Extracting text content...');

    // Extract all text content
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Create research directory if it doesn't exist
    const researchDir = path.join(__dirname, '.claude');
    if (!fs.existsSync(researchDir)) {
      fs.mkdirSync(researchDir, { recursive: true });
    }

    // Save text content
    const textPath = path.join(researchDir, 'research-raw-3.txt');
    fs.writeFileSync(textPath, content, 'utf8');
    console.log(`Text content saved to: ${textPath}`);

    console.log('Research completed successfully!');
    console.log(`- Screenshot: ${screenshotPath}`);
    console.log(`- Text content: ${textPath}`);
    console.log(`- Content length: ${content.length} characters`);

  } catch (error) {
    console.error('Error during research:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
