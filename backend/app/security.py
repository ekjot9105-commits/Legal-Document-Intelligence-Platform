import re
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from .config import Settings

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
PDF_SIGNATURE = b"%PDF"
ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
PROMPT_INJECTION_PATTERNS = re.compile(
    r"(?:ignore|disregard|override)\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?"
    r"|reveal\s+(?:the\s+)?(?:system|developer)\s+prompt",
    re.IGNORECASE,
)


def extension_for(filename: str) -> str:
    """Return a normalized extension without trusting it as a content check."""
    return Path(filename).suffix.lower().removeprefix(".")


async def validate_upload(upload: UploadFile, settings: Settings) -> str:
    """Validate name, size, and magic bytes before persisting an uploaded file."""
    extension = extension_for(upload.filename or "")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type")

    content = await upload.read(settings.max_upload_bytes + 1)
    await upload.seek(0)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    if extension == "pdf" and not content.startswith(PDF_SIGNATURE):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invalid PDF signature")
    if extension == "docx" and not content.startswith(ZIP_SIGNATURES):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invalid DOCX signature")
    if extension == "txt":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="TXT must be UTF-8") from error
    return extension


def isolate_document_content(text: str) -> str:
    """Treat extracted text as untrusted data and neutralize instruction-like content."""
    bounded = text.replace("\x00", "")[:200_000]
    sanitized = PROMPT_INJECTION_PATTERNS.sub("[instruction-like text removed]", bounded)
    return f"<document_content>\n{sanitized}\n</document_content>"
