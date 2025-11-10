"""
Sanity test for ingestor service
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

