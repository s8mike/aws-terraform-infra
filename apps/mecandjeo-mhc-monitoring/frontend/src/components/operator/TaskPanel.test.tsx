// Tests for the operator's task panel: starting a task from the lookup lists, and the rules for ending one.
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { endTask, startTask } from '../../api/operator'
import type { LookupValue, TaskLog } from '../../api/types'
import TaskPanel from './TaskPanel'

vi.mock('../../api/operator')

const workTypes: LookupValue[] = [
  { code: 'discharging', label: 'Discharging', short_key: null },
  { code: 'loading', label: 'Loading', short_key: null },
]
const areas: LookupValue[] = [
  { code: 'deck_free_bay', label: 'Deck Free Bay', short_key: null },
  { code: 'port_side', label: 'Port Side', short_key: null },
]

const task: TaskLog = {
  id: 9,
  shift_id: 2,
  operator_id: 2,
  crane_id: 2,
  nature_of_work: 'discharging',
  working_area: 'deck_free_bay',
  vessel_name: 'MV Demo',
  bay_reference: null,
  container_count: 0,
  started_at: '2026-10-07T15:10:00',
  ended_at: null,
  status: 'active',
  notes: null,
  created_at: '2026-10-07T15:10:00',
  updated_at: '2026-10-07T15:10:00',
}

beforeEach(() => {
  vi.mocked(startTask).mockReset()
  vi.mocked(endTask).mockReset()
})

describe('starting a task', () => {
  it('offers the lookup values and sends the choices with a naive UTC start time', async () => {
    const user = userEvent.setup()
    const onChanged = vi.fn()
    vi.mocked(startTask).mockResolvedValue(task)
    render(<TaskPanel shiftId={2} task={null} workTypes={workTypes} areas={areas} hasActiveDelay={false} onChanged={onChanged} />)

    await user.selectOptions(screen.getByLabelText('Nature of work'), 'discharging')
    await user.selectOptions(screen.getByLabelText('Working area'), 'deck_free_bay')
    await user.type(screen.getByLabelText('Vessel (optional)'), '  MV Test  ')
    await user.click(screen.getByRole('button', { name: 'Start task' }))

    expect(startTask).toHaveBeenCalledWith(
      expect.objectContaining({
        shift_id: 2,
        nature_of_work: 'discharging',
        working_area: 'deck_free_bay',
        vessel_name: 'MV Test',
        started_at: expect.stringMatching(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/),
      }),
    )
    expect(onChanged).toHaveBeenCalledTimes(1)
  })

  it('omits optional fields that were left blank', async () => {
    const user = userEvent.setup()
    vi.mocked(startTask).mockResolvedValue(task)
    render(<TaskPanel shiftId={2} task={null} workTypes={workTypes} areas={areas} hasActiveDelay={false} onChanged={vi.fn()} />)

    await user.selectOptions(screen.getByLabelText('Nature of work'), 'loading')
    await user.selectOptions(screen.getByLabelText('Working area'), 'port_side')
    await user.click(screen.getByRole('button', { name: 'Start task' }))

    const sent = vi.mocked(startTask).mock.calls[0][0]
    expect(sent.vessel_name).toBeUndefined()
    expect(sent.bay_reference).toBeUndefined()
  })

  it('does not start a task until a work type and an area are chosen', async () => {
    const user = userEvent.setup()
    render(<TaskPanel shiftId={2} task={null} workTypes={workTypes} areas={areas} hasActiveDelay={false} onChanged={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'Start task' }))

    expect(startTask).not.toHaveBeenCalled()
  })
})

describe('ending a task', () => {
  it('shows friendly labels for the open task instead of raw codes', () => {
    render(<TaskPanel shiftId={2} task={task} workTypes={workTypes} areas={areas} hasActiveDelay={false} onChanged={vi.fn()} />)

    expect(screen.getByText('Discharging')).toBeInTheDocument()
    expect(screen.getByText('Deck Free Bay')).toBeInTheDocument()
    expect(screen.getByText('MV Demo')).toBeInTheDocument()
  })

  it('blocks ending while a delay is open and explains why in a red notice', () => {
    render(<TaskPanel shiftId={2} task={task} workTypes={workTypes} areas={areas} hasActiveDelay onChanged={vi.fn()} />)

    expect(screen.getByRole('button', { name: 'End task' })).toBeDisabled()
    expect(screen.getByRole('status')).toHaveTextContent('End the active delay before ending the task.')
    expect(screen.getByRole('status')).toHaveClass('blocked-notice')
  })

  it('starts the container count empty and will not end the task without a number', async () => {
    const user = userEvent.setup()
    render(<TaskPanel shiftId={2} task={task} workTypes={workTypes} areas={areas} hasActiveDelay={false} onChanged={vi.fn()} />)

    expect(screen.getByLabelText('Containers moved')).toHaveValue(null)
    await user.click(screen.getByRole('button', { name: 'End task' }))

    expect(endTask).not.toHaveBeenCalled()
  })

  it('ends the task with the typed container count, including a deliberate zero', async () => {
    const user = userEvent.setup()
    const onChanged = vi.fn()
    vi.mocked(endTask).mockResolvedValue(task)
    render(<TaskPanel shiftId={2} task={task} workTypes={workTypes} areas={areas} hasActiveDelay={false} onChanged={onChanged} />)

    await user.type(screen.getByLabelText('Containers moved'), '0')
    await user.click(screen.getByRole('button', { name: 'End task' }))

    expect(endTask).toHaveBeenCalledWith(9, expect.objectContaining({ container_count: 0 }))
    expect(onChanged).toHaveBeenCalledTimes(1)
  })
})