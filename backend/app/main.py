from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .auth import current_user_id
from .config import Settings, get_settings
from .engine import compare_clauses
from .extractors import extract_document
from .llm import LLMService, ProviderUnavailable
from .pii import redact_pii
from .repository import Repository
from .schemas import ComparisonResult, DocumentOut, DocumentStatus, QAResponse, QuestionRequest
from .security import isolate_document_content, validate_upload
from .storage import SecureStorage


def classify_document(text: str) -> str:
    """Classify using transparent signals until a configured classifier adapter is available."""
    lowered = text.lower()
    if "tenant" in lowered or "landlord" in lowered or "rent" in lowered:
        return "Lease agreement"
    if "employee" in lowered or "employer" in lowered or "salary" in lowered:
        return "Employment agreement"
    if "vendor" in lowered or "services" in lowered:
        return "Master services agreement"
    return "Legal document"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the API with explicit dependencies so tests never share production storage."""
    runtime = settings or get_settings()
    repository = Repository(runtime.database_path)
    storage = SecureStorage(runtime)
    llm = LLMService(runtime)
    api = FastAPI(title="Lexora Document Intelligence API", version="0.1.0")
    api.add_middleware(CORSMiddleware, allow_origins=runtime.origins, allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])

    @api.get("/health")
    def health() -> dict[str, str]:
        """Provide a dependency-free liveness check."""
        return {"status": "ok"}

    @api.post("/api/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
    async def upload_document(file: UploadFile = File(...), owner_id: str = Depends(current_user_id)) -> DocumentOut:
        """Validate, redact, extract, classify, and persist a document for its owner."""
        extension = await validate_upload(file, runtime)
        content = await file.read()
        document_id = str(uuid4())
        try:
            extracted = extract_document(content, extension)
            redacted_text, redactions = redact_pii(extracted.text)
            safe_text = isolate_document_content(redacted_text)
            document = DocumentOut(id=document_id, filename=file.filename or "document", owner_id=owner_id, uploaded_at=datetime.now(UTC), status=DocumentStatus.READY, classification=classify_document(safe_text), pages=extracted.pages, redaction_count=len(redactions))
            original_path = storage.save(owner_id, f"{document_id}-original", content)
            storage.save(owner_id, f"{document_id}-redacted", redacted_text.encode("utf-8"))
            repository.create_document(document, str(original_path))
            repository.save_clauses(await llm.extract(owner_id, document_id, redacted_text))
            return document
        except ProviderUnavailable as error:
            storage.delete(owner_id, f"{document_id}-original")
            storage.delete(owner_id, f"{document_id}-redacted")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Configured AI provider unavailable") from error
        except Exception as error:
            storage.delete(owner_id, f"{document_id}-original")
            storage.delete(owner_id, f"{document_id}-redacted")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Document could not be processed") from error

    @api.get("/api/documents", response_model=list[DocumentOut])
    def list_documents(owner_id: str = Depends(current_user_id)) -> list[DocumentOut]:
        """List only documents owned by the authenticated workspace identity."""
        return repository.list_documents(owner_id)

    @api.get("/api/documents/{document_id}/clauses")
    def list_clauses(document_id: str, owner_id: str = Depends(current_user_id)):
        """Return extracted clauses only after ownership has been checked."""
        if not repository.get_document(document_id, owner_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return repository.get_clauses(document_id, owner_id)

    @api.post("/api/qa", response_model=QAResponse)
    async def ask_documents(request: QuestionRequest, owner_id: str = Depends(current_user_id)) -> QAResponse:
        """Answer from extracted clauses only and explicitly flag unsupported questions."""
        clauses = []
        for document_id in request.document_ids:
            if not repository.get_document(document_id, owner_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            clauses.extend(repository.get_clauses(document_id, owner_id))
        try:
            model_answer = await llm.answer(owner_id, request.question, clauses)
        except ProviderUnavailable as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Configured AI provider unavailable") from error
        if model_answer is not None:
            return QAResponse(**model_answer.model_dump())

        question_terms = {term for term in request.question.lower().split() if len(term) > 3}
        relevant = [clause for clause in clauses if question_terms.intersection(set(clause.source_text.lower().split()))]
        if not relevant:
            return QAResponse(answer="This document does not contain enough information to answer that reliably.", cited_clause_ids=[], groundedness="unsupported", confidence=0.12)
        return QAResponse(answer=f"Relevant document information: {relevant[0].simplified_text}", cited_clause_ids=[clause.id for clause in relevant[:3]], groundedness="grounded", confidence=min(clause.confidence_score for clause in relevant[:3]))

    @api.post("/api/compare", response_model=ComparisonResult)
    def compare_documents(document_a_id: str, document_b_id: str, owner_id: str = Depends(current_user_id)) -> ComparisonResult:
        """Compare two owner-scoped clause sets using semantic similarity thresholds."""
        if not repository.get_document(document_a_id, owner_id) or not repository.get_document(document_b_id, owner_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        changes = compare_clauses(document_a_id, repository.get_clauses(document_a_id, owner_id), document_b_id, repository.get_clauses(document_b_id, owner_id))
        return ComparisonResult(document_a_id=document_a_id, document_b_id=document_b_id, changes=changes)

    @api.delete("/api/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_document(document_id: str, owner_id: str = Depends(current_user_id)) -> None:
        """Delete original bytes, redacted bytes, metadata, and derived clauses together."""
        if not repository.get_document(document_id, owner_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        storage.delete(owner_id, f"{document_id}-original")
        storage.delete(owner_id, f"{document_id}-redacted")
        repository.delete_document(document_id, owner_id)

    return api


app = create_app()
