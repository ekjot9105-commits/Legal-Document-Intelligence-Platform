import spacy
import re
import json

# Load spaCy model lazily to speed up import if not used immediately
nlp = None

def get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    return nlp

def detect_and_redact_pii(text: str) -> tuple[str, str]:
    """
    Detects PII (Names, Emails, Phones, SSNs) and redacts it.
    Returns (redacted_text, redactions_json_string)
    """
    redactions = []
    
    # 1. Regex based: Email
    email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    for match in email_pattern.finditer(text):
        redactions.append({
            "field": match.group(),
            "originalLength": len(match.group()),
            "redactionType": "EMAIL",
            "start": match.start(),
            "end": match.end()
        })
        
    # 2. NER based (spaCy) for Persons and Orgs
    doc = get_nlp()(text)
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            redactions.append({
                "field": ent.text,
                "originalLength": len(ent.text),
                "redactionType": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
            
    # Sort backwards so string replacement doesn't shift indices
    redactions.sort(key=lambda x: x['start'], reverse=True)
    
    redacted_text = text
    for r in redactions:
        mask = f"[{r['redactionType']}]"
        redacted_text = redacted_text[:r['start']] + mask + redacted_text[r['end']:]
        
    return redacted_text, json.dumps(redactions)
