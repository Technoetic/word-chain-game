const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Visit the MDN documentation page
    await page.goto('https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition');

    // Wait for content to load
    await page.waitForLoadState('networkidle');

    // Create screenshots directory if it doesn't exist
    const screenshotDir = 'C:/Users/Admin/Desktop/끝말잇기/.claude/screenshots';
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    // Take a full page screenshot
    const screenshotPath = path.join(screenshotDir, 'research-1.png');
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
    const researchDir = 'C:/Users/Admin/Desktop/끝말잇기/.claude';
    if (!fs.existsSync(researchDir)) {
      fs.mkdirSync(researchDir, { recursive: true });
    }

    // Save the extracted text content
    const textPath = path.join(researchDir, 'research-raw-1.txt');
    fs.writeFileSync(textPath, content, 'utf8');
    console.log(`Research data saved to: ${textPath}`);
    console.log(`Content length: ${content.length} characters`);

  } catch (error) {
    console.error('Error during research:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
