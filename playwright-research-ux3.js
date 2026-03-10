const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Visit the flexbox MDN page
    await page.goto('https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox', {
      waitUntil: 'networkidle'
    });

    // Create screenshot directory if it doesn't exist
    const screenshotDir = path.join(process.cwd(), '.claude', 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Take full page screenshot
    await page.screenshot({
      path: path.join(screenshotDir, 'research-ux3.png'),
      fullPage: true
    });

    // Extract all text content
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Create research directory if it doesn't exist
    const researchDir = path.join(process.cwd(), '.claude');
    if (!fs.existsSync(researchDir)) {
      fs.mkdirSync(researchDir, { recursive: true });
    }

    // Save extracted content
    fs.writeFileSync(
      path.join(researchDir, 'research-raw-ux3.txt'),
      content,
      'utf8'
    );

    console.log('Research completed successfully');
    console.log('Screenshot saved to: .claude/screenshots/research-ux3.png');
    console.log('Raw content saved to: .claude/research-raw-ux3.txt');

  } catch (error) {
    console.error('Error during research:', error);
  } finally {
    await browser.close();
  }
})();
