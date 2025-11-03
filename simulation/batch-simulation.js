// batch-simulation.js
const { chromium } = require('playwright');

// BATCH OPTIMIZED CONFIGURATION
const BATCHES = 100; // 100 batches
const USERS_PER_BATCH = 5; // 4 Indian + 1 Global per batch
const TOTAL_USERS = BATCHES * USERS_PER_BATCH; // 500 total users
const CONCURRENT_BATCHES = 2; // Run 2 batches concurrently for M1 safety

// Expanded global cities (10+ nations)
const INDIAN_CITIES = [
  { city: "Mumbai", state: "Maharashtra" },
  { city: "Delhi", state: "Delhi" },
  { city: "Bangalore", state: "Karnataka" },
  { city: "Hyderabad", state: "Telangana" },
  { city: "Chennai", state: "Tamil Nadu" },
  { city: "Kolkata", state: "West Bengal" },
  { city: "Pune", state: "Maharashtra" },
  { city: "Ahmedabad", state: "Gujarat" }
];

const GLOBAL_CITIES = [
  { city: "London", country: "UK" },
  { city: "New York", country: "USA" },
  { city: "Toronto", country: "Canada" },
  { city: "Sydney", country: "Australia" },
  { city: "Berlin", country: "Germany" },
  { city: "Paris", country: "France" },
  { city: "Tokyo", country: "Japan" },
  { city: "Singapore", country: "Singapore" },
  { city: "Dubai", country: "UAE" },
  { city: "São Paulo", country: "Brazil" },
  { city: "Moscow", country: "Russia" },
  { city: "Seoul", country: "South Korea" },
  { city: "Mexico City", country: "Mexico" },
  { city: "Cairo", country: "Egypt" },
  { city: "Lagos", country: "Nigeria" }
];

// User behaviors
const USER_BEHAVIORS = [
  { type: 'EXPLORER', scrollDepth: 0.8, pages: 3 },
  { type: 'READER', scrollDepth: 0.6, pages: 2 },
  { type: 'SCANNER', scrollDepth: 0.4, pages: 1 }
];

const PAGES = ['/', '/services', '/about', '/contact'];

class BatchTrafficSimulator {
  constructor() {
    this.stats = {
      batchesCompleted: 0,
      usersCompleted: 0,
      usersFailed: 0,
      analyticsCalls: 0,
      startTime: Date.now()
    };
  }

  async simulateBatch(batchNumber) {
    console.log(`\n🔄 Starting Batch ${batchNumber}/${BATCHES}`);
    
    const batchUsers = [];
    
    // Create 4 Indian users
    for (let i = 0; i < 4; i++) {
      batchUsers.push({
        id: (batchNumber - 1) * USERS_PER_BATCH + i + 1,
        location: INDIAN_CITIES[Math.floor(Math.random() * INDIAN_CITIES.length)],
        behavior: USER_BEHAVIORS[Math.floor(Math.random() * USER_BEHAVIORS.length)],
        type: 'Indian'
      });
    }
    
    // Create 1 Global user
    batchUsers.push({
      id: (batchNumber - 1) * USERS_PER_BATCH + 5,
      location: GLOBAL_CITIES[Math.floor(Math.random() * GLOBAL_CITIES.length)],
      behavior: USER_BEHAVIORS[Math.floor(Math.random() * USER_BEHAVIORS.length)],
      type: 'Global'
    });

    // Simulate all users in the batch concurrently
    const batchPromises = batchUsers.map(user => this.simulateUser(user));
    await Promise.all(batchPromises);
    
    this.stats.batchesCompleted++;
    this.stats.usersCompleted += USERS_PER_BATCH;
    
    console.log(`✅ Batch ${batchNumber} completed: 4 Indian + 1 Global user`);
    this.printProgress();
  }

  async simulateUser(user) {
    let browser;
    try {
      browser = await chromium.launch({ 
        headless: true,
        timeout: 20000
      });
      
      const page = await browser.newPage();
      
      // Track analytics
      page.on('response', (response) => {
        if (response.url().includes('_vercel/insights') || response.url().includes('google-analytics') || response.url().includes('gtag')) {
          this.stats.analyticsCalls++;
        }
      });

      await page.setViewportSize({ width: 1920, height: 1080 });
      
      // Simulate user session
      const behavior = user.behavior;
      const pagesToVisit = this.getRandomPages(behavior.pages);
      
      for (const pagePath of pagesToVisit) {
        await page.goto(`https://seva-sindu-portal.vercel.app${pagePath}`, {
          waitUntil: 'domcontentloaded',
          timeout: 10000
        });
        
        // Quick scroll
        await this.quickScroll(page, behavior.scrollDepth);
        
        // Random interaction
        if (Math.random() < 0.4) {
          await this.quickClick(page);
        }
        
        await page.waitForTimeout(800 + Math.random() * 1200);
      }
      
      await page.close();
      
    } catch (error) {
      this.stats.usersFailed++;
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  }

  async quickScroll(page, scrollDepth) {
    const steps = [0.3, 0.6, scrollDepth];
    for (const step of steps) {
      await page.evaluate((pos) => {
        window.scrollTo(0, document.body.scrollHeight * pos);
      }, step);
      await page.waitForTimeout(200 + Math.random() * 500);
    }
  }

  async quickClick(page) {
    try {
      const clickable = await page.$$('a, button');
      if (clickable.length > 0) {
        const element = clickable[Math.floor(Math.random() * clickable.length)];
        await element.click();
        await page.waitForTimeout(800);
      }
    } catch (error) {
      // Ignore click errors
    }
  }

  getRandomPages(count) {
    const shuffled = [...PAGES].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  }

  printProgress() {
    const elapsed = Math.floor((Date.now() - this.stats.startTime) / 1000);
    const rate = this.stats.usersCompleted / elapsed;
    const remainingUsers = TOTAL_USERS - this.stats.usersCompleted;
    const remainingTime = rate > 0 ? Math.floor(remainingUsers / rate) : 0;
    
    console.log(`📊 Progress: ${this.stats.batchesCompleted}/${BATCHES} batches | ` +
                `${this.stats.usersCompleted}/${TOTAL_USERS} users | ` +
                `Rate: ${rate.toFixed(1)} users/sec | ` +
                `ETA: ${this.formatTime(remainingTime)}`);
    console.log(`🌍 Distribution: ${this.stats.usersCompleted} users (${Math.floor(this.stats.usersCompleted * 0.8)} Indian, ${Math.floor(this.stats.usersCompleted * 0.2)} Global)`);
  }

  formatTime(seconds) {
    if (seconds === 0) return 'Calculating...';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}m ${s}s`;
  }

  async run() {
    console.log('🚀 BATCH OPTIMIZED TRAFFIC SIMULATION');
    console.log(`💻 Optimized for M1 MacBook Air`);
    console.log(`🎯 Target: ${BATCHES} batches × ${USERS_PER_BATCH} users = ${TOTAL_USERS} total`);
    console.log(`🌍 Distribution: 4 Indian + 1 Global per batch`);
    console.log(`⚡ Concurrency: ${CONCURRENT_BATCHES} batches simultaneously`);
    console.log('===============================================\n');

    // Process batches with controlled concurrency
    for (let batchStart = 1; batchStart <= BATCHES; batchStart += CONCURRENT_BATCHES) {
      const batchEnd = Math.min(batchStart + CONCURRENT_BATCHES - 1, BATCHES);
      
      const batchPromises = [];
      for (let batchNum = batchStart; batchNum <= batchEnd; batchNum++) {
        batchPromises.push(this.simulateBatch(batchNum));
      }
      
      await Promise.all(batchPromises);
      
      // Small delay between batch groups
      if (batchEnd < BATCHES) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log('\n===============================================');
    console.log('🎉 BATCH SIMULATION COMPLETED!');
    console.log(`📈 Total batches: ${this.stats.batchesCompleted}`);
    console.log(`👥 Total users: ${this.stats.usersCompleted}`);
    console.log(`❌ Failed users: ${this.stats.usersFailed}`);
    console.log(`📊 Analytics calls: ${this.stats.analyticsCalls}`);
    console.log(`⏱️ Total time: ${this.formatTime(Math.floor((Date.now() - this.stats.startTime) / 1000))}`);
    console.log(`🌍 Final distribution: ${Math.floor(this.stats.usersCompleted * 0.8)} Indian, ${Math.floor(this.stats.usersCompleted * 0.2)} Global users`);
    console.log('\n📊 Check your analytics dashboards:');
    console.log('   Google Analytics Real-Time: https://analytics.google.com/');
    console.log('   Vercel Analytics: https://vercel.com/dashboard');
  }
}

// Run the batch optimized simulation
new BatchTrafficSimulator().run().catch(console.error);