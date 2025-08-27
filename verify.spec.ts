import { test, expect } from '@playwright/test';

test('homepage has no console errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  await page.goto('/');
  await expect(errors).toHaveLength(0);
});
