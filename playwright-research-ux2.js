const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Create screenshots directory if it doesn't exist
  const screenshotDir = '.claude/screenshots';
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  try {
    console.log('Navigating to MDN CSS animation page...');
    await page.goto('https://developer.mozilla.org/en-US/docs/Web/CSS/animation', {
      waitUntil: 'networkidle'
    });

    console.log('Taking full page screenshot...');
    await page.screenshot({
      path: path.join(screenshotDir, 'research-ux2.png'),
      fullPage: true
    });

    console.log('Extracting text content...');
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    console.log('Saving extracted text...');
    fs.writeFileSync(
      '.claude/research-raw-ux2.txt',
      content,
      'utf8'
    );

    console.log('Script completed successfully!');
    console.log('Files created:');
    console.log('- .claude/screenshots/research-ux2.png');
    console.log('- .claude/research-raw-ux2.txt');

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
})();
