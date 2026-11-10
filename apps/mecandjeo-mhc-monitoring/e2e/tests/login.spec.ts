// Browser tests for signing in: route protection, a wrong password, the show/hide eye, and the admin sign-in and sign-out.
import { expect, test } from '@playwright/test'
import { adminEmail, adminPassword } from '../helpers/env'
import { signIn, signOut } from '../helpers/ui'

test.describe('login and route protection', () => {
  test('a signed-out visitor is sent to the login page', async ({ page }) => {
    await page.goto('/manager')

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByRole('heading', { name: 'Mecandjeo MHC Monitoring' })).toBeVisible()
  })

  test('a wrong password shows a clear message and stays on the login page', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill(adminEmail)
    await page.getByLabel('Password', { exact: true }).fill('Definitely-Wrong-1!')
    await page.getByRole('button', { name: 'Sign in' }).click()

    await expect(page.getByRole('alert')).toHaveText('Invalid email or password')
    await expect(page).toHaveURL(/\/login$/)
  })

  test('the eye button shows and hides the typed password', async ({ page }) => {
    await page.goto('/login')
    const password = page.getByLabel('Password', { exact: true })
    await password.fill('Secret-1!')
    await expect(password).toHaveAttribute('type', 'password')

    await page.getByRole('button', { name: 'Show password' }).click()
    await expect(password).toHaveAttribute('type', 'text')

    await page.getByRole('button', { name: 'Hide password' }).click()
    await expect(password).toHaveAttribute('type', 'password')
  })

  test('the admin can sign in, reaches the admin screen, and can sign out again', async ({ page }) => {
    await signIn(page, adminEmail, adminPassword ?? '', /\/admin$/)
    await expect(page.getByRole('heading', { name: 'Admin', exact: true })).toBeVisible()

    await signOut(page)
  })
})