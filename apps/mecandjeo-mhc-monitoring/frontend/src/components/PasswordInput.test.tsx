// Tests for the password field: hidden by default, the eye button shows/hides the text, and it never submits the form.
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import PasswordInput from './PasswordInput'

// A small form that holds the typed value, the way a real screen does.
function Harness({ onSubmit = () => {} }: { onSubmit?: () => void }) {
  const [value, setValue] = useState('')
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit()
      }}
    >
      <PasswordInput id="pw" label="Password" value={value} onChange={setValue} />
    </form>
  )
}

describe('PasswordInput', () => {
  it('hides the typed text by default', () => {
    render(<Harness />)

    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password')
  })

  it('accepts typing', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    await user.type(screen.getByLabelText('Password'), 'Secret1!')

    expect(screen.getByLabelText('Password')).toHaveValue('Secret1!')
  })

  it('shows the text when the eye is clicked and hides it again on a second click', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    await user.click(screen.getByRole('button', { name: 'Show password' }))
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'text')
    expect(screen.getByRole('button', { name: 'Hide password' })).toHaveAttribute('aria-pressed', 'true')

    await user.click(screen.getByRole('button', { name: 'Hide password' }))
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password')
  })

  it('does not submit the form when the eye is clicked', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<Harness onSubmit={onSubmit} />)

    await user.click(screen.getByRole('button', { name: 'Show password' }))

    expect(onSubmit).not.toHaveBeenCalled()
  })
})