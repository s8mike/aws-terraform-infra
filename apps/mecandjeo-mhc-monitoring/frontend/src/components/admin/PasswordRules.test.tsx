// Tests for the live password checklist: red crosses until a rule is met, green ticks after, and a hint when editing.
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import PasswordRules from './PasswordRules'

describe('PasswordRules', () => {
  it('shows all five rules as unmet (red) for an empty required password', () => {
    render(<PasswordRules password="" required />)

    const items = screen.getAllByRole('listitem')
    expect(items).toHaveLength(5)
    items.forEach((item) => expect(item).toHaveClass('rule-unmet'))
  })

  it('turns the rules that are met green while the rest stay red', () => {
    render(<PasswordRules password="abc" required />)

    expect(screen.getByText(/A lowercase letter/)).toHaveClass('rule-met')
    expect(screen.getByText(/An uppercase letter/)).toHaveClass('rule-unmet')
    expect(screen.getByText(/At least 8 characters/)).toHaveClass('rule-unmet')
  })

  it('shows every rule as met for a valid password', () => {
    render(<PasswordRules password="Securepass123!" required />)

    screen.getAllByRole('listitem').forEach((item) => expect(item).toHaveClass('rule-met'))
  })

  it('shows a "keep current password" hint instead of the list when editing with a blank password', () => {
    render(<PasswordRules password="" required={false} />)

    expect(screen.getByText('Leave the password blank to keep the current one.')).toBeInTheDocument()
    expect(screen.queryByRole('list')).not.toBeInTheDocument()
  })
})