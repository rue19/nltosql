import { useMemo, useState } from 'react'
import { AlertCircle, Play, Table2, BarChart3, Download } from 'lucide-react'
import { runQuery, QueryResponse } from './api/client'
import QueryInput from './components/QueryInput'
import ResultTable from './components/ResultTable'
import ChartPanel from './components/ChartPanel'
import HistoryPanel from './components/HistoryPanel'
import StatusBar from './components/StatusBar'

interface HistoryItem {
  id: number
  question: string
  timestamp: string
}

type ViewMode = 'table' | 'chart' | 'both'

function App() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [nextId, setNextId] = useState(1)
  const [error, setError] = useState('')
  const [viewMode, setViewMode] = useState<ViewMode>('both')

  const historyMap = useMemo(() => history.reduce<Record<string, HistoryItem>>((acc, item) => {
    acc[item.question] = item
    return acc
  }, {}), [history])

  const execute = async (text: string) => {
    setLoading(true)
    setError('')
    try {
      const response = await runQuery(text)
      setResult(response)
      setHistory((current) => {
        const existing = historyMap[text]
        if (existing) return current
        return [...current, { id: nextId, question: text, timestamp: new Date().toISOString() }]
      })
      setNextId((id) => id + 1)
    } catch (err) {
      setError('Failed to execute query. Refresh and try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!question.trim()) return
    await execute(question.trim())
  }

  const handleHistoryRun = async (text: string) => {
    setQuestion(text)
    await execute(text)
  }

  const handleDelete = (id: number) => {
    setHistory((current) => current.filter((item) => item.id !== id))
  }

  const hasResult = result && !result.error && result.rows.length > 0

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-heading">
          <h2>Query History</h2>
          <p>Session-only history of your recent requests.</p>
        </div>
        <HistoryPanel history={history} onRun={handleHistoryRun} onDelete={handleDelete} />
      </aside>
      <main className="main-panel">
        <div className="top-panel">
          <div className="hero-card">
            <div>
              <p className="eyebrow">Oil & Gas NL2SQL</p>
              <h1>Ask about wells, production, formations, and petrophysics.</h1>
            </div>
          </div>
          <QueryInput
            value={question}
            onChange={setQuestion}
            onSubmit={handleSubmit}
            loading={loading}
          />
          {error ? (
            <div className="alert-bar">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          ) : null}
          {result ? <StatusBar result={result} /> : null}
        </div>
        {hasResult ? (
          <div className="view-toggle-bar">
            <button
              className={`view-toggle-btn ${viewMode === 'table' || viewMode === 'both' ? 'active' : ''}`}
              onClick={() => setViewMode(viewMode === 'table' ? 'both' : 'table')}
            >
              <Table2 size={14} /> Table
            </button>
            <button
              className={`view-toggle-btn ${viewMode === 'chart' || viewMode === 'both' ? 'active' : ''}`}
              onClick={() => setViewMode(viewMode === 'chart' ? 'both' : 'chart')}
            >
              <BarChart3 size={14} /> Chart
            </button>
          </div>
        ) : null}
        <div className="results-area">
          {(!hasResult || viewMode === 'table' || viewMode === 'both') ? (
            <ResultTable result={result} />
          ) : null}
          {hasResult && (viewMode === 'chart' || viewMode === 'both') ? (
            <ChartPanel result={result} />
          ) : null}
        </div>
      </main>
    </div>
  )
}

export default App
