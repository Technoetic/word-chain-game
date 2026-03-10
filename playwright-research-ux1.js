const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  // Create screenshots directory if it doesn't exist
  const screenshotsDir = path.join('.claude', 'screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    console.log('Navigating to https://dribbble.com/search/word-game-ui...');
    await page.goto('https://dribbble.com/search/word-game-ui', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Wait for page to fully load
    await page.waitForTimeout(2000);

    // Take full page screenshot
    console.log('Taking full page screenshot...');
    await page.screenshot({
      path: path.join(screenshotsDir, 'research-ux1.png'),
      fullPage: true
    });

    // Extract all text content
    console.log('Extracting text content...');
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Save to text file
    const outputPath = path.join('.claude', 'research-raw-ux1.txt');
    fs.writeFileSync(outputPath, content, 'utf8');

    console.log(`Success! Files saved:`);
    console.log(`  Screenshot: ${path.join(screenshotsDir, 'research-ux1.png')}`);
    console.log(`  Text content: ${outputPath}`);

  } catch (error) {
    console.error('Error during research:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
