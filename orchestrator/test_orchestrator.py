"""
Minimal tests for orchestrator service
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthz():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_create_job():
    """Test job creation"""
    response = client.post(
        "/jobs",
        json={
            "sources": [{"type": "url", "value": "https://example.com"}],
            "goal": "Test goal"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)
    return data["job_id"]


def test_get_job():
    """Test getting job status"""
    # Create a job first
    job_id = test_create_job()
    
    # Poll for job status
    import time
    timeout = 5  # 5 seconds
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check that status is one of the expected values
        assert "status" in data
        assert data["status"] in ["queued", "running", "done", "error"]
        
        # If job is done or error, we're done
        if data["status"] in ["done", "error"]:
            break
        
        # Check progress structure
        if "progress" in data:
            progress = data["progress"]
            assert "ingestor" in progress
            assert "summarize" in progress
            assert "viz" in progress
        
        time.sleep(0.5)
    
    # Final check - job should have a status
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["queued", "running", "done", "error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

