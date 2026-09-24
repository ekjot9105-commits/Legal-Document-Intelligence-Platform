import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from .schemas import Citation, ClauseOut, ComparisonChange
from .security import isolate_document_content


@dataclass(frozen=True)
class ExtractedClause:
    type: str
    title: str
    source_text: str
    simplified_text: str
    citation: Citation
    confidence_score: float
    risk_level: str
    reason: str


TAXONOMY: tuple[tuple[str, str, str, str], ...] = (
    ("Termination", "termination|terminate|notice", "Termination terms", "Check notice timing before ending the agreement."),
    ("Renewal", "renew|auto-renew|successive term", "Renewal terms", "Review the renewal window and notice requirement."),
    ("Payment", "payment|invoice|fee|rent|interest", "Payment terms", "Confirm amounts, timing, and consequences of late payment."),
    ("Penalty", "penalty|liquidated damages|late charge", "Penalty term", "Review the trigger and amount of this financial consequence."),
    ("Obligation", "shall|must|required|responsible", "Party obligation", "Confirm who must act and by when."),
    ("Right", "may|entitled|right to", "Party right", "Confirm when and how this right can be exercised."),
    ("Confidentiality", "confidential|non-public|disclos", "Confidentiality", "Review what information is protected and the exceptions."),
    ("Liability", "liable|liability|indirect|consequential", "Liability", "Review exclusions, caps, and carve-outs."),
    ("Intellectual property", "intellectual property|work product|copyright|invention", "IP ownership", "Confirm who owns work product and retained rights."),
    ("Non-compete", "non-compete|noncompete|non-solicit|non solicitation", "Restriction", "Review scope, duration, and jurisdiction with a professional."),
    ("Dispute resolution", "arbitration|mediation|dispute|venue", "Dispute process", "Confirm the required dispute process and venue."),
    ("Governing law", "governing law|laws of|jurisdiction", "Governing law", "Confirm which law and courts are named."),
    ("Deadline", r"deadline|within \d+ days|before|after|date", "Important date", "Add this timing requirement to an obligation calendar."),
)


def _citation(block: str) -> Citation:
    page_match = re.search(r"\[PAGE (\d+)\]", block)
    paragraph_match = re.search(r"\[PARAGRAPH (\d+)\]", block)
    return Citation(page=int(page_match.group(1)) if page_match else None, paragraph=int(paragraph_match.group(1)) if paragraph_match else None)


def extract_clauses(document_id: str, text: str) -> list[ClauseOut]:
    """Extract a deterministic baseline taxonomy; a provider can replace this behind the same contract."""
    safe_text = isolate_document_content(text)
    blocks = [block.strip() for block in re.split(r"\n\s*\n", safe_text) if block.strip()]
    clauses: list[ClauseOut] = []
    seen_types: set[str] = set()
    for block in blocks:
        body = re.sub(r"\[(?:PAGE|PARAGRAPH) \d+\]\s*", "", block).strip()
        lowered = body.lower()
        for clause_type, keywords, title, reason in TAXONOMY:
            if clause_type in seen_types or not re.search(keywords, lowered):
                continue
            risk = "high" if clause_type in {"Penalty", "Liability", "Non-compete"} else "medium" if clause_type in {"Termination", "Renewal", "Payment"} else "low"
            clauses.append(ClauseOut(id=f"{document_id}-clause-{len(clauses) + 1}", document_id=document_id, type=clause_type, title=title, source_text=body[:4000], simplified_text=_simplify(body, clause_type), citation=_citation(block), confidence_score=0.82, risk_level=risk, reason=reason))
            seen_types.add(clause_type)
            break
    return clauses


def _simplify(text: str, clause_type: str) -> str:
    """Produce a transparent baseline explanation when no LLM provider is configured."""
    if clause_type == "Termination" and (match := re.search(r"(\d+)\s+days", text, re.IGNORECASE)):
        return f"You may need to give {match.group(1)} days' written notice before ending the agreement."
    return f"This section covers {clause_type.lower()} terms. Read the source clause and discuss its effect with a professional."


def compare_clauses(document_a_id: str, clauses_a: list[ClauseOut], document_b_id: str, clauses_b: list[ClauseOut]) -> list[ComparisonChange]:
    """Align clauses by taxonomy type and report meaningful text changes."""
    by_type_a = {clause.type: clause for clause in clauses_a}
    by_type_b = {clause.type: clause for clause in clauses_b}
    changes: list[ComparisonChange] = []
    for clause_type in sorted(by_type_a.keys() | by_type_b.keys()):
        first = by_type_a.get(clause_type)
        second = by_type_b.get(clause_type)
        if not first:
            changes.append(ComparisonChange(clause_type=clause_type, change_type="added", after=second.simplified_text, significance="Review new clause"))
        elif not second:
            changes.append(ComparisonChange(clause_type=clause_type, change_type="removed", before=first.simplified_text, significance="Review removed clause"))
        elif SequenceMatcher(None, first.source_text, second.source_text).ratio() < 0.9:
            changes.append(ComparisonChange(clause_type=clause_type, change_type="modified", before=first.simplified_text, after=second.simplified_text, significance="Potentially important change"))
    return changes
