// Small reusable table: pass the columns (a header and how to show each cell) and the rows.
import type { ReactNode } from 'react'

interface Column<T> {
  header: string
  render: (row: T) => ReactNode
}

interface SimpleTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  rowKey: (row: T) => string | number
  emptyMessage?: string
}

export default function SimpleTable<T>({
  columns,
  rows,
  rowKey,
  emptyMessage = 'No data for this selection.',
}: SimpleTableProps<T>) {
  if (rows.length === 0) return <p className="hint">{emptyMessage}</p>

  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.header}>{column.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((column) => (
                <td key={column.header}>{column.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}