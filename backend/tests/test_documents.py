import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine
import io

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_upload_invalid_magic_byte():
    # Create a fake PDF that is actually just a text file missing the %PDF magic byte
    fake_pdf = io.BytesIO(b"Not a real PDF file")
    
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("fake.pdf", fake_pdf, "application/pdf")}
    )
    
    assert response.status_code == 415
    assert "does not match detected content type" in response.json()["detail"]

def test_upload_valid_txt_file():
    valid_txt = io.BytesIO(b"This is a valid text document.")
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", valid_txt, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["filename"] == "test.txt"
    # PII extraction will not find anything here, which is fine

def test_pii_extraction_service():
    from app.services.pii import detect_and_redact_pii
    import json
    
    sample_text = "Contact John Doe at john.doe@example.com."
    redacted, pii_json_str = detect_and_redact_pii(sample_text)
    
    pii_data = json.loads(pii_json_str)
    
    assert "john.doe@example.com" not in redacted
    assert "[EMAIL]" in redacted
    assert any(p["redactionType"] == "EMAIL" for p in pii_data)
