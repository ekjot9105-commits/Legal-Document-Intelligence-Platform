from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.clause import ClauseModel
from app.schemas.clause import Clause
from app.models.document import DocumentModel

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../ai-pipeline')))
from chains.analysis import detect_missing_clauses, detect_contradictions
from app.core.config import settings

router = APIRouter()

@router.get("/{document_id}/clauses", response_model=list[Clause])
def get_document_clauses(document_id: str, db: Session = Depends(get_db)):
    """Retrieve extracted clauses for a specific document."""
    clauses = db.query(ClauseModel).filter(ClauseModel.document_id == document_id).all()
    return clauses

@router.get("/{document_id}/analysis")
def get_document_analysis(document_id: str, db: Session = Depends(get_db)):
    """Retrieve missing clauses and contradictions for a document."""
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    clauses = db.query(ClauseModel).filter(ClauseModel.document_id == document_id).all()
    
    # Convert ORM models to dicts for analysis functions
    clauses_data = []
    for c in clauses:
        clauses_data.append({
            "id": c.id,
            "type": c.type,
            "source_text": c.source_text
        })
        
    missing_clauses = detect_missing_clauses(clauses_data, doc.classification or "Other Legal Document")
    
    api_key = settings.OPENAI_API_KEY if hasattr(settings, "OPENAI_API_KEY") else None
    contradictions = detect_contradictions(clauses_data, openai_api_key=api_key)
    
    return {
        "missing_clauses": missing_clauses,
        "contradictions": contradictions
    }
