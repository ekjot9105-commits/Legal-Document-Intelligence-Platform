# Lexora backend

FastAPI document-intelligence API with owner-scoped storage and deterministic local analysis contracts.

## Run

```powershell
uv sync --directory backend --group dev
uv run --directory backend uvicorn app.main:app --reload --port 8000
```

The API requires `X-User-Id` on document routes until the production identity provider is connected. Configure storage and database paths through `backend/.env` using `.env.example` as a template.

## Test

```powershell
uv run --directory backend pytest
```

The upload path validates extensions, size, magic bytes, UTF-8 text, PII redaction, and owner-scoped storage. Extracted clauses are source-cited and prompt-injection-like document instructions are treated as untrusted content. The deterministic engine is an adapter boundary for a production LLM provider; provider credentials must be supplied through environment variables and never committed.
