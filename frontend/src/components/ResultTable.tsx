import { useState } from 'react'
import { QueryResponse } from '../api/client'

interface Props {
  result: QueryResponse | null
}

const formatValue = (value: string | number | null) => {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') return value.toLocaleString()
  const date = new Date(value)
  if (!Number.isNaN(date.getTime()) && /^\d{4}-\d{2}-\d{2}T?/.test(String(value))) {
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }
  return String(value)
}

export default function ResultTable({ result }: Props) {
  if (!result) {
    return (
      <div className="card empty-state">
        <p>No results yet. Run a query to see data here.</p>
      </div>
    )
  }

  if (result.error) {
    return (
      <div className="card empty-state error-state">
        <p>{result.error}</p>
      </div>
    )
  }

  const rowsPerPage = 50
  const [page, setPage] = useState(1)
  const pageCount = Math.max(1, Math.ceil(result.rows.length / rowsPerPage))
  const pageRows = result.rows.slice((page - 1) * rowsPerPage, page * rowsPerPage)

  return (
    <div className="card table-card">
      <div className="table-header">
        <h2>Results</h2>
        <span>{result.row_count.toLocaleString()} rows</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {result.columns.map((column) => (
                <th key={column}>{column.toUpperCase()}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {row.map((value, colIndex) => (
                  <td key={colIndex} className={typeof value === 'number' ? 'numeric' : ''}>
                    {formatValue(value)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {pageCount > 1 ? (
        <div className="pagination">
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>
            Previous
          </button>
          <span>{page} / {pageCount}</span>
          <button disabled={page === pageCount} onClick={() => setPage(page + 1)}>
            Next
          </button>
        </div>
      ) : null}
    </div>
  )
}
