// What this test proves, in one line.
import { expect, test } from '@playwright/test'
import { adminEmail, adminPassword } from '../helpers/env'
import { signIn } from '../helpers/ui'

test('the admin sees the Users tab first', async ({ page }) => {
  await signIn(page, adminEmail, adminPassword ?? '', /\/admin$/)
  await expect(page.getByRole('heading', { name: 'Users' })).toBeVisible()
})