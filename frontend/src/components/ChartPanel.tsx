import { QueryResponse } from '../api/client'
import {
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'

interface Props {
  result: QueryResponse | null
}

export default function ChartPanel({ result }: Props) {
  if (!result || !result.chart_advice || result.chart_advice.chart_type === 'none') {
    return (
      <div className="card chart-card empty-state">
        <p>No chart suggested for this result set.</p>
      </div>
    )
  }

  const { chart_type, x_column, y_column, title } = result.chart_advice
  const data = result.rows.map((row) => {
    const rowObj: Record<string, string | number | null> = {}
    result.columns.forEach((column, index) => {
      rowObj[column] = row[index]
    })
    return rowObj
  })

  const primary = '#e8963c'
  const secondary = '#2dd4bf'

  return (
    <div className="card chart-card">
      <div className="chart-header">
        <div>
          <h2>{title ?? 'Suggested chart'}</h2>
          <p>{result.chart_advice.reason}</p>
        </div>
      </div>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={320}>
          {chart_type === 'bar' && x_column && y_column ? (
            <BarChart data={data}>
              <CartesianGrid stroke="#3c4a5a" />
              <XAxis dataKey={x_column} stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip />
              <Bar dataKey={y_column} fill={primary} />
            </BarChart>
          ) : chart_type === 'line' && x_column && y_column ? (
            <LineChart data={data}>
              <CartesianGrid stroke="#3c4a5a" />
              <XAxis dataKey={x_column} stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip />
              <Line type="monotone" dataKey={y_column} stroke={primary} dot={false} />
            </LineChart>
          ) : chart_type === 'scatter' && x_column && y_column ? (
            <ScatterChart>
              <CartesianGrid stroke="#3c4a5a" />
              <XAxis dataKey={x_column} stroke="#fff" />
              <YAxis dataKey={y_column} stroke="#fff" />
              <Tooltip />
              <Scatter name={y_column} data={data} fill={secondary} />
            </ScatterChart>
          ) : chart_type === 'pie' && y_column ? (
            <PieChart>
              <Pie data={data} dataKey={y_column} nameKey={x_column ?? result.columns[0]} outerRadius={120}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index % 2 === 0 ? primary : secondary} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          ) : (
            <div className="chart-unavailable">No valid chart configuration available.</div>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}
