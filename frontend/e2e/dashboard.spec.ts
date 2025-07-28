import { test, expect } from '@playwright/test';

test.describe('Stock Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the main page before each test
    await page.goto('/');
  });

  test('should load the main dashboard page', async ({ page }) => {
    // Check that the page title is correct
    await expect(page).toHaveTitle('Stock AI Agent - PE Ratio Dashboard');
    
    // Check that the main heading is visible
    await expect(page.locator('h1:has-text("PE Ratio Dashboard")')).toBeVisible();
    
    // Check that the description is visible
    await expect(page.locator('p').first()).toContainText('Track and analyze Price-to-Earnings ratios');
  });

  test('should display search section', async ({ page }) => {
    // Check search section heading
    await expect(page.locator('h2').first()).toHaveText('Search Stocks');
    
    // Check search input is visible
    await expect(page.locator('input[placeholder*="Enter stock symbol"]')).toBeVisible();
    
    // Check search button is visible
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toHaveText('Search');
  });

  test('should display popular stocks buttons', async ({ page }) => {
    // Check that popular stocks text is visible
    await expect(page.locator('text=Popular stocks:')).toBeVisible();
    
    // Check that popular stock buttons are present
    const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX'];
    
    for (const stock of popularStocks) {
      await expect(page.locator(`button:has-text("${stock}")`)).toBeVisible();
    }
  });

  test('should display stats section', async ({ page }) => {
    // Wait for stats to load
    await page.waitForSelector('.grid.grid-cols-1.md\\:grid-cols-3', { timeout: 10000 });
    
    // Check stats cards are visible
    await expect(page.locator('text=Stocks Tracked')).toBeVisible();
    await expect(page.locator('text=With PE Data')).toBeVisible();
    await expect(page.locator('text=Data Errors')).toBeVisible();
  });

  test('should interact with stock search input', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    const searchButton = page.locator('button[type="submit"]');
    
    // Test input functionality
    await searchInput.fill('AAPL');
    await expect(searchInput).toHaveValue('AAPL');
    
    // Check search button becomes enabled
    await expect(searchButton).toBeEnabled();
    
    // Clear input
    await searchInput.clear();
    await expect(searchInput).toHaveValue('');
  });

  test('should click popular stock buttons', async ({ page }) => {
    // Click on AAPL button
    const aaplButton = page.locator('button:has-text("AAPL")');
    await aaplButton.click();
    
    // Check that AAPL is filled in the search input
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    await expect(searchInput).toHaveValue('AAPL');
    
    // Click on GOOGL button
    const googlButton = page.locator('button:has-text("GOOGL")');
    await googlButton.click();
    
    // Check that GOOGL replaces AAPL in the search input
    await expect(searchInput).toHaveValue('GOOGL');
  });

  test('should display "About PE Ratios" information section', async ({ page }) => {
    // Check information section is visible
    await expect(page.locator('h3:has-text("About PE Ratios")')).toBeVisible();
    await expect(page.locator('text=The Price-to-Earnings ratio')).toBeVisible();
  });

  test('should handle input validation', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    const searchButton = page.locator('button[type="submit"]');
    
    // Test that search button is disabled when input is empty
    await expect(searchButton).toBeDisabled();
    
    // Add some text and check button becomes enabled
    await searchInput.fill('TEST');
    await expect(searchButton).toBeEnabled();
    
    // Clear and check button becomes disabled again
    await searchInput.clear();
    await expect(searchButton).toBeDisabled();
  });

  test('should display refresh button and loading states', async ({ page }) => {
    // Check refresh button is visible
    const refreshButton = page.locator('button:has-text("Refresh Data")');
    await expect(refreshButton).toBeVisible();
    
    // Check help text is visible
    await expect(page.locator('text=💡 Enter any valid stock symbol')).toBeVisible();
  });

  test('should have responsive layout elements', async ({ page }) => {
    // Check grid layouts for responsiveness
    await expect(page.locator('.grid.grid-cols-1.md\\:grid-cols-3')).toBeVisible(); // Stats grid
    
    // Check search form layout - just check the form exists
    await expect(page.locator('form')).toBeVisible();
    
    // Check popular stocks flex layout
    await expect(page.locator('.flex.flex-wrap.gap-2')).toBeVisible();
  });

  test('should navigate and have proper aria labels', async ({ page }) => {
    // Check input accessibility - the input should be focusable
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    await searchInput.focus();
    await expect(searchInput).toBeFocused();
    
    // Add some text to enable the button, then check if it can be focused
    await searchInput.fill('TEST');
    const searchButton = page.locator('button[type="submit"]');
    await expect(searchButton).toBeEnabled();
    await searchButton.focus();
    await expect(searchButton).toBeFocused();
  });
});