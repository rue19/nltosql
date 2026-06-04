import { Clipboard, CheckCircle, BarChart, LineChart, Activity, PieChart } from 'lucide-react'
import { QueryResponse } from '../api/client'

interface Props {
  result: QueryResponse
}

const chartIcons: Record<string, JSX.Element> = {
  bar: <BarChart size={16} />,
  line: <LineChart size={16} />,
  scatter: <Activity size={16} />,
  pie: <PieChart size={16} />,
  none: <CheckCircle size={16} />,
}

export default function StatusBar({ result }: Props) {
  const chartType = result.chart_advice?.chart_type ?? 'none'

  const copySql = async () => {
    await navigator.clipboard.writeText(result.sql)
  }

  return (
    <div className="status-card">
      <div className="sql-block">
        <div className="sql-header">
          <span>Generated SQL</span>
          <button className="copy-button" onClick={copySql}>
            <Clipboard size={14} /> Copy
          </button>
        </div>
        <code>{result.sql}</code>
      </div>
      <div className="status-meta">
        <div className="badge-row">
          <span className="badge">Rows: {result.row_count}</span>
          <span className="badge chart-badge">
            {chartIcons[chartType]}
            {chartType.toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  )
}
