import yaml
import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class Contradiction(BaseModel):
    clause_a_id: str
    clause_b_id: str
    description: str = Field(description="Explanation of why these clauses contradict.")

class ContradictionList(BaseModel):
    contradictions: List[Contradiction]

def get_taxonomy():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'clause_taxonomy.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def detect_missing_clauses(extracted_clauses: List[Dict[str, Any]], document_classification: str) -> List[str]:
    """
    Checks if expected clauses for a document type are missing.
    In a real app, the mapping of document_type -> required_clauses would be in the taxonomy.
    """
    taxonomy = get_taxonomy()
    # Simple mock rule: If Lease Agreement, require 'obligation' and 'termination'
    required = []
    if document_classification == "Lease Agreement":
        required = ["obligation", "termination"]
    elif document_classification == "NDA":
        required = ["confidentiality", "term"]
        
    extracted_types = {c["type"].lower() for c in extracted_clauses}
    missing = [req for req in required if req not in extracted_types]
    return missing

def detect_contradictions(clauses: List[Dict[str, Any]], openai_api_key: str = None) -> List[dict]:
    """
    Detects contradictions between clauses using LLM.
    """
    if len(clauses) < 2:
        return []
        
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
    parser = PydanticOutputParser(pydantic_object=ContradictionList)
    
    clauses_text = "\n".join([f"ID: {c.get('id', 'unknown')} | Type: {c['type']} | Text: {c['source_text']}" for c in clauses])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert legal assistant. Review the following legal clauses and identify any logical contradictions between them. Only report genuine legal contradictions."),
        ("user", "Clauses:\n{clauses_text}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({
            "clauses_text": clauses_text,
            "format_instructions": parser.get_format_instructions()
        })
        return [c.model_dump() for c in result.contradictions]
    except Exception as e:
        print(f"Contradiction detection failed: {e}")
        return []
