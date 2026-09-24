from dataclasses import dataclass
from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader


@dataclass(frozen=True)
class ExtractedText:
    text: str
    pages: int


def extract_pdf(content: bytes) -> ExtractedText:
    """Extract text page-by-page while preserving page boundaries for citations."""
    reader = PdfReader(BytesIO(content))
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        pages.append(f"[PAGE {page_number}]\n{page_text}")
    return ExtractedText("\n\n".join(pages), len(reader.pages))


def extract_docx(content: bytes) -> ExtractedText:
    """Extract DOCX paragraphs without executing or rendering document content."""
    document = DocxDocument(BytesIO(content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return ExtractedText("\n".join(f"[PARAGRAPH {index}]\n{text}" for index, text in enumerate(paragraphs, start=1)), 1)


def extract_txt(content: bytes) -> ExtractedText:
    """Decode UTF-8 text and retain a single logical page for citations."""
    return ExtractedText(content.decode("utf-8"), 1)


def extract_document(content: bytes, extension: str) -> ExtractedText:
    """Dispatch to a format-specific parser using a validated extension."""
    if extension == "pdf":
        return extract_pdf(content)
    if extension == "docx":
        return extract_docx(content)
    return extract_txt(content)
