import { KeyboardEvent } from 'react'
import { Play } from 'lucide-react'

interface Props {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  loading: boolean
}

export default function QueryInput({ value, onChange, onSubmit, loading }: Props) {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault()
      onSubmit()
    }
  }

  return (
    <div className="card query-card">
      <label htmlFor="nl-query" className="label">
        Ask anything about the wells — e.g. "Show me top 10 wells by cumulative oil production"
      </label>
      <textarea
        id="nl-query"
        className="query-input"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about the wells — e.g. 'Show me top 10 wells by cumulative oil production'"
        rows={4}
      />
      <button className="button primary" onClick={onSubmit} disabled={loading}>
        {loading ? 'Running…' : 'Run Query'}
        <Play size={16} />
      </button>
    </div>
  )
}
