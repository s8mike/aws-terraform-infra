// Tests for the change-password dialog: live checklist and mismatch warning, local checks, API call, and closing.
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { changePassword } from '../api/auth'
import { ApiError } from '../api/client'
import ChangePasswordDialog from './ChangePasswordDialog'

vi.mock('../api/auth')

type User = ReturnType<typeof userEvent.setup>

// Fill the three password fields.
async function fill(user: User, current: string, next: string, confirm: string) {
  await user.type(screen.getByLabelText('Current password'), current)
  await user.type(screen.getByLabelText('New password'), next)
  await user.type(screen.getByLabelText('Confirm new password'), confirm)
}

beforeEach(() => {
  vi.mocked(changePassword).mockReset()
})

describe('live feedback', () => {
  it('shows the rule checklist while the new password is typed', async () => {
    const user = userEvent.setup()
    render(<ChangePasswordDialog onClose={vi.fn()} />)

    await user.type(screen.getByLabelText('New password'), 'abc')

    expect(screen.getByText(/A lowercase letter/)).toHaveClass('rule-met')
    expect(screen.getByText(/An uppercase letter/)).toHaveClass('rule-unmet')
  })

  it('warns as soon as the confirmation differs and clears the warning when it matches', async () => {
    const user = userEvent.setup()
    render(<ChangePasswordDialog onClose={vi.fn()} />)

    await user.type(screen.getByLabelText('New password'), 'Brandnew456#')
    await user.type(screen.getByLabelText('Confirm new password'), 'Brand')
    expect(screen.getByText(/The two new passwords do not match/)).toBeInTheDocument()

    await user.type(screen.getByLabelText('Confirm new password'), 'new456#')
    expect(screen.queryByText(/The two new passwords do not match/)).not.toBeInTheDocument()
  })
})

describe('submitting', () => {
  it('rejects a weak new password without calling the API', async () => {
    const user = userEvent.setup()
    render(<ChangePasswordDialog onClose={vi.fn()} />)

    await fill(user, 'Securepass123!', 'alllowercase1!', 'alllowercase1!')
    await user.click(screen.getByRole('button', { name: 'Change password' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Password must include an uppercase letter.')
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('rejects a confirmation that does not match', async () => {
    const user = userEvent.setup()
    render(<ChangePasswordDialog onClose={vi.fn()} />)

    await fill(user, 'Securepass123!', 'Brandnew456#', 'Brandnew456!')
    await user.click(screen.getByRole('button', { name: 'Change password' }))

    expect(screen.getByRole('alert')).toHaveTextContent('The new password and its confirmation do not match.')
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('rejects a new password equal to the current one', async () => {
    const user = userEvent.setup()
    render(<ChangePasswordDialog onClose={vi.fn()} />)

    await fill(user, 'Securepass123!', 'Securepass123!', 'Securepass123!')
    await user.click(screen.getByRole('button', { name: 'Change password' }))

    expect(screen.getByRole('alert')).toHaveTextContent('The new password must be different from the current one.')
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('sends both passwords, then shows the success message and a Close button', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    vi.mocked(changePassword).mockResolvedValue(undefined)
    render(<ChangePasswordDialog onClose={onClose} />)

    await fill(user, 'Securepass123!', 'Brandnew456#', 'Brandnew456#')
    await user.click(screen.getByRole('button', { name: 'Change password' }))

    expect(changePassword).toHaveBeenCalledWith({ current_password: 'Securepass123!', new_password: 'Brandnew456#' })
    expect(await screen.findByText(/Your password has been changed/)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Close' }))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('shows the server message when the current password is wrong', async () => {
    const user = userEvent.setup()
    vi.mocked(changePassword).mockRejectedValue(new ApiError(400, 'Current password is incorrect'))
    render(<ChangePasswordDialog onClose={vi.fn()} />)

    await fill(user, 'WrongPass999!', 'Brandnew456#', 'Brandnew456#')
    await user.click(screen.getByRole('button', { name: 'Change password' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Current password is incorrect')
  })
})

describe('closing', () => {
  it('closes on Escape and when the dimmed backdrop is clicked, but not when the panel is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<ChangePasswordDialog onClose={onClose} />)

    await user.click(screen.getByRole('heading', { name: 'Change password' }))
    expect(onClose).not.toHaveBeenCalled()

    await user.keyboard('{Escape}')
    expect(onClose).toHaveBeenCalledTimes(1)

    await user.click(screen.getByRole('dialog').parentElement as HTMLElement)
    expect(onClose).toHaveBeenCalledTimes(2)
  })
})