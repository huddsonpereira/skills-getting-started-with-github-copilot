"""
FastAPI Backend Tests - Mergington High School API

Tests for activity management endpoints using AAA (Arrange-Act-Assert) pattern.
Uses deepcopy to reset activities state between tests to avoid side effects.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store original activities state for reset between tests
ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """
    Arrange: Reset activities to clean state before each test.
    Ensures no test pollution from previous tests.
    """
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    # Cleanup after test
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide FastAPI TestClient for HTTP requests."""
    return TestClient(app)


# =============================================================================
# TESTS
# =============================================================================

def test_get_activities_returns_all(client):
    """
    Test: GET /activities returns all activities.

    Arrange: Client fixture ready.
    Act: Send GET request to /activities endpoint.
    Assert: Status 200 + response contains all activities.
    """
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert len(data) == 9


def test_signup_adds_participant(client):
    """
    Test: POST /activities/{activity_name}/signup adds participant.

    Arrange: Prepare new student email.
    Act: Send POST signup request.
    Assert: Status 200 + participant added to activities list.
    """
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    """
    Test: Duplicate signup returns 400 error.

    Arrange: Use already-registered participant email.
    Act: Send POST signup request for duplicate.
    Assert: Status 400 + "Student already signed up" error detail.
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_delete_participant_removes(client):
    """
    Test: DELETE /activities/{activity_name}/participants removes participant.

    Arrange: Confirm participant exists.
    Act: Send DELETE request.
    Assert: Status 200 + participant removed from activities list.
    """
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_404(client):
    """
    Test: DELETE nonexistent participant returns 404 error.

    Arrange: Use email not in participants list.
    Act: Send DELETE request for nonexistent email.
    Assert: Status 404 + "Participant not found" error detail.
    """
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_nonexistent_activity_returns_404(client):
    """
    Test: Signup to nonexistent activity returns 404 error.

    Arrange: Use activity name that doesn't exist.
    Act: Send POST signup request to fake activity.
    Assert: Status 404 + "Activity not found" error detail.
    """
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
