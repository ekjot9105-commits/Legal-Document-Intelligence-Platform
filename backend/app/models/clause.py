from sqlalchemy import Column, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class ClauseModel(Base):
    __tablename__ = "clauses"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    type = Column(String, index=True)
    source_text = Column(String)
    citation = Column(JSON) # Stores page, section, paragraph
    confidence_score = Column(Float)
    explanation = Column(String, nullable=True)

    # Assuming DocumentModel has a relationship back to 'clauses'
    document = relationship("DocumentModel", back_populates="clauses")
