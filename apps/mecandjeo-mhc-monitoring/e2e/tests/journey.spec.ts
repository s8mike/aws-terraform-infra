// The main browser smoke test: the whole system in a real browser, from an admin preparing a crane and two users,
// through an operator's shift (task, delay, end), to a manager seeing and downloading it, then cleaning up after itself.
import fs from 'node:fs'
import { expect, test, type Page } from '@playwright/test'
import { adminEmail, adminPassword } from '../helpers/env'
import { signIn, signOut, tickSecond } from '../helpers/ui'

const PASSWORD = 'Securepass123!'

// Every run uses its own names (a short time-based code), so repeated runs never collide and test data is easy to spot.
const run = Date.now().toString(36)
const crane = `E2E-${run}`
const vessel = `MV E2E ${run}`
const operator = { name: `E2E Operator ${run}`, email: `e2e-operator-${run}@example.com` }
const manager = { name: `E2E Manager ${run}`, email: `e2e-manager-${run}@example.com` }

// Admin Users tab: add an account through the form and wait until its row appears in the table.
async function addUser(page: Page, account: { name: string; email: string }, role: 'operator' | 'manager') {
  await page.getByRole('button', { name: 'Add user' }).click()
  await page.getByLabel('Full name').fill(account.name)
  await page.getByLabel('Email').fill(account.email)
  await page.getByLabel('Role').selectOption(role)
  await page.getByLabel('Password', { exact: true }).fill(PASSWORD)
  await page.getByRole('button', { name: 'Create user' }).click()
  await expect(page.getByRole('row', { name: new RegExp(account.email) })).toBeVisible()
}

// Admin Users tab: deactivate an account (the confirmation dialog is accepted automatically) and wait for "Inactive".
async function deactivateUser(page: Page, email: string) {
  const row = page.getByRole('row', { name: new RegExp(email) })
  await row.getByRole('button', { name: 'Deactivate' }).click()
  await expect(row).toContainText('Inactive')
}

test('admin prepares users and a crane, an operator works a shift, a manager sees and downloads it', async ({ page }) => {
  // Accept every browser confirmation ("End this shift?", "Deactivate ...?", "Retire ...?").
  page.on('dialog', (dialog) => void dialog.accept())

  await test.step('admin signs in and creates a crane, an operator and a manager', async () => {
    await signIn(page, adminEmail, adminPassword ?? '', /\/admin$/)

    await page.getByRole('tab', { name: 'Cranes' }).click()
    await expect(page.getByRole('heading', { name: 'Cranes (MHC)' })).toBeVisible()
    await page.getByRole('button', { name: 'Add crane' }).click()
    const craneForm = page.locator('form.edit-panel')
    await craneForm.getByLabel('MHC number').fill(crane)
    await craneForm.getByLabel('Code', { exact: true }).fill(crane)
    await craneForm.getByLabel('Name', { exact: true }).fill(`Mobile Harbour Crane ${crane}`)
    await craneForm.getByRole('button', { name: 'Add crane' }).click()
    await expect(page.getByRole('row', { name: new RegExp(crane) })).toBeVisible()

    await page.getByRole('tab', { name: 'Users' }).click()
    await addUser(page, operator, 'operator')
    await addUser(page, manager, 'manager')

    await signOut(page)
  })

  await test.step('operator starts a shift on the new crane and starts a task', async () => {
    await signIn(page, operator.email, PASSWORD, /\/operator$/)

    await page.getByLabel('MHC', { exact: true }).selectOption({ label: crane })
    await page.getByLabel('Shift', { exact: true }).selectOption({ label: 'Shift A' })
    await page.getByRole('button', { name: 'Start shift' }).click()
    await expect(page.getByRole('heading', { name: 'Active shift' })).toBeVisible()

    await page.getByLabel('Nature of work').selectOption({ label: 'Discharging' })
    await page.getByLabel('Working area').selectOption({ label: 'Deck Free Bay' })
    await page.getByLabel('Vessel (optional)').fill(vessel)
    await page.getByRole('button', { name: 'Start task' }).click()
    await expect(page.getByRole('heading', { name: 'Active task' })).toBeVisible()
  })

  await test.step('a delay blocks ending the task until the delay is ended', async () => {
    await page.getByLabel('Delay reason').selectOption({ label: 'Awaiting Trucks' })
    await page.getByRole('button', { name: 'Start delay' }).click()
    await expect(page.getByRole('heading', { name: 'Active delay' })).toBeVisible()

    await expect(page.getByText('End the active delay before ending the task.')).toBeVisible()
    await expect(page.getByRole('button', { name: 'End task' })).toBeDisabled()

    await tickSecond(page)
    await page.getByRole('button', { name: 'End delay' }).click()
    await expect(page.getByText('End the active delay before ending the task.')).toBeHidden()
  })

  await test.step('operator ends the task and the "this shift" numbers update', async () => {
    await tickSecond(page)
    await page.getByLabel('Containers moved').fill('12')
    await page.getByRole('button', { name: 'End task' }).click()
    await expect(page.getByRole('heading', { name: 'Start task' })).toBeVisible()

    await expect(page.getByRole('heading', { name: `This shift - ${crane}` })).toBeVisible()
    const thisShift = page.locator('.card-grid').first()
    await expect(thisShift.locator('.card', { hasText: 'Completed tasks' }).locator('.card-value')).toHaveText('1')
    await expect(thisShift.locator('.card', { hasText: 'Containers moved' }).locator('.card-value')).toHaveText('12')

    // The shift stays open on purpose, so the manager can see the operator on shift.
    await signOut(page)
  })

  await test.step('manager sees the operator on shift, then reads and downloads the report', async () => {
    await signIn(page, manager.email, PASSWORD, /\/manager$/)

    await expect(page.getByRole('heading', { name: 'Operators on shift' })).toBeVisible()
    // The operator's name appears in two tables on this page (operators on shift, and open shifts),
    // so look only inside the "Operators on shift" block.
    const onShift = page.locator('section.panel').filter({ has: page.getByRole('heading', { name: 'Operators on shift' }) })
    await expect(onShift.getByRole('row', { name: new RegExp(operator.name) })).toBeVisible()

    await page.getByRole('tab', { name: 'Reports' }).click()
    await page.getByLabel('MHC', { exact: true }).selectOption({ label: crane })
    await expect(page.locator('.card', { hasText: 'Completed tasks' }).locator('.card-value')).toHaveText('1')
    await expect(page.locator('.card', { hasText: 'Containers moved' }).locator('.card-value')).toHaveText('12')
    await expect(page.getByRole('cell', { name: vessel })).toBeVisible()

    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.getByRole('button', { name: 'Download CSV' }).click(),
    ])
    expect(download.suggestedFilename()).toBe('historical-performance.csv')
    const lines = fs.readFileSync(await download.path(), 'utf-8').trim().split(/\r?\n/)
    expect(lines.length).toBeGreaterThanOrEqual(2)

    await signOut(page)
  })

  await test.step('clean up: the operator ends the shift, then the admin retires the test accounts and crane', async () => {
    await signIn(page, operator.email, PASSWORD, /\/operator$/)
    await tickSecond(page)
    await page.getByRole('button', { name: 'End shift' }).click()
    await expect(page.getByRole('heading', { name: 'Start shift' })).toBeVisible()
    await signOut(page)

    await signIn(page, adminEmail, adminPassword ?? '', /\/admin$/)
    await deactivateUser(page, operator.email)
    await deactivateUser(page, manager.email)

    await page.getByRole('tab', { name: 'Cranes' }).click()
    const craneRow = page.getByRole('row', { name: new RegExp(crane) })
    await craneRow.getByRole('button', { name: 'Retire' }).click()
    await expect(craneRow).toContainText('Retired')
  })
})