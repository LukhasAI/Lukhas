/**
 * Playwright test for TransparencyBox component accessibility and functionality
 * 
 * To use this test:
 * 1. Install Playwright: npm install --save-dev @playwright/test
 * 2. Add to package.json scripts: "test": "playwright test"
 * 3. Run: npm test
 */

import { test, expect } from '@playwright/test';

test.describe('TransparencyBox Component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the matriz page where the transparency box should appear
    await page.goto('/matriz');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should render transparency box on matriz page', async ({ page }) => {
    // Check that the transparency box is present
    const transparencyBox = page.locator('.transparency-box');
    await expect(transparencyBox).toBeVisible();
    
    // Check that the title is present
    const title = page.locator('#transparency-title');
    await expect(title).toContainText('Transparency & Limitations');
  });

  test('should be accessible with proper ARIA attributes', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    
    // Check ARIA attributes
    await expect(transparencyBox).toHaveAttribute('role', 'complementary');
    await expect(transparencyBox).toHaveAttribute('aria-labelledby', 'transparency-title');
    
    // Check toggle button accessibility
    const toggleButton = transparencyBox.locator('button').first();
    await expect(toggleButton).toHaveAttribute('aria-expanded');
    await expect(toggleButton).toHaveAttribute('aria-controls', 'transparency-content');
  });

  test('should toggle expanded/collapsed state', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    const content = page.locator('#transparency-content');
    
    // Should start collapsed (defaultExpanded={false})
    await expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
    await expect(content).not.toBeVisible();
    
    // Click to expand
    await toggleButton.click();
    await expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    await expect(content).toBeVisible();
    
    // Click to collapse
    await toggleButton.click();
    await expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
    await expect(content).not.toBeVisible();
  });

  test('should display all required transparency sections when expanded', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    
    // Expand the box
    await toggleButton.click();
    
    // Check that all required sections are present
    const sectionsToCheck = [
      'What MATRIZ Does',
      'Limitations', 
      'Dependencies',
      'Data Handling'
    ];
    
    for (const sectionTitle of sectionsToCheck) {
      const section = page.locator('h4').filter({ hasText: sectionTitle });
      await expect(section).toBeVisible();
    }
  });

  test('should contain specific MATRIZ capabilities', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    
    // Expand the box
    await toggleButton.click();
    
    // Check for specific capabilities
    const capabilities = [
      'Tracks AI decision-making processes',
      'Creates audit trails for compliance',
      'Visualizes reasoning chains',
      'Monitors system behavior for drift detection'
    ];
    
    for (const capability of capabilities) {
      await expect(page.locator('text=' + capability)).toBeVisible();
    }
  });

  test('should mention key limitations', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    
    // Expand the box
    await toggleButton.click();
    
    // Check for key limitations
    const limitations = [
      'Does not guarantee decision accuracy',
      'Cannot trace decisions from external AI systems',
      'Real-time monitoring may impact system latency'
    ];
    
    for (const limitation of limitations) {
      await expect(page.locator('text=' + limitation)).toBeVisible();
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    
    // Focus the toggle button with keyboard
    await toggleButton.focus();
    await expect(toggleButton).toBeFocused();
    
    // Press Enter to toggle
    await page.keyboard.press('Enter');
    await expect(toggleButton).toHaveAttribute('aria-expanded', 'true');
    
    // Press Space to toggle
    await page.keyboard.press('Space');
    await expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
  });

  test('should have proper focus indicators', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    
    // Focus the button
    await toggleButton.focus();
    
    // Check that focus ring is visible (this depends on your CSS)
    // You might need to adjust the selector based on your focus styles
    await expect(toggleButton).toHaveClass(/focus:/);
  });

  test('should display support link in footer', async ({ page }) => {
    const transparencyBox = page.locator('.transparency-box');
    const toggleButton = transparencyBox.locator('button').first();
    
    // Expand the box
    await toggleButton.click();
    
    // Check for support link
    const supportLink = page.locator('a[href="/support"]');
    await expect(supportLink).toBeVisible();
    await expect(supportLink).toContainText('support');
  });
});

test.describe('TransparencyBox Component - Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/matriz');
    
    const transparencyBox = page.locator('.transparency-box');
    await expect(transparencyBox).toBeVisible();
    
    // Should still be functional on mobile
    const toggleButton = transparencyBox.locator('button').first();
    await toggleButton.click();
    
    const content = page.locator('#transparency-content');
    await expect(content).toBeVisible();
  });
});

test.describe('TransparencyBox Component - Performance', () => {
  test('should load quickly', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/matriz');
    await page.waitForSelector('.transparency-box');
    
    const endTime = Date.now();
    const loadTime = endTime - startTime;
    
    // Should load within 3 seconds (adjust as needed)
    expect(loadTime).toBeLessThan(3000);
  });
});