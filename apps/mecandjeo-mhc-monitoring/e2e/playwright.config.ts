// Playwright settings for the browser smoke tests: where the stack is, what to record on failure, and which browser to use.
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  // Runs once before the tests and stops early, with a clear message, if the stack is not running.
  globalSetup: './global-setup.ts',
  // One step at a time: the journey changes shared data, so tests must not run in parallel.
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 180_000,
  expect: { timeout: 10_000 },
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    // The web container of the compose stack. Override with E2E_BASE_URL to test another address.
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:8080',
    // A screenshot and a step-by-step trace are kept only for tests that fail (see the playwright-report folder).
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})