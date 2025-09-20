"""Basic tests for the API"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_user_me_endpoint():
    """Test user endpoint"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
