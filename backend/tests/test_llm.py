import json

import pytest
from fastapi import HTTPException

from app.config import Settings
from app.llm import LLMService


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"choices": [{"message": {"content": json.dumps({"clauses": [{"type": "Termination", "title": "Notice", "source_text": "Give 60 days notice.", "simplified_text": "Give 60 days notice.", "citation": {"page": 2, "section": "9.2"}, "confidence_score": 0.91, "risk_level": "medium", "reason": "Timing matters."}]})}}]}


class FakeClient:
    async def __aenter__(self) -> "FakeClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, *args: object, **kwargs: object) -> FakeResponse:
        return FakeResponse()


@pytest.mark.asyncio
async def test_configured_provider_returns_validated_structured_clauses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.llm.httpx.AsyncClient", lambda **_: FakeClient())
    settings = Settings(llm_base_url="https://provider.test", llm_api_key="test-key")
    clauses = await LLMService(settings).extract("user-a", "doc-1", "Give 60 days notice.")
    assert clauses[0].type == "Termination"
    assert clauses[0].confidence_score == 0.91


def test_llm_rate_limit_is_enforced() -> None:
    service = LLMService(Settings(llm_requests_per_minute=1))
    service._guard("user-a", "qa")
    try:
        service._guard("user-a", "qa")
    except HTTPException as error:
        assert error.status_code == 429
    else:
        raise AssertionError("Expected the second request to be rate limited")
