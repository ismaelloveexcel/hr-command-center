"""Tests for API endpoints."""

import pytest


def test_create_and_retrieve_request(client):
    """Test the full lifecycle of creating and retrieving a request."""
    # Create request
    request_data = {
        "title": "Leave Request",
        "description": "Need 5 days leave for vacation",
        "submitted_by": "john.doe@company.ae"
    }
    
    create_response = client.post("/requests", json=request_data)
    assert create_response.status_code == 201
    
    created_data = create_response.json()
    reference = created_data["reference"]
    
    # Retrieve request (tracking endpoint returns different schema)
    get_response = client.get(f"/requests/{reference}")
    assert get_response.status_code == 200
    
    retrieved_data = get_response.json()
    assert retrieved_data["reference"] == reference
    assert retrieved_data["title"] == "Leave Request"
    assert retrieved_data["current_status"] == "submitted"  # Tracking API uses current_status


def test_update_request_status(client, hr_api_key):
    """Test updating request status with HR API key."""
    # Create request
    request_data = {
        "title": "Certificate Request",
        "description": "Need employment certificate",
        "submitted_by": "jane.smith@company.ae"
    }
    
    create_response = client.post("/requests", json=request_data)
    reference = create_response.json()["reference"]
    
    # Update status
    update_data = {
        "status": "reviewing",
        "public_notes": "Your request is under review"
    }
    
    update_response = client.patch(
        f"/requests/{reference}/status",
        json=update_data,
        headers={"X-HR-API-Key": hr_api_key}
    )
    
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["status"] == "reviewing"
    assert updated_data["public_notes"] == "Your request is under review"


def test_hr_queue_endpoint(client, hr_api_key):
    """Test HR queue endpoint returns all requests."""
    # Create multiple requests
    for i in range(3):
        request_data = {
            "title": f"Request {i}",
            "description": f"Description {i}",
            "submitted_by": f"user{i}@company.ae"
        }
        client.post("/requests", json=request_data)
    
    # Get HR queue
    response = client.get(
        "/hr/requests",
        headers={"X-HR-API-Key": hr_api_key}
    )
    
    assert response.status_code == 200
    requests = response.json()
    assert len(requests) >= 3


def test_hr_stats_endpoint(client, hr_api_key):
    """Test HR stats endpoint returns correct counts."""
    # Create requests with different statuses
    request_data = {
        "title": "Test Request",
        "description": "Test",
        "submitted_by": "test@company.ae"
    }
    client.post("/requests", json=request_data)
    
    # Get stats
    response = client.get(
        "/hr/stats",
        headers={"X-HR-API-Key": hr_api_key}
    )
    
    assert response.status_code == 200
    stats = response.json()
    assert "status_counts" in stats
    assert "total" in stats
    assert stats["total"] > 0


def test_request_not_found(client):
    """Test retrieving non-existent request."""
    response = client.get("/requests/REF-9999-999")
    assert response.status_code == 404


def test_pagination_in_hr_queue(client, hr_api_key):
    """Test pagination parameters in HR queue."""
    # Create some requests
    for i in range(5):
        request_data = {
            "title": f"Request {i}",
            "description": "Test",
            "submitted_by": f"user{i}@company.ae"
        }
        client.post("/requests", json=request_data)
    
    # Test with limit
    response = client.get(
        "/hr/requests?limit=2",
        headers={"X-HR-API-Key": hr_api_key}
    )
    assert response.status_code == 200
    assert len(response.json()) <= 2
    
    # Test with offset
    response = client.get(
        "/hr/requests?limit=2&offset=2",
        headers={"X-HR-API-Key": hr_api_key}
    )
    assert response.status_code == 200


def test_status_filter_in_hr_queue(client, hr_api_key):
    """Test status filtering in HR queue."""
    # Create a request and update its status
    request_data = {
        "title": "Approved Request Filter",
        "description": "Test",
        "submitted_by": "testfilter@company.ae"
    }
    create_response = client.post("/requests", json=request_data)
    assert create_response.status_code == 201
    reference = create_response.json()["reference"]
    
    # Update to approved
    update_data = {"status": "approved"}
    client.patch(
        f"/requests/{reference}/status",
        json=update_data,
        headers={"X-HR-API-Key": hr_api_key}
    )
    
    # Filter by approved status
    response = client.get(
        "/hr/requests?status=approved",
        headers={"X-HR-API-Key": hr_api_key}
    )
    
    assert response.status_code == 200
    requests = response.json()
    # All returned requests should be approved
    for req in requests:
        assert req["status"] == "approved"
