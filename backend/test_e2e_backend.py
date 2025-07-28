"""
E2E Backend Tests for Stock AI Agent SaaS

Comprehensive end-to-end tests that validate the complete backend API functionality
including database operations, validation, error handling, and API workflows.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json
from datetime import datetime
from typing import Dict, Any

# Import after setting up test environment to avoid PostgreSQL connection
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app
from app.database import get_db, Base
from app.models.alert import Alert


class TestE2EBackend:
    """Comprehensive E2E test suite for backend API functionality."""
    
    @pytest.fixture(scope="function")
    def client(self):
        """Create a test client with isolated in-memory database for each test."""
        # Create in-memory SQLite database for testing
        engine = create_engine(
            "sqlite:///:memory:", 
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        # Override the database dependency
        app.dependency_overrides[get_db] = override_get_db
        
        # Create test client
        with TestClient(app) as test_client:
            yield test_client
        
        # Clean up
        app.dependency_overrides.clear()

    @pytest.fixture
    def sample_alert_data(self) -> Dict[str, Any]:
        """Sample alert data for testing."""
        return {
            "symbol": "AAPL",
            "alert_type": "price",
            "condition": "above",
            "threshold_value": 150.0,
            "message": "AAPL price alert above $150",
            "is_active": True
        }

    @pytest.fixture
    def multiple_alerts_data(self) -> list[Dict[str, Any]]:
        """Multiple alert data for testing filtering and pagination."""
        return [
            {
                "symbol": "AAPL",
                "alert_type": "price",
                "condition": "above",
                "threshold_value": 150.0,
                "message": "AAPL price alert",
                "is_active": True
            },
            {
                "symbol": "TSLA",
                "alert_type": "volume",
                "condition": "below",
                "threshold_value": 1000000.0,
                "message": "TSLA volume alert",
                "is_active": True
            },
            {
                "symbol": "GOOGL",
                "alert_type": "price",
                "condition": "below",
                "threshold_value": 120.0,
                "message": "GOOGL price alert",
                "is_active": False
            },
            {
                "symbol": "AAPL",
                "alert_type": "news",
                "condition": "equals",
                "threshold_value": None,
                "message": "AAPL news alert",
                "is_active": True
            }
        ]


class TestHealthEndpoints(TestE2EBackend):
    """Test health check and basic endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct application information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "running"
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_documentation(self, client):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "paths" in openapi_data
        assert "/api/alerts/" in openapi_data["paths"]
        
        # Test Swagger UI accessibility
        response = client.get("/docs")
        assert response.status_code == 200


class TestAlertCreation(TestE2EBackend):
    """Test alert creation scenarios."""
    
    def test_create_valid_alert(self, client, sample_alert_data):
        """Test creating a valid alert with all required fields."""
        response = client.post("/api/alerts/", json=sample_alert_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["symbol"] == sample_alert_data["symbol"]
        assert data["alert_type"] == sample_alert_data["alert_type"]
        assert data["condition"] == sample_alert_data["condition"]
        assert data["threshold_value"] == sample_alert_data["threshold_value"]
        assert data["message"] == sample_alert_data["message"]
        assert data["is_active"] == sample_alert_data["is_active"]
        
        # Check auto-generated fields
        assert "id" in data
        assert isinstance(data["id"], int)
        assert "created_at" in data
        assert datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        
    def test_create_alert_symbol_normalization(self, client, sample_alert_data):
        """Test that stock symbols are normalized to uppercase."""
        sample_alert_data["symbol"] = "aapl"  # lowercase
        
        response = client.post("/api/alerts/", json=sample_alert_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["symbol"] == "AAPL"  # Should be uppercase

    def test_create_alert_optional_fields(self, client):
        """Test creating alert with minimal required fields."""
        minimal_alert = {
            "symbol": "MSFT",
            "alert_type": "news",
            "condition": "equals"
        }
        
        response = client.post("/api/alerts/", json=minimal_alert)
        assert response.status_code == 201
        
        data = response.json()
        assert data["symbol"] == "MSFT"
        assert data["alert_type"] == "news"
        assert data["condition"] == "equals"
        assert data["threshold_value"] is None
        assert data["message"] is None
        assert data["is_active"] is True  # Default value

    def test_create_alert_validation_errors(self, client):
        """Test validation errors for invalid alert data."""
        test_cases = [
            # Missing required fields
            ({}, 422),
            ({"symbol": "AAPL"}, 422),
            ({"symbol": "AAPL", "alert_type": "price"}, 422),
            
            # Invalid field values
            ({"symbol": "", "alert_type": "price", "condition": "above"}, 422),
            ({"symbol": "TOOLONGSYMBOL", "alert_type": "price", "condition": "above"}, 422),
            ({"symbol": "AAPL", "alert_type": "", "condition": "above"}, 422),
            ({"symbol": "AAPL", "alert_type": "price", "condition": ""}, 422),
        ]
        
        for invalid_data, expected_status in test_cases:
            response = client.post("/api/alerts/", json=invalid_data)
            assert response.status_code == expected_status

    def test_create_multiple_alerts(self, client, multiple_alerts_data):
        """Test creating multiple alerts to verify database persistence."""
        created_alerts = []
        
        for alert_data in multiple_alerts_data:
            response = client.post("/api/alerts/", json=alert_data)
            assert response.status_code == 201
            created_alerts.append(response.json())
        
        # Verify all alerts have unique IDs
        ids = [alert["id"] for alert in created_alerts]
        assert len(ids) == len(set(ids))  # All IDs should be unique
        
        # Verify alerts are persisted
        response = client.get("/api/alerts/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == len(multiple_alerts_data)


class TestAlertRetrieval(TestE2EBackend):
    """Test alert retrieval and filtering scenarios."""
    
    def test_get_empty_alerts_list(self, client):
        """Test retrieving alerts when none exist."""
        response = client.get("/api/alerts/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["alerts"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 100

    def test_get_alerts_with_data(self, client, multiple_alerts_data):
        """Test retrieving alerts when data exists."""
        # Create test alerts
        for alert_data in multiple_alerts_data:
            client.post("/api/alerts/", json=alert_data)
        
        response = client.get("/api/alerts/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["alerts"]) == len(multiple_alerts_data)
        assert data["total"] == len(multiple_alerts_data)
        assert data["page"] == 1
        assert data["page_size"] == 100

    def test_get_alert_by_id(self, client, sample_alert_data):
        """Test retrieving a specific alert by ID."""
        # Create an alert
        create_response = client.post("/api/alerts/", json=sample_alert_data)
        created_alert = create_response.json()
        alert_id = created_alert["id"]
        
        # Retrieve the alert
        response = client.get(f"/api/alerts/{alert_id}")
        assert response.status_code == 200
        
        retrieved_alert = response.json()
        assert retrieved_alert["id"] == alert_id
        assert retrieved_alert["symbol"] == sample_alert_data["symbol"]

    def test_get_nonexistent_alert(self, client):
        """Test retrieving an alert that doesn't exist."""
        response = client.get("/api/alerts/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_filter_alerts_by_symbol(self, client, multiple_alerts_data):
        """Test filtering alerts by stock symbol."""
        # Create test alerts
        for alert_data in multiple_alerts_data:
            client.post("/api/alerts/", json=alert_data)
        
        # Filter by AAPL
        response = client.get("/api/alerts/?symbol=AAPL")
        assert response.status_code == 200
        
        data = response.json()
        aapl_alerts = [alert for alert in multiple_alerts_data if alert["symbol"] == "AAPL"]
        assert data["total"] == len(aapl_alerts)
        
        for alert in data["alerts"]:
            assert alert["symbol"] == "AAPL"

    def test_filter_alerts_by_active_status(self, client, multiple_alerts_data):
        """Test filtering alerts by active status."""
        # Create test alerts
        for alert_data in multiple_alerts_data:
            client.post("/api/alerts/", json=alert_data)
        
        # Filter by active status
        response = client.get("/api/alerts/?is_active=true")
        assert response.status_code == 200
        
        data = response.json()
        active_alerts = [alert for alert in multiple_alerts_data if alert["is_active"]]
        assert data["total"] == len(active_alerts)
        
        for alert in data["alerts"]:
            assert alert["is_active"] is True

    def test_pagination(self, client, multiple_alerts_data):
        """Test pagination functionality."""
        # Create test alerts
        for alert_data in multiple_alerts_data:
            client.post("/api/alerts/", json=alert_data)
        
        # Test pagination with limit
        response = client.get("/api/alerts/?limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["alerts"]) == 2
        assert data["total"] == len(multiple_alerts_data)
        assert data["page_size"] == 2
        
        # Test pagination with skip
        response = client.get("/api/alerts/?skip=2&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["alerts"]) <= 2
        assert data["total"] == len(multiple_alerts_data)


class TestAlertUpdate(TestE2EBackend):
    """Test alert update scenarios."""
    
    def test_update_alert_full(self, client, sample_alert_data):
        """Test updating all fields of an alert."""
        # Create an alert
        create_response = client.post("/api/alerts/", json=sample_alert_data)
        alert_id = create_response.json()["id"]
        
        # Update the alert
        update_data = {
            "symbol": "TSLA",
            "alert_type": "volume",
            "condition": "below",
            "threshold_value": 500000.0,
            "message": "Updated TSLA alert",
            "is_active": False
        }
        
        response = client.put(f"/api/alerts/{alert_id}", json=update_data)
        assert response.status_code == 200
        
        updated_alert = response.json()
        assert updated_alert["id"] == alert_id
        assert updated_alert["symbol"] == "TSLA"
        assert updated_alert["alert_type"] == "volume"
        assert updated_alert["condition"] == "below"
        assert updated_alert["threshold_value"] == 500000.0
        assert updated_alert["message"] == "Updated TSLA alert"
        assert updated_alert["is_active"] is False

    def test_update_alert_partial(self, client, sample_alert_data):
        """Test updating only some fields of an alert."""
        # Create an alert
        create_response = client.post("/api/alerts/", json=sample_alert_data)
        created_alert = create_response.json()
        alert_id = created_alert["id"]
        
        # Partial update
        update_data = {
            "threshold_value": 200.0,
            "is_active": False
        }
        
        response = client.put(f"/api/alerts/{alert_id}", json=update_data)
        assert response.status_code == 200
        
        updated_alert = response.json()
        assert updated_alert["id"] == alert_id
        # Updated fields
        assert updated_alert["threshold_value"] == 200.0
        assert updated_alert["is_active"] is False
        # Unchanged fields
        assert updated_alert["symbol"] == created_alert["symbol"]
        assert updated_alert["alert_type"] == created_alert["alert_type"]
        assert updated_alert["condition"] == created_alert["condition"]
        assert updated_alert["message"] == created_alert["message"]

    def test_update_nonexistent_alert(self, client):
        """Test updating an alert that doesn't exist."""
        update_data = {
            "threshold_value": 200.0
        }
        
        response = client.put("/api/alerts/99999", json=update_data)
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_alert_symbol_normalization(self, client, sample_alert_data):
        """Test that symbol is normalized during update."""
        # Create an alert
        create_response = client.post("/api/alerts/", json=sample_alert_data)
        alert_id = create_response.json()["id"]
        
        # Update with lowercase symbol
        update_data = {"symbol": "msft"}
        
        response = client.put(f"/api/alerts/{alert_id}", json=update_data)
        assert response.status_code == 200
        
        updated_alert = response.json()
        assert updated_alert["symbol"] == "MSFT"


class TestAlertDeletion(TestE2EBackend):
    """Test alert deletion scenarios."""
    
    def test_delete_alert(self, client, sample_alert_data):
        """Test deleting an existing alert."""
        # Create an alert
        create_response = client.post("/api/alerts/", json=sample_alert_data)
        alert_id = create_response.json()["id"]
        
        # Delete the alert
        response = client.delete(f"/api/alerts/{alert_id}")
        assert response.status_code == 204
        assert response.content == b""
        
        # Verify alert is deleted
        get_response = client.get(f"/api/alerts/{alert_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_alert(self, client):
        """Test deleting an alert that doesn't exist."""
        response = client.delete("/api/alerts/99999")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_alert_persistence(self, client, multiple_alerts_data):
        """Test that deleting one alert doesn't affect others."""
        # Create multiple alerts
        created_ids = []
        for alert_data in multiple_alerts_data:
            response = client.post("/api/alerts/", json=alert_data)
            created_ids.append(response.json()["id"])
        
        # Delete the first alert
        response = client.delete(f"/api/alerts/{created_ids[0]}")
        assert response.status_code == 204
        
        # Verify other alerts still exist
        for alert_id in created_ids[1:]:
            response = client.get(f"/api/alerts/{alert_id}")
            assert response.status_code == 200
        
        # Verify total count is reduced
        response = client.get("/api/alerts/")
        data = response.json()
        assert data["total"] == len(multiple_alerts_data) - 1


class TestErrorHandling(TestE2EBackend):
    """Test error handling and edge cases."""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request body."""
        response = client.post(
            "/api/alerts/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_large_threshold_values(self, client):
        """Test handling of very large threshold values."""
        alert_data = {
            "symbol": "TEST",
            "alert_type": "price",
            "condition": "above",
            "threshold_value": 999999999999.99,
            "message": "Large threshold test"
        }
        
        response = client.post("/api/alerts/", json=alert_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["threshold_value"] == 999999999999.99

    def test_negative_threshold_values(self, client):
        """Test handling of negative threshold values."""
        alert_data = {
            "symbol": "TEST",
            "alert_type": "price",
            "condition": "above",
            "threshold_value": -100.0,
            "message": "Negative threshold test"
        }
        
        response = client.post("/api/alerts/", json=alert_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["threshold_value"] == -100.0

    def test_special_characters_in_message(self, client):
        """Test handling of special characters in alert message."""
        alert_data = {
            "symbol": "TEST",
            "alert_type": "news",
            "condition": "equals",
            "message": "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>? áéíóú"
        }
        
        response = client.post("/api/alerts/", json=alert_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == alert_data["message"]


class TestCompleteWorkflow(TestE2EBackend):
    """Test complete E2E workflows."""
    
    def test_complete_alert_lifecycle(self, client, sample_alert_data):
        """Test the complete lifecycle of an alert: create, read, update, delete."""
        # Step 1: Create alert
        create_response = client.post("/api/alerts/", json=sample_alert_data)
        assert create_response.status_code == 201
        created_alert = create_response.json()
        alert_id = created_alert["id"]
        
        # Step 2: Read alert
        read_response = client.get(f"/api/alerts/{alert_id}")
        assert read_response.status_code == 200
        read_alert = read_response.json()
        assert read_alert["id"] == alert_id
        
        # Step 3: Update alert
        update_data = {
            "threshold_value": 175.0,
            "message": "Updated alert message"
        }
        update_response = client.put(f"/api/alerts/{alert_id}", json=update_data)
        assert update_response.status_code == 200
        updated_alert = update_response.json()
        assert updated_alert["threshold_value"] == 175.0
        assert updated_alert["message"] == "Updated alert message"
        
        # Step 4: Verify update persisted
        read_updated_response = client.get(f"/api/alerts/{alert_id}")
        assert read_updated_response.status_code == 200
        persisted_alert = read_updated_response.json()
        assert persisted_alert["threshold_value"] == 175.0
        
        # Step 5: Delete alert
        delete_response = client.delete(f"/api/alerts/{alert_id}")
        assert delete_response.status_code == 204
        
        # Step 6: Verify deletion
        final_read_response = client.get(f"/api/alerts/{alert_id}")
        assert final_read_response.status_code == 404

    def test_bulk_operations_workflow(self, client, multiple_alerts_data):
        """Test bulk operations workflow."""
        # Create multiple alerts
        created_ids = []
        for alert_data in multiple_alerts_data:
            response = client.post("/api/alerts/", json=alert_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # Test filtering and pagination
        aapl_response = client.get("/api/alerts/?symbol=AAPL")
        assert aapl_response.status_code == 200
        aapl_data = aapl_response.json()
        aapl_count = len([a for a in multiple_alerts_data if a["symbol"] == "AAPL"])
        assert aapl_data["total"] == aapl_count
        
        # Test active filter
        active_response = client.get("/api/alerts/?is_active=true")
        assert active_response.status_code == 200
        active_data = active_response.json()
        active_count = len([a for a in multiple_alerts_data if a["is_active"]])
        assert active_data["total"] == active_count
        
        # Update multiple alerts
        for alert_id in created_ids[:2]:
            update_response = client.put(
                f"/api/alerts/{alert_id}",
                json={"is_active": False}
            )
            assert update_response.status_code == 200
        
        # Verify updates
        updated_active_response = client.get("/api/alerts/?is_active=true")
        updated_active_data = updated_active_response.json()
        assert updated_active_data["total"] == active_count - 2
        
        # Clean up by deleting all
        for alert_id in created_ids:
            delete_response = client.delete(f"/api/alerts/{alert_id}")
            assert delete_response.status_code == 204
        
        # Verify all deleted
        final_response = client.get("/api/alerts/")
        final_data = final_response.json()
        assert final_data["total"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])