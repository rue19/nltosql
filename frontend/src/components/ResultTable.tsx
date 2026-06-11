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

  const downloadCSV = () => {
    const header = result.columns.join(",");
    const body = result.rows.map(row =>
      row.map(cell => {
        if (cell === null) return "";
        const s = String(cell);
        // Wrap in quotes if contains comma, newline, or quote
        return s.includes(",") || s.includes("\n") || s.includes('"')
          ? `"${s.replace(/"/g, '""')}"`
          : s;
      }).join(",")
    ).join("\n");
    const csv = `${header}\n${body}`;
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `query_results_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card table-card">
      <div className="table-header">
        <div style={{ display: "flex", alignItems: "center" }}>
          <h2>Results</h2>
          <span style={{ marginLeft: 12 }}>{result.row_count.toLocaleString()} rows</span>
          <button
            onClick={downloadCSV}
            style={{
              background: "none",
              border: "1px solid #374151",
              borderRadius: 6,
              color: "#9ca3af",
              fontSize: 11,
              padding: "4px 10px",
              cursor: "pointer",
              marginLeft: 12
            }}>
            ↓ Download CSV
          </button>
        </div>
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
