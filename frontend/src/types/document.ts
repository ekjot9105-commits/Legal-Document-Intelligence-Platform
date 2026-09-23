export type DocumentStatus = 'uploading' | 'processing' | 'ready' | 'failed';

export interface Document {
  id: string;
  filename: string;
  uploadedAt: string; // ISO-8601
  status: DocumentStatus;
  ownerId: string;
  classification?: string;
  storagePath?: string;
}

export interface ApiError {
  errorCode: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string; // ISO-8601
}
