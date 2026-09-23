from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Citation(BaseModel):
    page: Optional[int] = None
    section: Optional[str] = None
    paragraph: Optional[int] = None

class ClauseBase(BaseModel):
    type: str
    source_text: str
    citation: Citation
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    explanation: Optional[str] = None

class ClauseCreate(ClauseBase):
    pass

class Clause(ClauseBase):
    id: str
    document_id: str
    
    model_config = ConfigDict(from_attributes=True)
