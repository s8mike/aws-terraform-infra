// Small helpers shared by the browser tests: sign in, sign out, and a short pause between timed actions.
import { expect, type Page } from '@playwright/test'

// Sign in through the login form and wait until the expected landing page is open.
export async function signIn(page: Page, email: string, password: string, landing: RegExp): Promise<void> {
  await page.goto('/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(landing)
}

// Sign out with the header button and wait for the login page.
export async function signOut(page: Page): Promise<void> {
  await page.getByRole('button', { name: 'Sign out' }).click()
  await expect(page).toHaveURL(/\/login$/)
}

// The app records times to the second and an end time must be later than its start time,
// so the test pauses just over a second before ending a shift, task or delay it has only just started.
export async function tickSecond(page: Page): Promise<void> {
  await page.waitForTimeout(1100)
}