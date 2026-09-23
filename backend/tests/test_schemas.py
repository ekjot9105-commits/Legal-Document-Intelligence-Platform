from datetime import datetime, timezone
from app.schemas.document import Document, DocumentStatus, ApiError

def test_document_schema_valid():
    doc = Document(
        id="doc-123",
        filename="test.pdf",
        uploaded_at=datetime.now(timezone.utc),
        status=DocumentStatus.ready,
        owner_id="user-456"
    )
    assert doc.id == "doc-123"
    assert doc.status == "ready"

def test_apierror_schema_valid():
    err = ApiError(
        error_code="VALIDATION_ERROR",
        message="Invalid input",
        timestamp=datetime.now(timezone.utc)
    )
    assert err.error_code == "VALIDATION_ERROR"
