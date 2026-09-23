# Data Contracts

## 1. Document
Represents an uploaded file in the system.

**TypeScript:**
```typescript
type DocumentStatus = 'uploading' | 'processing' | 'ready' | 'failed';

interface Document {
  id: string;
  filename: string;
  uploadedAt: string; // ISO-8601
  status: DocumentStatus;
  ownerId: string;
  classification?: string;
  storagePath?: string;
}
```

**Python (Pydantic):**
```python
class DocumentStatus(str, Enum):
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class Document(BaseModel):
    id: str
    filename: str
    uploaded_at: datetime
    status: DocumentStatus
    owner_id: str
    classification: Optional[str] = None
    storage_path: Optional[str] = None
```

## 2. ApiError
Standard error response shape.

**TypeScript:**
```typescript
interface ApiError {
  errorCode: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string; // ISO-8601
}
```

**Python (Pydantic):**
```python
class ApiError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
```
