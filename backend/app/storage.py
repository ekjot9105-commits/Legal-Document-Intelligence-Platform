import os
import hashlib
from pathlib import Path

from fastapi import HTTPException, status

from .config import Settings


class SecureStorage:
    """Store document bytes under owner-scoped paths with traversal-resistant names."""

    def __init__(self, settings: Settings) -> None:
        self.root = settings.storage_root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _owner_root(self, owner_id: str) -> Path:
        owner_key = hashlib.sha256(owner_id.encode("utf-8")).hexdigest()
        owner_root = (self.root / owner_key).resolve()
        owner_root.mkdir(parents=True, exist_ok=True)
        return owner_root

    def save(self, owner_id: str, document_id: str, content: bytes) -> Path:
        """Write bytes atomically to a path derived only from server-owned identifiers."""
        target = (self._owner_root(owner_id) / f"{document_id}.bin").resolve()
        if target.parent != self._owner_root(owner_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid storage path")
        temporary = target.with_suffix(".tmp")
        temporary.write_bytes(content)
        os.replace(temporary, target)
        return target

    def read(self, owner_id: str, document_id: str) -> bytes:
        """Read only an owner-scoped document path."""
        target = (self._owner_root(owner_id) / f"{document_id}.bin").resolve()
        if not target.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document content not found")
        return target.read_bytes()

    def delete(self, owner_id: str, document_id: str) -> None:
        """Remove stored bytes; derived records are deleted by the repository transaction."""
        target = (self._owner_root(owner_id) / f"{document_id}.bin").resolve()
        if target.exists():
            target.unlink()
