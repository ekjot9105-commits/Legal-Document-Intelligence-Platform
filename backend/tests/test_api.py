from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def client(tmp_path: Path) -> TestClient:
    settings = Settings(storage_root=tmp_path / "storage", database_path=tmp_path / "db.sqlite3")
    return TestClient(create_app(settings))


def upload_text(api: TestClient, name: str, text: str, user: str = "user-a") -> dict:
    response = api.post("/api/documents", headers={"X-User-Id": user}, files={"file": (name, text.encode(), "text/plain")})
    assert response.status_code == 201, response.text
    return response.json()


def test_upload_redacts_pii_extracts_clauses_and_scopes_access(tmp_path: Path) -> None:
    api = client(tmp_path)
    document = upload_text(api, "lease.txt", "Tenant shall pay rent. Contact alice@example.com. Give 60 days notice to terminate.")
    assert document["classification"] == "Lease agreement"
    assert document["redaction_count"] == 1

    clauses = api.get(f"/api/documents/{document['id']}/clauses", headers={"X-User-Id": "user-a"})
    assert clauses.status_code == 200
    assert any(clause["type"] == "Termination" for clause in clauses.json())
    assert "alice@example.com" not in clauses.text

    forbidden = api.get(f"/api/documents/{document['id']}/clauses", headers={"X-User-Id": "user-b"})
    assert forbidden.status_code == 404


def test_unsupported_question_is_not_invented(tmp_path: Path) -> None:
    api = client(tmp_path)
    document = upload_text(api, "agreement.txt", "The tenant shall provide 60 days notice to terminate.")
    response = api.post("/api/qa", headers={"X-User-Id": "user-a"}, json={"document_ids": [document["id"]], "question": "What are my tax obligations?"})
    assert response.status_code == 200
    assert response.json()["groundedness"] == "unsupported"
    assert response.json()["cited_clause_ids"] == []


def test_secure_delete_removes_document_and_derived_access(tmp_path: Path) -> None:
    api = client(tmp_path)
    document = upload_text(api, "agreement.txt", "The parties agree to confidentiality.")
    deleted = api.delete(f"/api/documents/{document['id']}", headers={"X-User-Id": "user-a"})
    assert deleted.status_code == 204
    assert api.get("/api/documents", headers={"X-User-Id": "user-a"}).json() == []
    assert api.get(f"/api/documents/{document['id']}/clauses", headers={"X-User-Id": "user-a"}).status_code == 404


def test_disguised_pdf_is_rejected(tmp_path: Path) -> None:
    api = client(tmp_path)
    response = api.post("/api/documents", headers={"X-User-Id": "user-a"}, files={"file": ("bad.pdf", b"not a pdf", "application/pdf")})
    assert response.status_code == 415
