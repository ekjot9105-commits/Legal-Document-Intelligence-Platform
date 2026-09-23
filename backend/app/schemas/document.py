from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

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
    
class ApiError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
