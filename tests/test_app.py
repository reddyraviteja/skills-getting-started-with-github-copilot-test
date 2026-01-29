import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    def test_get_activities(self):
        """Test that we can retrieve activities from the API"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Basketball Team" in activities


class TestSignup:
    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Art%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Signed up" in result["message"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signups are rejected"""
        # First signup
        response1 = client.post(
            "/activities/Art%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200

        # Duplicate signup
        response2 = client.post(
            "/activities/Art%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestUnregister:
    def test_unregister_from_activity(self):
        """Test unregistering from an activity"""
        # First signup
        client.post("/activities/Debate%20Club/signup?email=unreg@mergington.edu")

        # Then unregister
        response = client.delete(
            "/activities/Debate%20Club/unregister?email=unreg@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

    def test_unregister_not_signed_up(self):
        """Test unregistering someone who isn't signed up"""
        response = client.delete(
            "/activities/Drama%20Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestParticipantLimits:
    def test_activity_with_existing_participants(self):
        """Test that activities display existing participants"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) > 0
        assert "michael@mergington.edu" in chess_club["participants"]
