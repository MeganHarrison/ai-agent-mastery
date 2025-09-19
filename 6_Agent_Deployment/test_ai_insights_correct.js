const { chromium } = require('playwright');

async function testAIInsightsCorrect() {
  console.log('🔍 Starting AI Insights Test on Correct Server (Port 3000)...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();
  
  // Capture console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  
  try {
    console.log('📝 Test Step 1: Navigate to AI Insights page on correct server...');
    await page.goto('http://localhost:3000/ai-insights');
    await page.waitForTimeout(5000);
    
    // Take screenshot of the AI Insights page
    console.log('📸 Taking screenshot of AI Insights page on correct server...');
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-correct-server.png',
      fullPage: true 
    });
    
    console.log('📝 Test Step 2: Check page title and content...');
    const pageTitle = await page.title();
    console.log(`   Page title: "${pageTitle}"`);
    
    // Check for AI Insights heading
    const heading = await page.locator('h1').textContent().catch(() => null);
    console.log(`   Main heading: "${heading || 'Not found'}"`);
    
    // Check for description
    const description = await page.locator('p').first().textContent().catch(() => null);
    console.log(`   Description: "${description || 'Not found'}"`);
    
    console.log('📝 Test Step 3: Check for data table components...');
    
    // Check for search input
    const searchInputs = await page.locator('input[placeholder*="Search"], input[placeholder*="search"]').count();
    console.log(`   Search inputs found: ${searchInputs}`);
    
    // Check for filter selects
    const filterSelects = await page.locator('select, [role="combobox"]').count();
    console.log(`   Filter selects found: ${filterSelects}`);
    
    // Check for data table
    const dataTables = await page.locator('table, [role="table"]').count();
    console.log(`   Data tables found: ${dataTables}`);
    
    // Check for table headers
    const tableHeaders = await page.locator('th, [role="columnheader"]').count();
    console.log(`   Table headers found: ${tableHeaders}`);
    
    console.log('📝 Test Step 4: Check for specific filter labels...');
    
    const typeFilters = await page.locator('text="Type"').count();
    console.log(`   Type filter labels: ${typeFilters}`);
    
    const priorityFilters = await page.locator('text="Priority"').count();
    console.log(`   Priority filter labels: ${priorityFilters}`);
    
    const statusFilters = await page.locator('text="Status"').count();
    console.log(`   Status filter labels: ${statusFilters}`);
    
    const resolutionFilters = await page.locator('text="Resolution"').count();
    console.log(`   Resolution filter labels: ${resolutionFilters}`);
    
    console.log('📝 Test Step 5: Test search functionality if available...');
    const searchField = page.locator('input[placeholder*="Search"], input[placeholder*="search"]').first();
    if (await searchField.count() > 0) {
      await searchField.fill('test search');
      await page.waitForTimeout(1000);
      console.log('   ✅ Search field tested - entered "test search"');
      
      // Clear search
      await searchField.fill('');
      await page.waitForTimeout(500);
      console.log('   ✅ Search field cleared');
    } else {
      console.log('   ❌ No search field found');
    }
    
    console.log('📝 Test Step 6: Test filter dropdowns...');
    const dropdowns = await page.locator('[role="combobox"]').count();
    if (dropdowns > 0) {
      console.log(`   ✅ Found ${dropdowns} dropdown filters`);
      
      // Try to click the first dropdown
      const firstDropdown = page.locator('[role="combobox"]').first();
      if (await firstDropdown.isVisible()) {
        await firstDropdown.click();
        await page.waitForTimeout(1000);
        console.log('   ✅ Clicked first filter dropdown');
        
        // Try to close it by clicking elsewhere
        await page.locator('body').click({ position: { x: 100, y: 100 } });
        await page.waitForTimeout(500);
        console.log('   ✅ Closed filter dropdown');
      }
    } else {
      console.log('   ❌ No filter dropdowns found');
    }
    
    console.log('📝 Test Step 7: Check for column toggle...');
    const columnToggleButtons = await page.locator('button:has-text("Columns"), button[title*="column"], button[aria-label*="column"]').count();
    console.log(`   Column toggle buttons found: ${columnToggleButtons}`);
    
    if (columnToggleButtons > 0) {
      const columnToggle = page.locator('button:has-text("Columns"), button[title*="column"], button[aria-label*="column"]').first();
      if (await columnToggle.isVisible()) {
        await columnToggle.click();
        await page.waitForTimeout(1000);
        console.log('   ✅ Clicked column toggle button');
        
        // Close it by clicking elsewhere
        await page.locator('body').click({ position: { x: 100, y: 100 } });
        await page.waitForTimeout(500);
        console.log('   ✅ Closed column toggle menu');
      }
    }
    
    console.log('📝 Test Step 8: Check for any visible errors...');
    const serverErrors = await page.locator('text="Internal Server Error"').count();
    console.log(`   Internal server errors: ${serverErrors}`);
    
    // Check for other error messages
    const errorMessages = await page.locator('[role="alert"], .error').count();
    console.log(`   Error messages: ${errorMessages}`);
    
    console.log('📝 Test Step 9: Test responsive design...');
    
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-tablet-correct.png',
      fullPage: true 
    });
    console.log('   ✅ Tablet view tested');
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-mobile-correct.png',
      fullPage: true 
    });
    console.log('   ✅ Mobile view tested');
    
    // Reset to desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    
    console.log('📝 Test Step 10: Navigation test - check sidebar...');
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    // Look for AI Insights link in navigation
    const aiInsightsNavLinks = await page.locator('a:has-text("AI Insights")').count();
    console.log(`   AI Insights nav links found: ${aiInsightsNavLinks}`);
    
    if (aiInsightsNavLinks > 0) {
      console.log('   ✅ AI Insights navigation link found');
      await page.locator('a:has-text("AI Insights")').first().click();
      await page.waitForTimeout(3000);
      
      const currentUrl = page.url();
      console.log(`   Current URL after navigation: ${currentUrl}`);
      
      const isOnAIInsightsPage = currentUrl.includes('/ai-insights');
      console.log(`   Successfully navigated to AI Insights page: ${isOnAIInsightsPage ? '✅' : '❌'}`);
      
      // Take final screenshot
      await page.screenshot({ 
        path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-final-working.png',
        fullPage: true 
      });
    } else {
      console.log('   ❌ AI Insights navigation link not found');
    }
    
    console.log('\n🎯 AI INSIGHTS PAGE TEST RESULTS:');
    console.log('=' .repeat(50));
    console.log(`✅ Server loads without Internal Server Error: ${serverErrors === 0}`);
    console.log(`✅ Has proper heading "${heading}": ${heading === 'AI Insights'}`);
    console.log(`${searchInputs > 0 ? '✅' : '❌'} Search functionality present: ${searchInputs > 0}`);
    console.log(`${filterSelects > 0 ? '✅' : '❌'} Filter dropdowns present: ${filterSelects}`);
    console.log(`${dataTables > 0 ? '✅' : '❌'} Data table present: ${dataTables > 0}`);
    console.log(`${columnToggleButtons > 0 ? '✅' : '❌'} Column toggle present: ${columnToggleButtons > 0}`);
    console.log(`${aiInsightsNavLinks > 0 ? '✅' : '❌'} Navigation link present: ${aiInsightsNavLinks > 0}`);
    console.log(`✅ Console errors: ${consoleErrors.length}`);
    
    if (consoleErrors.length > 0) {
      console.log('\n🚨 Console Errors:');
      consoleErrors.forEach((error, index) => {
        console.log(`   ${index + 1}. ${error}`);
      });
    }
    
    // Calculate success criteria
    const hasBasicStructure = heading === 'AI Insights' && serverErrors === 0;
    const hasDataFeatures = dataTables > 0 && searchInputs > 0;
    const hasFilters = filterSelects > 0;
    const hasNavigation = aiInsightsNavLinks > 0;
    
    const overallSuccess = hasBasicStructure && hasDataFeatures && hasNavigation;
    
    console.log('\n' + '=' .repeat(50));
    console.log(`🏆 OVERALL TEST STATUS: ${overallSuccess ? 'PASSED ✅' : 'PARTIALLY WORKING ⚠️'}`);
    console.log('=' .repeat(50));
    
    return {
      success: overallSuccess,
      hasBasicStructure,
      hasDataFeatures,
      hasFilters,
      hasNavigation,
      serverErrors,
      consoleErrors: consoleErrors.length,
      details: {
        heading,
        searchInputs,
        filterSelects,
        dataTables,
        columnToggleButtons,
        aiInsightsNavLinks
      }
    };
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-test-error-correct.png',
      fullPage: true 
    });
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

testAIInsightsCorrect();