// m1-optimized-simulation.js
const { chromium } = require('playwright');

// M1 OPTIMIZED CONFIGURATION
const TOTAL_USERS = 5000; // Reduced from 100K to 5K for M1
const CONCURRENT_USERS = 8; // Reduced concurrency for M1 memory limits
const INDIAN_RATIO = 0.85;
const BATCH_SIZE = 100; // Process in smaller batches

// Optimized geographic data (reduced size)
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
  { city: "Singapore", country: "Singapore" },
  { city: "Dubai", country: "UAE" }
];

// Simplified user behaviors for M1
const USER_BEHAVIORS = [
  { type: 'EXPLORER', scrollDepth: 0.8, pages: 3 },
  { type: 'READER', scrollDepth: 0.6, pages: 2 },
  { type: 'SCANNER', scrollDepth: 0.4, pages: 1 }
];

const PAGES = ['/', '/services', '/about', '/contact'];

class M1TrafficSimulator {
  constructor() {
    this.stats = {
      started: 0,
      completed: 0,
      failed: 0,
      analyticsCalls: 0,
      startTime: Date.now(),
      batchCount: 0
    };
    this.browserPool = [];
  }

  async getBrowser() {
    // Reuse browsers to save memory
    if (this.browserPool.length > 0) {
      return this.browserPool.pop();
    }
    return await chromium.launch({ 
      headless: true,
      timeout: 30000
    });
  }

  async releaseBrowser(browser) {
    if (this.browserPool.length < CONCURRENT_USERS) {
      this.browserPool.push(browser);
    } else {
      await browser.close();
    }
  }

  async simulateUser(userId) {
    this.stats.started++;
    let browser;
    
    try {
      const userProfile = this.generateUserProfile(userId);
      
      browser = await this.getBrowser();
      const page = await browser.newPage();
      
      // Track analytics calls
      page.on('response', (response) => {
        const url = response.url();
        if (url.includes('_vercel/insights') || url.includes('google-analytics') || url.includes('gtag')) {
          this.stats.analyticsCalls++;
        }
      });

      await page.setViewportSize({ width: 1920, height: 1080 });
      await this.simulateQuickSession(page, userProfile, userId);
      
      this.stats.completed++;
      await page.close();
      
    } catch (error) {
      this.stats.failed++;
    } finally {
      if (browser) {
        await this.releaseBrowser(browser);
      }
    }
  }

  generateUserProfile(userId) {
    const isIndian = Math.random() < INDIAN_RATIO;
    const location = isIndian ? 
      INDIAN_CITIES[Math.floor(Math.random() * INDIAN_CITIES.length)] :
      GLOBAL_CITIES[Math.floor(Math.random() * GLOBAL_CITIES.length)];
    
    const behavior = USER_BEHAVIORS[Math.floor(Math.random() * USER_BEHAVIORS.length)];
    
    return {
      id: userId,
      location,
      behavior
    };
  }

  async simulateQuickSession(page, profile, userId) {
    const behavior = profile.behavior;
    
    // Visit pages
    const pagesToVisit = this.getRandomPages(behavior.pages);
    
    for (const pagePath of pagesToVisit) {
      try {
        await page.goto(`https://seva-sindu-portal.vercel.app${pagePath}`, {
          waitUntil: 'domcontentloaded',
          timeout: 15000
        });
        
        // Quick scroll
        await this.quickScroll(page, behavior.scrollDepth);
        
        // Quick interaction
        if (Math.random() < 0.3) {
          await this.quickClick(page);
        }
        
        await page.waitForTimeout(1000 + Math.random() * 2000);
        
      } catch (error) {
        // Continue with next page on error
      }
    }
  }

  async quickScroll(page, scrollDepth) {
    const steps = [0.3, 0.6, scrollDepth];
    for (const step of steps) {
      await page.evaluate((pos) => {
        window.scrollTo(0, document.body.scrollHeight * pos);
      }, step);
      await page.waitForTimeout(300 + Math.random() * 700);
    }
  }

  async quickClick(page) {
    try {
      const clickable = await page.$$('a, button');
      if (clickable.length > 0) {
        const element = clickable[Math.floor(Math.random() * clickable.length)];
        await element.click();
        await page.waitForTimeout(1000);
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
    const rate = this.stats.completed / elapsed;
    const remaining = rate > 0 ? Math.floor((TOTAL_USERS - this.stats.completed) / rate) : 0;
    
    console.log(`📊 Batch ${this.stats.batchCount} | ${this.stats.completed}/${TOTAL_USERS} | ` +
                `Rate: ${rate.toFixed(1)} users/sec | ` +
                `ETA: ${this.formatTime(remaining)}`);
  }

  formatTime(seconds) {
    if (seconds === 0) return 'Calculating...';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return `${h}h ${m}m ${s}s`;
  }

  async run() {
    console.log('🚀 M1 OPTIMIZED TRAFFIC SIMULATION');
    console.log(`💻 Optimized for M1 MacBook Air (8GB RAM)`);
    console.log(`🎯 Target: ${TOTAL_USERS.toLocaleString()} users`);
    console.log(`⚡ Concurrency: ${CONCURRENT_USERS} users`);
    console.log(`🌍 Distribution: ${Math.round(INDIAN_RATIO * 100)}% India`);
    console.log('===============================================\n');
    
    // Process in batches to manage memory
    for (let batchStart = 1; batchStart <= TOTAL_USERS; batchStart += BATCH_SIZE) {
      this.stats.batchCount++;
      const batchEnd = Math.min(batchStart + BATCH_SIZE - 1, TOTAL_USERS);
      
      console.log(`🔄 Starting batch ${this.stats.batchCount}: Users ${batchStart}-${batchEnd}`);
      
      const batchPromises = [];
      for (let i = batchStart; i <= batchEnd; i++) {
        const promise = this.simulateUser(i);
        batchPromises.push(promise);
        
        // Control concurrency
        if (batchPromises.length >= CONCURRENT_USERS) {
          await Promise.race(batchPromises);
          // Clean up completed promises
          for (let j = batchPromises.length - 1; j >= 0; j--) {
            if (batchPromises[j].isCompleted) {
              batchPromises.splice(j, 1);
            }
          }
        }
      }
      
      // Wait for batch completion
      await Promise.all(batchPromises);
      this.printProgress();
      
      // Clear browser pool between batches to free memory
      for (const browser of this.browserPool) {
        await browser.close();
      }
      this.browserPool = [];
      
      // Small delay between batches
      if (batchEnd < TOTAL_USERS) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    console.log('\n===============================================');
    console.log('🎉 M1 OPTIMIZED SIMULATION COMPLETED!');
    console.log(`📈 Total users: ${this.stats.completed.toLocaleString()}`);
    console.log(`❌ Failed: ${this.stats.failed}`);
    console.log(`📊 Analytics calls: ${this.stats.analyticsCalls.toLocaleString()}`);
    console.log(`⏱️ Total time: ${this.formatTime(Math.floor((Date.now() - this.stats.startTime) / 1000))}`);
    console.log('\n📊 Check your analytics dashboards:');
    console.log('   Google Analytics: https://analytics.google.com/');
    console.log('   Vercel Analytics: https://vercel.com/dashboard');
  }
}

// Run the M1 optimized simulation
new M1TrafficSimulator().run().catch(console.error);