"""
Unit tests for summarize health and version endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz():
    """Test healthz endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "version" in data


def test_version():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["service"] == "summarize"
