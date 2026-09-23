import asyncio

async def classify_document(text: str) -> str:
    """
    Mock classification for Phase 1. 
    In production, this would use LangChain + OpenAI to output a structured classification.
    """
    # Simulate LLM call
    await asyncio.sleep(1)
    
    text_lower = text.lower()
    if "lease" in text_lower or "tenant" in text_lower:
        return "Lease Agreement"
    elif "non-disclosure" in text_lower or "nda" in text_lower or "confidential" in text_lower:
        return "NDA"
    elif "terms of service" in text_lower or "tos" in text_lower:
        return "Terms of Service"
    elif "employment" in text_lower or "employee" in text_lower:
        return "Employment Contract"
    
    return "Other Legal Document"
