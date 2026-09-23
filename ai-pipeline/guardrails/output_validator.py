from typing import Any, Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def validate_llm_output(output: dict[str, Any], schema_class: Type[T]) -> T:
    """
    Validates that a parsed LLM output matches the expected Pydantic schema.
    Raises ValueError if validation fails.
    """
    try:
        return schema_class.model_validate(output)
    except ValidationError as e:
        raise ValueError(f"LLM output failed validation: {e}")
