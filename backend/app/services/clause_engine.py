import sys
import os
import uuid
import logging
from sqlalchemy.orm import Session
from app.models.clause import ClauseModel
from app.models.document import DocumentModel
from app.core.config import settings

# Add ai-pipeline to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai-pipeline')))
from chains.chunking import get_document_chunks
from chains.extraction import extract_clauses
from chains.analysis import detect_missing_clauses, detect_contradictions

logger = logging.getLogger(__name__)

def process_document_clauses(db: Session, document_id: str, text: str):
    """
    Orchestrates the extraction of clauses from a document and saves them to the DB.
    """
    logger.info(f"Starting clause extraction for document {document_id}")
    try:
        # 1. Chunking
        chunks = get_document_chunks(text)
        logger.info(f"Generated {len(chunks)} chunks.")
        
        extracted_clauses = []
        api_key = settings.OPENAI_API_KEY if hasattr(settings, "OPENAI_API_KEY") else None
        
        # 2. Extraction
        for chunk in chunks:
            clauses = extract_clauses(chunk, openai_api_key=api_key)
            extracted_clauses.extend(clauses)
            
        # 3. Save to DB
        # In a real app we might deduplicate first
        for clause_data in extracted_clauses:
            clause_model = ClauseModel(
                id=str(uuid.uuid4()),
                document_id=document_id,
                type=clause_data["type"],
                source_text=clause_data["source_text"],
                citation=clause_data.get("citation", {}),
                confidence_score=clause_data["confidence_score"],
                explanation=clause_data.get("explanation")
            )
            db.add(clause_model)
        
        db.commit()
        logger.info(f"Saved {len(extracted_clauses)} clauses for document {document_id}")
    except Exception as e:
        logger.error(f"Error extracting clauses for document {document_id}: {e}")
        db.rollback()
