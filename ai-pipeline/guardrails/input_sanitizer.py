import re

def sanitize_document_text(text: str) -> str:
    """
    Sanitizes raw document text to prevent prompt injection.
    Treats all content as data.
    """
    # Remove XML/HTML-like tags that could be used for injection
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Simple heuristic to strip out common prompt injection markers
    injection_markers = [
        "ignore previous instructions",
        "system prompt",
        "you are a",
        "forget all rules",
    ]
    
    for marker in injection_markers:
        # Case insensitive replacement
        pattern = re.compile(re.escape(marker), re.IGNORECASE)
        text = pattern.sub("[REDACTED_INJECTION_ATTEMPT]", text)
        
    return text.strip()
