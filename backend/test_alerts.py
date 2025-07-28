import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

from app.main import app
from app.database import get_db, Base
from app.models.alert import Alert  # Import the model to ensure it's registered


def test_create_alert():
    """Test creating a new alert via POST /api/alerts/"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    # Test creating a valid alert
    alert_data = {
        "symbol": "AAPL",
        "alert_type": "price",
        "condition": "above",
        "threshold_value": 150.0,
        "message": "AAPL price above $150",
        "is_active": True
    }
    
    response = client.post("/api/alerts/", json=alert_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["alert_type"] == "price"
    assert data["condition"] == "above"
    assert data["threshold_value"] == 150.0
    assert data["message"] == "AAPL price above $150"
    assert data["is_active"] == True
    assert "id" in data
    assert "created_at" in data
    
    # Test validation errors
    invalid_alert = {
        "symbol": "",  # Too short
        "alert_type": "price"
        # Missing required field 'condition'
    }
    
    response = client.post("/api/alerts/", json=invalid_alert)
    assert response.status_code == 422
    
    # Clean up
    app.dependency_overrides.clear()


def test_get_alerts():
    """Test retrieving alerts via GET /api/alerts/"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    # Create test alerts
    alert1 = {
        "symbol": "AAPL",
        "alert_type": "price",
        "condition": "above",
        "threshold_value": 150.0,
        "message": "AAPL alert"
    }
    
    alert2 = {
        "symbol": "TSLA",
        "alert_type": "volume",
        "condition": "below",
        "threshold_value": 1000000.0,
        "message": "TSLA alert"
    }
    
    # Create alerts
    client.post("/api/alerts/", json=alert1)
    client.post("/api/alerts/", json=alert2)
    
    # Get all alerts
    response = client.get("/api/alerts/")
    assert response.status_code == 200
    
    data = response.json()
    assert "alerts" in data
    assert "total" in data
    assert data["total"] == 2
    assert len(data["alerts"]) == 2
    
    # Test filtering by symbol
    response = client.get("/api/alerts/?symbol=AAPL")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 1
    assert data["alerts"][0]["symbol"] == "AAPL"
    
    # Clean up
    app.dependency_overrides.clear()


def test_health_endpoints():
    """Test health check endpoints"""
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "message" in data
    assert "version" in data
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])