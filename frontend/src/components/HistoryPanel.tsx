import { Trash2 } from 'lucide-react'

interface HistoryItem {
  id: number
  question: string
  timestamp: string
}

interface Props {
  history: HistoryItem[]
  onRun: (question: string) => void
  onDelete: (id: number) => void
}

export default function HistoryPanel({ history, onRun, onDelete }: Props) {
  if (!history.length) {
    return <div className="history-empty">No history yet. Run a query to save it.</div>
  }

  return (
    <div className="history-list">
      {history.map((item) => (
        <div key={item.id} className="history-item">
          <button className="history-action" onClick={() => onRun(item.question)}>
            <div>
              <p>{item.question}</p>
              <small>{new Date(item.timestamp).toLocaleString()}</small>
            </div>
          </button>
          <button className="icon-button" onClick={() => onDelete(item.id)}>
            <Trash2 size={16} />
          </button>
        </div>
      ))}
    </div>
  )
}
