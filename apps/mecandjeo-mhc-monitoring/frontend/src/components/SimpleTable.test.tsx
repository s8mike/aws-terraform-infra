// Tests for the reusable table: headers and rows are rendered from the column definitions, and an empty list shows a message.
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import SimpleTable from './SimpleTable'

interface Row {
  id: number
  name: string
}

const rows: Row[] = [
  { id: 1, name: 'Operator One' },
  { id: 2, name: 'Operator Two' },
]

describe('SimpleTable', () => {
  it('renders a header row and one row per item using each column\'s render function', () => {
    render(
      <SimpleTable
        rows={rows}
        rowKey={(row) => row.id}
        columns={[
          { header: 'Name', render: (row) => row.name },
          { header: 'Id', render: (row) => row.id },
        ]}
      />,
    )

    expect(screen.getAllByRole('row')).toHaveLength(3)
    expect(screen.getByRole('columnheader', { name: 'Name' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'Operator Two' })).toBeInTheDocument()
  })

  it('shows the default message and no table when there are no rows', () => {
    render(<SimpleTable rows={[]} rowKey={(row: Row) => row.id} columns={[{ header: 'Name', render: (row: Row) => row.name }]} />)

    expect(screen.getByText('No data for this selection.')).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('shows a custom empty message when one is given', () => {
    render(
      <SimpleTable
        rows={[]}
        rowKey={(row: Row) => row.id}
        columns={[{ header: 'Name', render: (row: Row) => row.name }]}
        emptyMessage="Nobody is on shift right now."
      />,
    )

    expect(screen.getByText('Nobody is on shift right now.')).toBeInTheDocument()
  })
})