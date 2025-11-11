"""
End-to-end test for the orchestrator pipeline
"""
import asyncio
import threading
import time
import sys
import os
import uvicorn
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from orchestrator.main import app


# Service instances for testing
ingestor_app = None
summarize_app = None
viz_app = None


def run_service(app_instance, port):
    """Run a service in a thread"""
    config = uvicorn.Config(app_instance, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    asyncio.run(server.serve())


@pytest.fixture(scope="module", autouse=True)
def setup_services():
    """Start all services in background threads"""
    global ingestor_app, summarize_app, viz_app
    
    try:
        # Import service apps
        import importlib.util
        
        # Load ingestor
        ingestor_path = os.path.join(os.path.dirname(__file__), '../../ingestor/main.py')
        spec = importlib.util.spec_from_file_location("ingestor.main", ingestor_path)
        ingestor_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ingestor_module)
        ingestor_app = ingestor_module.app
        
        # Load summarize
        summarize_path = os.path.join(os.path.dirname(__file__), '../../summarize/main.py')
        spec = importlib.util.spec_from_file_location("summarize.main", summarize_path)
        summarize_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(summarize_module)
        summarize_app = summarize_module.app
        
        # Load viz
        viz_path = os.path.join(os.path.dirname(__file__), '../../viz/main.py')
        spec = importlib.util.spec_from_file_location("viz.main", viz_path)
        viz_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(viz_module)
        viz_app = viz_module.app
        
        # Start services in threads
        threads = [
            threading.Thread(target=run_service, args=(ingestor_app, 8081), daemon=True),
            threading.Thread(target=run_service, args=(summarize_app, 8082), daemon=True),
            threading.Thread(target=run_service, args=(viz_app, 8083), daemon=True),
        ]
        
        for thread in threads:
            thread.start()
        
        # Wait for services to start
        time.sleep(3)
        
    except Exception as e:
        pytest.skip(f"Could not start services: {e}")
    
    yield
    
    # Cleanup (threads are daemon, will exit with main process)


@pytest.mark.asyncio
async def test_e2e_job_flow():
    """Test complete job flow: create -> poll -> complete"""
    # Use TestClient for sync operations, AsyncClient for async
    client = TestClient(app)
    
    # Create a job
    response = client.post(
        "/jobs",
        json={
            "sources": [
                {"type": "url", "value": "https://example.com"},
                {"type": "text", "value": "This is a test document about AI and machine learning."}
            ],
            "goal": "Summarize the key points"
        }
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    assert job_id is not None
    
    # Poll until job is done (with timeout)
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        
        job = response.json()
        status = job.get("status")
        
        if status == "done":
            # Verify result structure
            result = job.get("result")
            assert result is not None
            assert "tldr" in result
            assert "clusters" in result
            assert "assets" in result
            break
        elif status == "error":
            pytest.fail(f"Job failed with error: {job.get('error')}")
        
        attempt += 1
        time.sleep(1)
    
    assert attempt < max_attempts, "Job did not complete within timeout"


def test_healthz():
    """Test healthz endpoint"""
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "version" in data


def test_version():
    """Test version endpoint"""
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["service"] == "orchestrator"


def test_create_job_validation():
    """Test job creation with validation"""
    client = TestClient(app)
    
    # Test empty sources
    response = client.post("/jobs", json={"sources": [], "goal": "test"})
    assert response.status_code == 422
    
    # Test too many sources
    sources = [{"type": "url", "value": f"https://example.com/{i}"} for i in range(21)]
    response = client.post("/jobs", json={"sources": sources, "goal": "test"})
    assert response.status_code in [400, 422]  # Could be either validation or business logic
    
    # Test valid job
    response = client.post(
        "/jobs",
        json={
            "sources": [{"type": "url", "value": "https://example.com"}],
            "goal": "test goal"
        }
    )
    assert response.status_code == 200
    assert "job_id" in response.json()

