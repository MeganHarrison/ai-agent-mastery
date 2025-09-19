const { chromium } = require('playwright');

async function testAIInsightsPageFixed() {
  console.log('🔍 Starting Fixed AI Insights Page Test...\n');
  
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
    console.log('📝 Test Step 1: Navigate directly to AI Insights page...');
    await page.goto('http://localhost:3009/ai-insights');
    await page.waitForTimeout(5000);
    
    // Take screenshot of the AI Insights page
    console.log('📸 Taking screenshot of AI Insights page after fix...');
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-fixed.png',
      fullPage: true 
    });
    
    console.log('📝 Test Step 2: Check page title and content...');
    const pageTitle = await page.title();
    console.log(`   Page title: ${pageTitle}`);
    
    // Check for AI Insights heading
    const heading = await page.locator('h1').textContent().catch(() => null);
    console.log(`   Main heading: ${heading || 'Not found'}`);
    
    // Check for description
    const description = await page.locator('p').first().textContent().catch(() => null);
    console.log(`   Description: ${description || 'Not found'}`);
    
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
      console.log('   Search field tested - entered "test search"');
      
      // Clear search
      await searchField.fill('');
      await page.waitForTimeout(500);
      console.log('   Search field cleared');
      
      // Take screenshot after search interaction
      await page.screenshot({ 
        path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-search-test.png',
        fullPage: true 
      });
    } else {
      console.log('   No search field found to test');
    }
    
    console.log('📝 Test Step 6: Check for column toggle/settings...');
    const columnToggleButtons = await page.locator('button:has-text("Columns"), button[title*="column"], button[aria-label*="column"]').count();
    console.log(`   Column toggle buttons found: ${columnToggleButtons}`);
    
    console.log('📝 Test Step 7: Check for any visible errors on page...');
    const errorElements = await page.locator('text*="Error", text*="error", [role="alert"]').count();
    console.log(`   Visible error elements: ${errorElements}`);
    
    // Check for "Internal Server Error" specifically
    const serverErrors = await page.locator('text="Internal Server Error"').count();
    console.log(`   Internal server errors: ${serverErrors}`);
    
    console.log('📝 Test Step 8: Test responsive design...');
    
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-tablet.png',
      fullPage: true 
    });
    console.log('   Tablet view tested');
    
    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-mobile-fixed.png',
      fullPage: true 
    });
    console.log('   Mobile view tested');
    
    // Reset to desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    
    console.log('📝 Test Step 9: Navigation test - go to home and check sidebar...');
    await page.goto('http://localhost:3009');
    await page.waitForTimeout(3000);
    
    // Look for AI Insights link in navigation
    const aiInsightsNavLinks = await page.locator('a:has-text("AI Insights")').count();
    console.log(`   AI Insights nav links found: ${aiInsightsNavLinks}`);
    
    if (aiInsightsNavLinks > 0) {
      console.log('   Clicking AI Insights navigation link...');
      await page.locator('a:has-text("AI Insights")').first().click();
      await page.waitForTimeout(3000);
      
      const currentUrl = page.url();
      console.log(`   Current URL after click: ${currentUrl}`);
      
      const isOnAIInsightsPage = currentUrl.includes('/ai-insights');
      console.log(`   Successfully navigated to AI Insights page: ${isOnAIInsightsPage}`);
    } else {
      console.log('   AI Insights navigation link not found');
    }
    
    console.log('\n✅ Fixed AI Insights Page Test Complete!');
    console.log('\n📊 SUMMARY:');
    console.log(`   - Page loads without Internal Server Error: ${serverErrors === 0}`);
    console.log(`   - Has proper heading: ${heading === 'AI Insights'}`);
    console.log(`   - Search functionality: ${searchInputs > 0 ? 'Present' : 'Missing'}`);
    console.log(`   - Filter dropdowns: ${filterSelects}`);
    console.log(`   - Data table: ${dataTables > 0 ? 'Present' : 'Missing'}`);
    console.log(`   - Navigation link: ${aiInsightsNavLinks > 0 ? 'Present' : 'Missing'}`);
    console.log(`   - Console errors: ${consoleErrors.length}`);
    
    if (consoleErrors.length > 0) {
      console.log('   Console error details:');
      consoleErrors.forEach((error, index) => {
        console.log(`     ${index + 1}. ${error}`);
      });
    }
    
    const testSuccess = serverErrors === 0 && dataTables > 0 && heading === 'AI Insights';
    console.log(`\n🎯 Overall Test Status: ${testSuccess ? 'PASSED ✅' : 'NEEDS ATTENTION ⚠️'}`);
    
    return {
      success: testSuccess,
      hasDataTable: dataTables > 0,
      hasSearch: searchInputs > 0,
      hasNavigation: aiInsightsNavLinks > 0,
      serverErrors: serverErrors,
      consoleErrors: consoleErrors.length
    };
    
  } catch (error) {
    console.error('❌ Test failed with error:', error);
    await page.screenshot({ 
      path: '/Users/meganharrison/Documents/github/ai-agent-mastery3/6_Agent_Deployment/screenshots/ai-insights-test-error.png',
      fullPage: true 
    });
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

testAIInsightsPageFixed();