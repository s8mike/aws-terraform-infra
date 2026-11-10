// Tests for the number cards: the title is shown, and each card gets a color tone from its label unless one is given.
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import SummaryCards from './SummaryCards'

// The card element that holds a label.
function cardOf(label: string): HTMLElement {
  const card = screen.getByText(label).closest('.card')
  if (!(card instanceof HTMLElement)) throw new Error(`No card found for ${label}`)
  return card
}

describe('SummaryCards', () => {
  it('shows the title and every value with its label', () => {
    render(
      <SummaryCards
        title="This shift - MHC-02"
        items={[
          { label: 'Completed tasks', value: '2' },
          { label: 'Containers moved', value: '15' },
        ]}
      />,
    )

    expect(screen.getByRole('heading', { name: 'This shift - MHC-02' })).toBeInTheDocument()
    expect(cardOf('Containers moved')).toHaveTextContent('15')
  })

  it.each([
    ['Delay time', 'amber'],
    ['Active delays', 'amber'],
    ['Containers moved', 'green'],
    ['Moves per hour', 'green'],
    ['Effective time', 'green'],
    ['Completed tasks', 'blue'],
    ['Shifts', 'blue'],
    ['Operators', 'slate'],
  ])('colors the "%s" card %s', (label, tone) => {
    render(<SummaryCards title="Totals" items={[{ label, value: '1' }]} />)

    expect(cardOf(label)).toHaveClass(`card-tone-${tone}`)
  })

  it('uses an explicit tone instead of the inferred one', () => {
    render(<SummaryCards title="Totals" items={[{ label: 'Delay time', value: '5 min', tone: 'blue' }]} />)

    expect(cardOf('Delay time')).toHaveClass('card-tone-blue')
  })
})