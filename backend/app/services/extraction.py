import io
from pypdf import PdfReader
from docx import Document as DocxDocument

class ExtractionError(Exception):
    pass

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extracts text from PDF, DOCX, or TXT based on extension."""
    ext = filename.split(".")[-1].lower()
    
    try:
        if ext == "txt":
            return file_bytes.decode('utf-8', errors='replace')
        elif ext == "pdf":
            reader = PdfReader(io.BytesIO(file_bytes))
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
        elif ext == "docx":
            doc = DocxDocument(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            raise ExtractionError(f"Unsupported extraction format for {ext}")
    except Exception as e:
        raise ExtractionError(f"Failed to extract text: {e}")
