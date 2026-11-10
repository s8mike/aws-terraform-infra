// Tests for the operator's shift panel: details are shown, ending is blocked while a task is open, and ending asks first.
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { endShift } from '../../api/operator'
import type { Shift } from '../../api/types'
import ShiftPanel from './ShiftPanel'

vi.mock('../../api/operator')

const shift: Shift = {
  id: 5,
  operator_id: 2,
  crane_id: 2,
  mhc_number: 'MHC-02',
  shift_code: 'B',
  started_at: '2026-10-07T14:00:00',
  ended_at: null,
  status: 'active',
  notes: null,
  created_at: '2026-10-07T14:00:00',
  updated_at: '2026-10-07T14:00:00',
}

beforeEach(() => {
  vi.mocked(endShift).mockReset()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('ShiftPanel', () => {
  it('shows the MHC and shift code', () => {
    render(<ShiftPanel shift={shift} hasActiveTask={false} onChanged={vi.fn()} />)

    expect(screen.getByText('MHC-02')).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
  })

  it('blocks ending the shift while a task is open and says why in a red notice', () => {
    render(<ShiftPanel shift={shift} hasActiveTask onChanged={vi.fn()} />)

    expect(screen.getByRole('button', { name: 'End shift' })).toBeDisabled()
    expect(screen.getByRole('status')).toHaveTextContent('End the active task before ending the shift.')
    expect(screen.getByRole('status')).toHaveClass('blocked-notice')
  })

  it('does nothing when the confirmation is cancelled', async () => {
    const user = userEvent.setup()
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    render(<ShiftPanel shift={shift} hasActiveTask={false} onChanged={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'End shift' }))

    expect(endShift).not.toHaveBeenCalled()
  })

  it('ends the shift with a naive UTC time once confirmed, then asks the page to refresh', async () => {
    const user = userEvent.setup()
    const onChanged = vi.fn()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    vi.mocked(endShift).mockResolvedValue(shift)
    render(<ShiftPanel shift={shift} hasActiveTask={false} onChanged={onChanged} />)

    await user.click(screen.getByRole('button', { name: 'End shift' }))

    expect(endShift).toHaveBeenCalledWith(5, { ended_at: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/) })
    expect(onChanged).toHaveBeenCalledTimes(1)
  })

  it('shows the server message when ending fails', async () => {
    const user = userEvent.setup()
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    vi.mocked(endShift).mockRejectedValue(new ApiError(409, 'End active task before ending shift'))
    render(<ShiftPanel shift={shift} hasActiveTask={false} onChanged={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'End shift' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('End active task before ending shift')
  })
})