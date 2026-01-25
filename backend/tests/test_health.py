"""Test Health Check and Basic Endpoints"""
import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client: TestClient):
        """Test health check returns OK"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "message" in response.json()
    
    def test_root_redirect(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/", follow_redirects=False)
        # Should either redirect or return something
        assert response.status_code in [200, 307, 404]
    
    def test_openapi_json(self, client: TestClient):
        """Test OpenAPI schema available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_docs_available(self, client: TestClient):
        """Test Swagger docs available"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
