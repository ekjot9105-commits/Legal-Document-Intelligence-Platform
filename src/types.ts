export type DocumentStatus = 'ready' | 'processing' | 'failed'

export type DocumentRecord = {
  id: string
  filename: string
  uploadedAt: string
  status: DocumentStatus
  ownerId: string
  classification: string
  storagePath: string
}

export type Clause = {
  id: string
  documentId: string
  type: string
  sourceText: string
  citation: { page: number; section: string }
  confidenceScore: number
  explanation: string
}

export type RiskAssessment = {
  clauseId: string
  riskLevel: 'low' | 'medium' | 'high'
  reason: string
}

export type ApiError = { code: string; message: string; requestId?: string }
