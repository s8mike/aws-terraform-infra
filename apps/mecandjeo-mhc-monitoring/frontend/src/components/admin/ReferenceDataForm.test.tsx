// Tests for the reference-data form: the locked code explains itself in red when touched, and saves send the right payload.
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createReferenceData, updateReferenceData } from '../../api/admin'
import type { ReferenceData } from '../../api/types'
import ReferenceDataForm from './ReferenceDataForm'

vi.mock('../../api/admin')

const NOTICE = 'The code cannot be changed because past records use it.'

const item: ReferenceData = {
  id: 12,
  category: 'working_area',
  code: 'port_side',
  label: 'Port Side',
  short_key: null,
  description: null,
  is_active: true,
  created_at: '2026-10-07T06:00:00',
  updated_at: '2026-10-07T06:00:00',
}

beforeEach(() => {
  vi.mocked(createReferenceData).mockReset()
  vi.mocked(updateReferenceData).mockReset()
})

describe('locked code field (editing)', () => {
  it('is read-only and labelled as locked, with no notice until it is touched', () => {
    render(<ReferenceDataForm category="working_area" item={item} onSaved={vi.fn()} onCancel={vi.fn()} />)

    expect(screen.getByLabelText('Code (locked)')).toHaveAttribute('readonly')
    expect(screen.queryByText(NOTICE)).not.toBeInTheDocument()
  })

  it('shows the red notice when the field is clicked and hides it when focus leaves', async () => {
    const user = userEvent.setup()
    render(<ReferenceDataForm category="working_area" item={item} onSaved={vi.fn()} onCancel={vi.fn()} />)

    await user.click(screen.getByLabelText('Code (locked)'))
    expect(screen.getByRole('alert')).toHaveTextContent(NOTICE)
    expect(screen.getByRole('alert')).toHaveClass('blocked-notice')

    await user.tab()
    expect(screen.queryByText(NOTICE)).not.toBeInTheDocument()
  })

  it('shows the notice when someone tries to type in it, and the code stays unchanged', async () => {
    const user = userEvent.setup()
    render(<ReferenceDataForm category="working_area" item={item} onSaved={vi.fn()} onCancel={vi.fn()} />)

    await user.type(screen.getByLabelText('Code (locked)'), 'x')

    expect(screen.getByText(NOTICE)).toBeInTheDocument()
    expect(screen.getByLabelText('Code (locked)')).toHaveValue('port_side')
  })
})

describe('adding a value', () => {
  it('has an editable code and never shows the locked notice', async () => {
    const user = userEvent.setup()
    render(<ReferenceDataForm category="working_area" item={null} onSaved={vi.fn()} onCancel={vi.fn()} />)

    const code = screen.getByLabelText('Code')
    expect(code).not.toHaveAttribute('readonly')
    await user.click(code)

    expect(screen.queryByText(NOTICE)).not.toBeInTheDocument()
  })

  it('normalizes the code to lowercase with underscores and saves it in the chosen category', async () => {
    const user = userEvent.setup()
    const onSaved = vi.fn()
    vi.mocked(createReferenceData).mockResolvedValue(item)
    render(<ReferenceDataForm category="working_area" item={null} onSaved={onSaved} onCancel={vi.fn()} />)

    await user.type(screen.getByLabelText('Code'), 'Quay Side')
    await user.type(screen.getByLabelText('Label shown to operators'), 'Quay Side')
    await user.click(screen.getByRole('button', { name: 'Add value' }))

    expect(createReferenceData).toHaveBeenCalledWith(
      expect.objectContaining({ category: 'working_area', code: 'quay_side', label: 'Quay Side', is_active: true }),
    )
    expect(onSaved).toHaveBeenCalledTimes(1)
  })

  it('rejects a code with invalid characters without calling the API', async () => {
    const user = userEvent.setup()
    render(<ReferenceDataForm category="working_area" item={null} onSaved={vi.fn()} onCancel={vi.fn()} />)

    await user.type(screen.getByLabelText('Code'), 'bad!code')
    await user.type(screen.getByLabelText('Label shown to operators'), 'Bad')
    await user.click(screen.getByRole('button', { name: 'Add value' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Code may only contain letters, numbers and underscores.')
    expect(createReferenceData).not.toHaveBeenCalled()
  })
})

describe('editing a value', () => {
  it('says nothing has changed when saved untouched', async () => {
    const user = userEvent.setup()
    render(<ReferenceDataForm category="working_area" item={item} onSaved={vi.fn()} onCancel={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'Save changes' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Nothing has changed.')
    expect(updateReferenceData).not.toHaveBeenCalled()
  })

  it('sends only the field that changed', async () => {
    const user = userEvent.setup()
    vi.mocked(updateReferenceData).mockResolvedValue(item)
    render(<ReferenceDataForm category="working_area" item={item} onSaved={vi.fn()} onCancel={vi.fn()} />)

    const label = screen.getByLabelText('Label shown to operators')
    await user.clear(label)
    await user.type(label, 'Port Side (Quay)')
    await user.click(screen.getByRole('button', { name: 'Save changes' }))

    expect(updateReferenceData).toHaveBeenCalledWith(12, { label: 'Port Side (Quay)' })
  })
})