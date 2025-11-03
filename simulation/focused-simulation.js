// focused-simulation.js
const { chromium } = require('playwright');

const TARGET_USERS = 50; // Smaller batch for testing
const ACTIVE_URL = "https://seva-sindu-portal.vercel.app";

const indianCities = [
  { city: "Mumbai" }, { city: "Delhi" }, { city: "Bangalore" },
  { city: "Hyderabad" }, { city: "Chennai" }, { city: "Kolkata" }
];

async function simulateUserWithAnalytics(userId, city) {
  let browser;
  try {
    console.log(`👤 User ${userId} from ${city}`);
    
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    // Track analytics requests
    let analyticsCallCount = 0;
    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('_vercel/insights') || url.includes('va.vercel')) {
        analyticsCallCount++;
        console.log(`   📊 Analytics call ${analyticsCallCount}: ${response.status()} - ${url}`);
      }
    });

    await page.setViewportSize({ width: 1920, height: 1080 });
    
    console.log(`   🔗 Navigating to ${ACTIVE_URL}`);
    await page.goto(ACTIVE_URL, {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Wait for analytics to load
    await page.waitForTimeout(3000);
    
    // Simulate interactions
    console.log(`   🖱️ Simulating user behavior...`);
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.waitForTimeout(1000);
    await page.evaluate(() => window.scrollTo(0, 1000));
    await page.waitForTimeout(1000);

    // Try to click a link
    const links = await page.$$('a');
    if (links.length > 0) {
      await links[0].click();
      await page.waitForTimeout(2000);
      await page.goBack();
      await page.waitForTimeout(1000);
    }

    console.log(`   ✅ Completed - ${analyticsCallCount} analytics calls made`);
    return analyticsCallCount;
    
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
    return 0;
  } finally {
    if (browser) await browser.close();
  }
}

async function runFocusedSimulation() {
  console.log('🎯 Starting FOCUSED simulation on active URL');
  console.log(`🌐 Target: ${ACTIVE_URL}`);
  console.log(`👥 Users: ${TARGET_USERS}`);
  console.log('=========================================\n');
  
  let totalAnalyticsCalls = 0;
  let completedUsers = 0;
  
  for (let i = 1; i <= TARGET_USERS; i++) {
    const city = indianCities[Math.floor(Math.random() * indianCities.length)].city;
    const analyticsCalls = await simulateUserWithAnalytics(i, city);
    totalAnalyticsCalls += analyticsCalls;
    completedUsers++;
    
    console.log(`📈 Progress: ${completedUsers}/${TARGET_USERS} users | Total analytics calls: ${totalAnalyticsCalls}\n`);
    
    // Small delay between users
    if (i < TARGET_USERS) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
  
  console.log('=========================================');
  console.log('🎉 SIMULATION COMPLETED');
  console.log(`📊 Total users: ${completedUsers}`);
  console.log(`📊 Total analytics calls: ${totalAnalyticsCalls}`);
  console.log(`📊 Average calls per user: ${(totalAnalyticsCalls / completedUsers).toFixed(1)}`);
  console.log('\n💡 Check your Vercel Analytics dashboard now:');
  console.log('   https://vercel.com/rishiguptarg007-gmailcoms-projects/seva-sindu-portal/analytics');
  console.log('\n⏰ Data should appear within 5-10 minutes');
}

runFocusedSimulation().catch(console.error);
