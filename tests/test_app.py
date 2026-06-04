"""
Test suite for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestRootEndpoint:
    """Tests for GET /"""
    
    def test_root_redirects_to_static(self):
        """Root endpoint should redirect to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities"""
    
    def test_get_all_activities(self):
        """Should return all activities with correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_expected_activities(self):
        """Should contain the expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Club",
            "Basketball Team",
            "Art Workshop",
            "Drama Club",
            "Science Club",
            "Debate Team"
        ]
        
        for activity in expected_activities:
            assert activity in data


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""
    
    def test_successful_signup(self):
        """Should successfully sign up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "neustudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "neustudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert "neustudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_already_registered(self):
        """Should reject signup if student already signed up"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Should reject signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister"""
    
    def test_successful_unregister(self):
        """Should successfully unregister a participant"""
        # First signup
        client.post(
            "/activities/Soccer Club/signup",
            params={"email": "testunregister@mergington.edu"}
        )
        
        # Then unregister
        response = client.post(
            "/activities/Soccer Club/unregister",
            params={"email": "testunregister@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert "testunregister@mergington.edu" not in activities["Soccer Club"]["participants"]
    
    def test_unregister_not_signed_up(self):
        """Should reject unregister if student is not signed up"""
        response = client.post(
            "/activities/Basketball Team/unregister",
            params={"email": "neverregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self):
        """Should reject unregister for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_existing_participant(self):
        """Should successfully unregister an existing participant"""
        # liam@mergington.edu is already in Soccer Club
        response = client.post(
            "/activities/Soccer Club/unregister",
            params={"email": "liam@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify removal
        activities = client.get("/activities").json()
        assert "liam@mergington.edu" not in activities["Soccer Club"]["participants"]
