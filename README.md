# Lexora Legal Document Intelligence Platform

Lexora is a document-grounded legal information workspace. It helps people understand clauses, compare agreements, identify obligations and attention points, ask source-cited questions, and prepare for conversations with qualified legal professionals.

> This tool provides legal information and document assistance, not legal advice.

## Run locally

Frontend:

```powershell
npm install
npm run dev
```

Backend:

```powershell
uv sync --directory backend --group dev
npm run dev:backend
```

The API runs on `http://localhost:8000`. Document routes require an `X-User-Id` header until a production identity provider is connected.

## Validate

```powershell
npm run build
npm run lint
npm run test
npm run test:backend
```

## Architecture

- `src/`: React workspace with document library, clause intelligence, grounded Q&A, comparison, action planning, trust center, reduced-motion mode, and lazy visual enhancement.
- `backend/app/`: FastAPI API with typed Pydantic contracts, owner-scoped SQLite metadata, hashed storage paths, upload validation, PDF/DOCX/TXT extraction, PII redaction, clause taxonomy, Q&A grounding, comparison, and secure deletion.
- `backend/tests/`: API/security regression tests for ownership isolation, PII redaction, unsupported questions, secure deletion, and disguised-file rejection.

## Security boundary

The backend validates extensions, maximum size, file signatures, and UTF-8 text before persistence. Original and redacted copies are stored separately. Extracted content is treated as untrusted data, instruction-like prompt injection is neutralized before analysis, and every document operation is scoped to the authenticated owner.

The clause engine currently provides a deterministic, auditable local fallback behind stable API contracts. A production LLM adapter can be added at that boundary with credentials supplied through environment variables, bounded prompts, structured output validation, rate limiting, and cost controls. No provider secret is stored in this repository.
