const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Visit the Korean dictionary open API page
    await page.goto('https://stdict.korean.go.kr/openapi/openApiInfo.do', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Create screenshots directory if it doesn't exist
    const screenshotsDir = path.join(__dirname, '.claude', 'screenshots');
    if (!fs.existsSync(screenshotsDir)) {
      fs.mkdirSync(screenshotsDir, { recursive: true });
    }

    // Take a full page screenshot
    const screenshotPath = path.join(screenshotsDir, 'research-5.png');
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });
    console.log(`Screenshot saved to: ${screenshotPath}`);

    // Extract all text content
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Create research directory if it doesn't exist
    const researchDir = path.join(__dirname, '.claude');
    if (!fs.existsSync(researchDir)) {
      fs.mkdirSync(researchDir, { recursive: true });
    }

    // Save the extracted text content
    const textFilePath = path.join(researchDir, 'research-raw-5.txt');
    fs.writeFileSync(textFilePath, content, 'utf8');
    console.log(`Text content saved to: ${textFilePath}`);

  } catch (error) {
    console.error('Error during script execution:', error);
  } finally {
    await browser.close();
  }
})();
