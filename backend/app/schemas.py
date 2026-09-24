from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    owner_id: str
    uploaded_at: datetime
    status: DocumentStatus
    classification: str | None = None
    pages: int = 0
    redaction_count: int = 0


class Citation(BaseModel):
    page: int | None = None
    section: str | None = None
    paragraph: int | None = None


class ClauseOut(BaseModel):
    id: str
    document_id: str
    type: str
    title: str
    source_text: str
    simplified_text: str
    citation: Citation
    confidence_score: float = Field(ge=0, le=1)
    risk_level: str
    reason: str


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_ids: list[str] = Field(min_length=1, max_length=10)


class QAResponse(BaseModel):
    answer: str
    cited_clause_ids: list[str]
    groundedness: str
    confidence: float = Field(ge=0, le=1)


class LLMClause(BaseModel):
    """Strict schema accepted from an external model before it enters storage."""

    type: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    source_text: str = Field(min_length=1, max_length=4000)
    simplified_text: str = Field(min_length=1, max_length=1200)
    citation: Citation
    confidence_score: float = Field(ge=0, le=1)
    risk_level: str = Field(pattern="^(low|medium|high)$")
    reason: str = Field(min_length=1, max_length=500)


class LLMAnswer(BaseModel):
    """Strict grounded-answer schema returned by an external model."""

    answer: str = Field(min_length=1, max_length=4000)
    cited_clause_ids: list[str] = Field(max_length=5)
    groundedness: str = Field(pattern="^(grounded|unsupported)$")
    confidence: float = Field(ge=0, le=1)


class ComparisonChange(BaseModel):
    clause_type: str
    change_type: str
    before: str | None = None
    after: str | None = None
    significance: str


class ComparisonResult(BaseModel):
    document_a_id: str
    document_b_id: str
    changes: list[ComparisonChange]


class ApiError(BaseModel):
    code: str
    message: str
    request_id: str
