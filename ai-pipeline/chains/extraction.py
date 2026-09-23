from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Use internal Pydantic models since backend ones are for API
class CitationModel(BaseModel):
    page: Optional[int] = Field(description="Page number if applicable")
    section: Optional[str] = Field(description="Section heading or number")
    paragraph: Optional[int] = Field(description="Paragraph number")

class ExtractedClause(BaseModel):
    type: str = Field(description="The semantic type of the clause, e.g., 'obligation', 'termination', 'liability'.")
    source_text: str = Field(description="The exact text of the clause.")
    citation: CitationModel = Field(description="Citation info for the clause.")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0.")
    explanation: Optional[str] = Field(description="A brief explanation of the clause.")

class ExtractedClausesList(BaseModel):
    clauses: List[ExtractedClause] = Field(description="List of clauses extracted from the text.")

def extract_clauses(chunk: str, openai_api_key: str = None) -> List[dict]:
    """
    Extracts clauses from a chunk of legal text using LLM structured output.
    Returns a list of dictionaries matching the ExtractedClause schema.
    """
    # If no key is provided, we can mock the output for testing without incurring costs,
    # or rely on environment variables (OPENAI_API_KEY).
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
    
    parser = PydanticOutputParser(pydantic_object=ExtractedClausesList)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert legal assistant. Extract distinct legal clauses from the provided text. Identify the type, quote the exact text, extract citation info, give a confidence score, and explain it."),
        ("user", "Extract clauses from this text:\n\n{text}\n\n{format_instructions}")
    ])
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({
            "text": chunk,
            "format_instructions": parser.get_format_instructions()
        })
        return [clause.model_dump() for clause in result.clauses]
    except Exception as e:
        print(f"Extraction failed: {e}")
        return []
