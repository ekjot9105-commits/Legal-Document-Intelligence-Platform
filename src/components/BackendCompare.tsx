import { useState } from 'react'
import type { BackendComparison } from '../lib/api'
import { compareDocuments } from '../lib/api'

type CompareDocument = { id: string; filename: string; version: number }
type CompareProps = { documents: CompareDocument[]; notify: (message: string) => void }
type DisplayChange = { type: string; before: string; after: string; significance: string }

const fallbackChanges: DisplayChange[] = [
  { type: 'Changed obligation', before: '30-day written notice', after: '60-day written notice', significance: 'Potentially important' },
  { type: 'Financial term', before: '₹50,000 penalty', after: '₹75,000 penalty', significance: 'Review amount' },
  { type: 'Added clause', before: 'No auto-renewal', after: 'Auto-renewal added', significance: 'New obligation' },
]

/** Render backend comparison results with a transparent local fallback when the API is offline. */
export default function BackendCompare({ documents, notify }: CompareProps) {
  const [left, setLeft] = useState(documents[0]?.id ?? '')
  const [right, setRight] = useState(documents[1]?.id ?? '')
  const [changes, setChanges] = useState<DisplayChange[]>(fallbackChanges)

  const runComparison = async () => {
    try {
      const result: BackendComparison = await compareDocuments(left, right)
      setChanges(result.changes.map((change) => ({ type: change.clause_type, before: change.before ?? 'Not present', after: change.after ?? 'Not present', significance: change.significance })))
      notify('Comparison refreshed from the backend analysis.')
    } catch {
      setChanges(fallbackChanges)
      notify('Backend unavailable. Showing the local comparison demo.')
    }
  }

  return <>
    <div className="page-title"><div><p className="eyebrow">COMPARE / VERSION INTELLIGENCE</p><h1>What changed?</h1><p className="lede">Meaningful differences across agreements, with noise filtered out.</p></div><button className="primary-button" onClick={runComparison}>Run comparison</button></div>
    <div className="compare-selectors"><div><label>Contract A<select value={left} onChange={(event) => setLeft(event.target.value)}>{documents.map((document) => <option key={document.id} value={document.id}>{document.filename}</option>)}</select></label><span className="version-chip">Version {documents.find((document) => document.id === left)?.version}</span></div><div className="compare-symbol">⇄</div><div><label>Contract B<select value={right} onChange={(event) => setRight(event.target.value)}>{documents.map((document) => <option key={document.id} value={document.id}>{document.filename}</option>)}</select></label><span className="version-chip">Version {documents.find((document) => document.id === right)?.version}</span></div></div>
    <div className="meaningful-banner"><span className="insight-icon">✦</span><div><strong>{changes.length} potentially important contractual changes detected.</strong><p>These are document differences, not conclusions about legality or enforceability.</p></div></div>
    <div className="compare-table"><div className="compare-head"><span>Change type</span><span>Before</span><span>After</span><span>Interpretation</span></div>{changes.map((change) => <div className="compare-row" key={`${change.type}-${change.before}`}><span className="change-type">{change.type}</span><span>{change.before}</span><span className="changed">{change.after}</span><span><b>{change.significance}</b><small>Source clauses aligned by type</small></span></div>)}</div>
    <div className="compare-footer"><strong>Version history</strong><span>Choose two owner-scoped documents to compare</span></div>
  </>
}
