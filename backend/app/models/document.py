import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.schemas.document import DocumentStatus

def get_uuid():
    return str(uuid.uuid4())

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=get_uuid)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.uploading, nullable=False)
    owner_id = Column(String, nullable=False)
    classification = Column(String, nullable=True)
    storage_path = Column(String, nullable=True)
    # Storing PII redactions as a JSON string or text for now to maintain SQLite compatibility easily
    pii_redactions = Column(Text, nullable=True) 
    
    clauses = relationship("ClauseModel", back_populates="document", cascade="all, delete-orphan")
