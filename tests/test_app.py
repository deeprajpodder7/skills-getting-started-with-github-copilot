import pytest
from fastapi.testclient import TestClient
from src.app import app


def test_get_activities():
    """Test that activities can be retrieved"""
    client = TestClient(app)
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Basketball" in activities
    assert "Tennis Club" in activities
    assert len(activities) > 0


def test_activity_has_required_fields():
    """Test that each activity has required fields"""
    client = TestClient(app)
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity():
    """Test signing up a student for an activity"""
    client = TestClient(app)
    email = "test.student@mergington.edu"
    activity = "Basketball"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]


def test_signup_twice_fails():
    """Test that signing up twice for the same activity fails"""
    client = TestClient(app)
    email = "duplicate.student@mergington.edu"
    activity = "Tennis Club"
    
    # First signup should succeed
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_for_nonexistent_activity():
    """Test that signing up for a nonexistent activity fails"""
    client = TestClient(app)
    email = "test.student@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_unregister_from_activity():
    """Test unregistering a student from an activity"""
    client = TestClient(app)
    email = "unregister.student@mergington.edu"
    activity = "Art Studio"
    
    # First, sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Then, unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert unregister_response.status_code == 200
    data = unregister_response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify the student was removed by trying to unregister again
    unregister_again = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_again.status_code == 400


def test_unregister_nonexistent_student():
    """Test that unregistering a student who isn't signed up fails"""
    client = TestClient(app)
    email = "not.signed.up@mergington.edu"
    activity = "Programming Class"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_from_nonexistent_activity():
    """Test that unregistering from a nonexistent activity fails"""
    client = TestClient(app)
    email = "test.student@mergington.edu"
    activity = "Nonexistent Activity"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]
