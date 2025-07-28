import { test, expect } from '@playwright/test';

test.describe('Basic Setup Tests', () => {
  test('should load the application', async ({ page }) => {
    await page.goto('/');
    
    // Check that the page loads without errors
    await expect(page.locator('body')).toBeVisible();
    
    // Check that we can see the specific main content heading
    await expect(page.locator('h1:has-text("PE Ratio Dashboard")')).toBeVisible();
    
    // Check that we can see the header
    await expect(page.locator('h1:has-text("Stock AI Agent")')).toBeVisible();
  });

  test('should have proper page title', async ({ page }) => {
    await page.goto('/');
    
    // The page should have the correct title
    await expect(page).toHaveTitle('Stock AI Agent - PE Ratio Dashboard');
  });
});