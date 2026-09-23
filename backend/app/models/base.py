# Import all models here to ensure Base.metadata can discover them
from app.db.session import Base
from app.models.document import DocumentModel
from app.models.clause import ClauseModel
