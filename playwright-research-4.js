const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // Navigate to the Korean Wikipedia page about 끝말잇기
    console.log('Navigating to Korean Wikipedia page...');
    await page.goto('https://ko.wikipedia.org/wiki/%EB%81%9D%EB%A7%90%EC%9E%87%EA%B8%B0', {
      waitUntil: 'networkidle'
    });

    // Take a full page screenshot
    console.log('Taking screenshot...');
    const screenshotDir = '.claude/screenshots';
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }

    await page.screenshot({
      path: path.join(screenshotDir, 'research-4.png'),
      fullPage: true
    });

    // Extract all text content from the page
    console.log('Extracting text content...');
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });

    // Save the extracted text content
    const textDir = '.claude';
    if (!fs.existsSync(textDir)) {
      fs.mkdirSync(textDir, { recursive: true });
    }

    fs.writeFileSync(
      path.join(textDir, 'research-raw-4.txt'),
      content,
      'utf8'
    );

    console.log('Successfully completed research:');
    console.log('- Screenshot saved to: .claude/screenshots/research-4.png');
    console.log('- Text content saved to: .claude/research-raw-4.txt');
    console.log('- Content length: ' + content.length + ' characters');
  } catch (error) {
    console.error('Error during research:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
