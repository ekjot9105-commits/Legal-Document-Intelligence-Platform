from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import magic
from app.db.session import get_db, SessionLocal
from app.models.document import DocumentModel
from app.schemas.document import DocumentStatus, Document as DocumentSchema, ApiError
from app.services.extraction import extract_text, ExtractionError
from app.services.pii import detect_and_redact_pii
from app.services.classification import classify_document
from app.services.clause_engine import process_document_clauses
import logging
from app.core.config import settings
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt"
}

def run_clause_extraction(document_id: str, text: str):
    db = SessionLocal()
    try:
        process_document_clauses(db, document_id, text)
    finally:
        db.close()

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Size Check
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB.")
    
    # 2. Magic byte validation
    mime_type = magic.from_buffer(file_bytes, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415, 
            detail=f"Unsupported file type: {mime_type}. Allowed: PDF, DOCX, TXT."
        )
        
    expected_ext = ALLOWED_MIME_TYPES[mime_type]
    actual_ext = file.filename.split('.')[-1].lower()
    
    if actual_ext != expected_ext:
        raise HTTPException(
            status_code=415,
            detail=f"File extension .{actual_ext} does not match detected content type {mime_type}."
        )

    # Create DB entry
    db_doc = DocumentModel(
        filename=file.filename,
        owner_id="mock-user-123", # From phase 0 constraints
        status=DocumentStatus.processing
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    try:
        # Extract text
        raw_text = extract_text(file_bytes, file.filename)
        
        # Detect PII and Redact
        redacted_text, pii_json = detect_and_redact_pii(raw_text)
        
        # Classify
        classification = await classify_document(redacted_text)
        
        # Update DB
        db_doc.status = DocumentStatus.ready
        db_doc.classification = classification
        db_doc.pii_redactions = pii_json
        
        db.commit()
        db.refresh(db_doc)
        
        # Trigger clause extraction in the background
        background_tasks.add_task(run_clause_extraction, db_doc.id, redacted_text)
        
    except Exception as e:
        logger.error(f"Processing failed for {db_doc.id}: {e}")
        db_doc.status = DocumentStatus.failed
        db.commit()
        db.refresh(db_doc)
        raise HTTPException(status_code=500, detail="Document processing failed.")
        
    return db_doc

@router.get("/", response_model=list[DocumentSchema])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(DocumentModel).all()
    return docs

@router.get("/{doc_id}", response_model=DocumentSchema)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Secure delete (remove DB record)
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}
