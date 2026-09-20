from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_activity_catalog():
    # Arrange
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Club",
        "Track and Field",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert set(response.json().keys()) == expected_activity_names


def test_signup_for_activity_registers_student():
    # Arrange
    activity_name = "Basketball Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activity = client.get("/activities").json()[activity_name]
    assert email in activity["participants"]


def test_signup_for_activity_rejects_duplicate_registration():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    # Act
    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    second_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email_and_rejects_missing_registration():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    second_unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == (
        f"Unregistered {email} from {activity_name}"
    )

    activity = client.get("/activities").json()[activity_name]
    assert email not in activity["participants"]

    assert second_unregister_response.status_code == 404
    assert second_unregister_response.json()["detail"] == (
        "Student is not signed up for this activity"
    )


def test_unregister_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Missing Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
