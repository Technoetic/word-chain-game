const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const htmlPath = path.resolve(__dirname, '../../dist/index.html');
const screenshotDir = path.resolve(__dirname, '../../.claude/screenshots/mouse');

async function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

async function testMouseHoverOnStartBtn(browser, page) {
  console.log('\n=== Testing: Hover on startBtn ===');

  // Before hover
  await page.screenshot({
    path: path.join(screenshotDir, '01-startBtn-hover-before.png'),
    fullPage: true
  });
  console.log('Captured: 01-startBtn-hover-before.png');

  // Hover on startBtn
  await page.hover('#startBtn');
  await page.waitForTimeout(300);

  // After hover
  await page.screenshot({
    path: path.join(screenshotDir, '02-startBtn-hover-after.png'),
    fullPage: true
  });
  console.log('Captured: 02-startBtn-hover-after.png');
}

async function testMouseClickOnStartBtn(browser, page) {
  console.log('\n=== Testing: Click on startBtn ===');

  // Before click
  await page.screenshot({
    path: path.join(screenshotDir, '03-startBtn-click-before.png'),
    fullPage: true
  });
  console.log('Captured: 03-startBtn-click-before.png');

  // Click on startBtn
  await page.click('#startBtn');
  await page.waitForTimeout(500);

  // After click - should transition to game screen
  await page.screenshot({
    path: path.join(screenshotDir, '04-startBtn-click-after.png'),
    fullPage: true
  });
  console.log('Captured: 04-startBtn-click-after.png');
}

async function testMouseHoverOnSubmitBtn(browser, page) {
  console.log('\n=== Testing: Hover on submit-btn ===');

  // Make sure we're on the game screen
  const submitBtn = await page.$('.submit-btn');
  if (!submitBtn) {
    console.log('submit-btn not found, skipping this test');
    return;
  }

  // Before hover
  await page.screenshot({
    path: path.join(screenshotDir, '05-submitBtn-hover-before.png'),
    fullPage: true
  });
  console.log('Captured: 05-submitBtn-hover-before.png');

  // Hover on submit-btn
  await page.hover('.submit-btn');
  await page.waitForTimeout(300);

  // After hover
  await page.screenshot({
    path: path.join(screenshotDir, '06-submitBtn-hover-after.png'),
    fullPage: true
  });
  console.log('Captured: 06-submitBtn-hover-after.png');
}

async function testMouseHoverOnMicBtn(browser, page) {
  console.log('\n=== Testing: Hover on mic-btn ===');

  // Make sure we're on the game screen
  const micBtn = await page.$('.mic-btn');
  if (!micBtn) {
    console.log('mic-btn not found, skipping this test');
    return;
  }

  // Before hover
  await page.screenshot({
    path: path.join(screenshotDir, '07-micBtn-hover-before.png'),
    fullPage: true
  });
  console.log('Captured: 07-micBtn-hover-before.png');

  // Hover on mic-btn
  await page.hover('.mic-btn');
  await page.waitForTimeout(300);

  // After hover
  await page.screenshot({
    path: path.join(screenshotDir, '08-micBtn-hover-after.png'),
    fullPage: true
  });
  console.log('Captured: 08-micBtn-hover-after.png');
}

async function main() {
  await ensureDir(screenshotDir);

  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    const fileUrl = `file:///${htmlPath.replace(/\\/g, '/')}`;
    console.log(`Opening: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);

    // Test 1: Hover on startBtn
    await testMouseHoverOnStartBtn(browser, page);

    // Test 2: Click on startBtn (transitions to game screen)
    await testMouseClickOnStartBtn(browser, page);

    // Test 3: Hover on submit-btn
    await testMouseHoverOnSubmitBtn(browser, page);

    // Test 4: Hover on mic-btn
    await testMouseHoverOnMicBtn(browser, page);

    console.log('\n=== All mouse interaction tests completed ===');
    console.log(`Screenshots saved to: ${screenshotDir}`);

  } catch (error) {
    console.error('Error during test:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

main();
