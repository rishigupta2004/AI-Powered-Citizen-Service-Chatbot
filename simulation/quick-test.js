const { chromium } = require('playwright');

async function testGA() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('🔍 Testing Google Analytics deployment...\n');
  
  let gaDetected = false;
  
  page.on('request', (request) => {
    const url = request.url();
    if (url.includes('google-analytics') || url.includes('gtag')) {
      gaDetected = true;
      console.log('✅ Google Analytics request detected:', url);
    }
  });

  await page.goto('https://seva-sindu-portal.vercel.app');
  await page.waitForTimeout(5000);
  await browser.close();
  
  if (gaDetected) {
    console.log('\n🎉 Google Analytics is WORKING on your live site!');
  } else {
    console.log('\n❌ Google Analytics NOT detected. You need to deploy the code.');
  }
}

testGA();