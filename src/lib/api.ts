export type BackendDocument = {
  id: string
  filename: string
  owner_id: string
  uploaded_at: string
  status: 'processing' | 'ready' | 'failed'
  classification: string | null
  pages: number
  redaction_count: number
}

export type BackendClause = {
  id: string
  document_id: string
  type: string
  title: string
  source_text: string
  simplified_text: string
  citation: { page: number | null; section: string | null; paragraph: number | null }
  confidence_score: number
  risk_level: 'low' | 'medium' | 'high'
  reason: string
}

export type BackendQA = {
  answer: string
  cited_clause_ids: string[]
  groundedness: 'grounded' | 'unsupported'
  confidence: number
}

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const USER_ID = import.meta.env.VITE_USER_ID ?? 'demo-user'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers: { 'X-User-Id': USER_ID, ...init?.headers } })
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  return response.json() as Promise<T>
}

export async function uploadDocument(file: File): Promise<BackendDocument> {
  const form = new FormData()
  form.append('file', file)
  return request<BackendDocument>('/api/documents', { method: 'POST', body: form })
}

export function listDocuments(): Promise<BackendDocument[]> {
  return request<BackendDocument[]>('/api/documents')
}

export function getClauses(documentId: string): Promise<BackendClause[]> {
  return request<BackendClause[]>(`/api/documents/${encodeURIComponent(documentId)}/clauses`)
}

export function askDocuments(question: string, documentIds: string[]): Promise<BackendQA> {
  return request<BackendQA>('/api/qa', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, document_ids: documentIds }) })
}

export type BackendComparison = { document_a_id: string; document_b_id: string; changes: { clause_type: string; change_type: string; before?: string; after?: string; significance: string }[] }

export function compareDocuments(documentAId: string, documentBId: string): Promise<BackendComparison> {
  return request<BackendComparison>(`/api/compare?document_a_id=${encodeURIComponent(documentAId)}&document_b_id=${encodeURIComponent(documentBId)}`, { method: 'POST' })
}
