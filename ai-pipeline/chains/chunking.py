from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_document_chunks(text: str) -> list[str]:
    """
    Splits the legal document into semantic chunks for clause extraction.
    We use a recursive character splitter prioritizing paragraphs and sections.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)
    return chunks
