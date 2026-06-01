import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface QueryResponse {
  question: string
  sql: string
  columns: string[]
  rows: (string | number | null)[][]
  row_count: number
  chart_advice?: {
    chart_type: 'bar' | 'line' | 'scatter' | 'pie' | 'none'
    x_column?: string
    y_column?: string
    title?: string
    reason?: string
  }
  error?: string
}

export async function runQuery(question: string): Promise<QueryResponse> {
  const res = await axios.post(`${BASE}/api/query`, { question })
  return res.data
}

export async function fetchHealth() {
  const res = await axios.get(`${BASE}/api/health`)
  return res.data
}
