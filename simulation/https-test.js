// http-test.js
const https = require('https');

async function makeRequest(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, (res) => {
      console.log(`✅ ${url} - Status: ${res.statusCode}`);
      resolve(res.statusCode);
    });
    
    req.on('error', (err) => {
      console.log(`❌ ${url} - Error: ${err.message}`);
      reject(err);
    });
    
    req.setTimeout(10000, () => {
      req.destroy();
      console.log(`⏰ ${url} - Timeout`);
      reject(new Error('Timeout'));
    });
  });
}

async function testAllUrls() {
  console.log('🌐 Testing all your Vercel URLs...\n');
  
  const urls = [
    'https://seva-sindu-portal.vercel.app',
    'https://seva-sindu-portal-h5y8ydckd-rishiguptarg007-gmailcoms-projects.vercel.app',
    'https://seva-sindu-portal-hr62egz33-rishiguptarg007-gmailcoms-projects.vercel.app'
  ];
  
  for (const url of urls) {
    await makeRequest(url);
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n🎉 Testing completed. Check which URLs are active.');
}

testAllUrls();