import { test, expect } from '@playwright/test';

test('login/signup have tone layers + transparency', async ({ page }) => {
  for (const path of ['/login', '/signup']) {
    await page.goto(path);
    
    // Check for tone layers
    for (const tone of ['poetic', 'technical', 'plain']) {
      await expect(page.locator(`[data-tone="${tone}"]`).first()).toBeVisible();
    }
    
    // Check for transparency box
    await expect(page.locator('[data-transparency="present"]')).toBeVisible();
    
    // Check all required sections
    for (const section of ['capabilities', 'limitations', 'dependencies', 'dataHandling']) {
      await expect(page.locator(`[data-section="${section}"]`)).toBeVisible();
    }
  }
});

test('ΛiD button has aria-label', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('button', { name: /Log in with Lukhas ID/i })).toBeVisible();
});

test('language toggle works', async ({ page }) => {
  await page.goto('/login');
  
  // Check English is default
  await expect(page.getByText('Welcome back')).toBeVisible();
  
  // Click language toggle
  await page.getByRole('button', { name: /Cambiar a español/i }).click();
  
  // Check Spanish content appears
  await expect(page.getByText('Bienvenido de nuevo')).toBeVisible();
});

test('pricing page has tier cards with RPM/RPD', async ({ page }) => {
  await page.goto('/pricing');
  
  // Check tier cards are present
  await expect(page.locator('[data-tier="T1"]')).toBeVisible();
  await expect(page.locator('[data-tier="T2"]')).toBeVisible();
  await expect(page.locator('[data-tier="T3"]')).toBeVisible();
  await expect(page.locator('[data-tier="T4"]')).toBeVisible();
  await expect(page.locator('[data-tier="T5"]')).toBeVisible();
  
  // Check RPM/RPD values are shown
  await expect(page.getByText('RPM: 30')).toBeVisible();
  await expect(page.getByText('RPD: 1,000')).toBeVisible();
});

test('signup flow navigation', async ({ page }) => {
  await page.goto('/signup');
  
  // Check progress steps
  await expect(page.getByRole('progressbar')).toBeVisible();
  await expect(page.getByText('Step 1 of 4')).toBeVisible();
  
  // Fill email
  await page.fill('#email', 'test@lukhas.ai');
  await page.getByRole('button', { name: /Continue with email/i }).click();
  
  // Should move to verification step
  await expect(page.getByText('Check your email')).toBeVisible();
});

test('transparency box has all required content', async ({ page }) => {
  await page.goto('/login');
  
  const transparencyBox = page.locator('[data-transparency="present"]');
  await expect(transparencyBox).toBeVisible();
  
  // Check headers
  await expect(transparencyBox.getByRole('heading', { name: /Transparency|Transparencia/i })).toBeVisible();
  await expect(transparencyBox.getByRole('heading', { name: /Capabilities|Capacidades/i })).toBeVisible();
  await expect(transparencyBox.getByRole('heading', { name: /Limitations|Limitaciones/i })).toBeVisible();
  await expect(transparencyBox.getByRole('heading', { name: /Dependencies|Dependencias/i })).toBeVisible();
  await expect(transparencyBox.getByRole('heading', { name: /Data handling|Tratamiento de datos/i })).toBeVisible();
});

test('auth copy uses GLYPH encoding (not encryption)', async ({ page }) => {
  await page.goto('/login');
  
  // Check that "Encode → GLYPH" is used (not "Encrypt → GLYPH")
  const content = await page.content();
  expect(content).not.toContain('Encrypt → GLYPH');
  expect(content).toContain('encoding → GLYPH');
});