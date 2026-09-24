import sqlite3
from datetime import datetime
from pathlib import Path

from .schemas import ClauseOut, Citation, DocumentOut, DocumentStatus


class Repository:
    """Persist document metadata and derived analysis with owner-scoped queries."""

    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY, filename TEXT NOT NULL, owner_id TEXT NOT NULL,
                    uploaded_at TEXT NOT NULL, status TEXT NOT NULL, classification TEXT,
                    pages INTEGER NOT NULL DEFAULT 0, redaction_count INTEGER NOT NULL DEFAULT 0,
                    storage_path TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS clauses (
                    id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    payload TEXT NOT NULL
                );
            """)

    def create_document(self, document: DocumentOut, storage_path: str) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (document.id, document.filename, document.owner_id, document.uploaded_at.isoformat(), document.status.value, document.classification, document.pages, document.redaction_count, storage_path))

    def update_document(self, document_id: str, owner_id: str, **values: object) -> None:
        if not values:
            return
        assignments = ", ".join(f"{key} = ?" for key in values)
        with self._connect() as connection:
            connection.execute(f"UPDATE documents SET {assignments} WHERE id = ? AND owner_id = ?", (*values.values(), document_id, owner_id))

    def get_document(self, document_id: str, owner_id: str) -> DocumentOut | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM documents WHERE id = ? AND owner_id = ?", (document_id, owner_id)).fetchone()
        return self._document(row) if row else None

    def list_documents(self, owner_id: str) -> list[DocumentOut]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM documents WHERE owner_id = ? ORDER BY uploaded_at DESC", (owner_id,)).fetchall()
        return [self._document(row) for row in rows]

    def save_clauses(self, clauses: list[ClauseOut]) -> None:
        with self._connect() as connection:
            connection.executemany("INSERT OR REPLACE INTO clauses VALUES (?, ?, ?)", [(clause.id, clause.document_id, clause.model_dump_json()) for clause in clauses])

    def get_clauses(self, document_id: str, owner_id: str) -> list[ClauseOut]:
        with self._connect() as connection:
            rows = connection.execute("SELECT clauses.payload FROM clauses JOIN documents ON documents.id = clauses.document_id WHERE clauses.document_id = ? AND documents.owner_id = ?", (document_id, owner_id)).fetchall()
        return [ClauseOut.model_validate_json(row[0]) for row in rows]

    def delete_document(self, document_id: str, owner_id: str) -> bool:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.execute("DELETE FROM documents WHERE id = ? AND owner_id = ?", (document_id, owner_id))
        return cursor.rowcount > 0

    @staticmethod
    def _document(row: sqlite3.Row) -> DocumentOut:
        return DocumentOut(id=row["id"], filename=row["filename"], owner_id=row["owner_id"], uploaded_at=datetime.fromisoformat(row["uploaded_at"]), status=DocumentStatus(row["status"]), classification=row["classification"], pages=row["pages"], redaction_count=row["redaction_count"])
