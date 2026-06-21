def create_problem(authenticated_client):
    problem_data = {
        "title": "Move Zeroes",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Two Pointers",
        "status": "Review Again",
        "confidence_level": 2,
    }

    response = authenticated_client.post("/problems/", json=problem_data)

    return response.json()["id"]


def test_create_review_log(authenticated_client):
    problem_id = create_problem(authenticated_client)

    review_data = {
        "confidence_before": 2,
        "confidence_after": 4,
        "was_solved_again": True,
        "time_taken_minutes": 15,
        "notes": "I understood the two-pointer movement better.",
    }

    response = authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json=review_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["confidence_before"] == review_data["confidence_before"]
    assert data["confidence_after"] == review_data["confidence_after"]
    assert data["was_solved_again"] == review_data["was_solved_again"]
    assert data["time_taken_minutes"] == review_data["time_taken_minutes"]
    assert data["notes"] == review_data["notes"]
    assert data["problem_id"] == problem_id
    assert data["user_id"] == 1
    assert "id" in data


def test_get_review_logs(authenticated_client):
    problem_id = create_problem(authenticated_client)

    review_data = {
        "confidence_before": 2,
        "confidence_after": 4,
        "was_solved_again": True,
        "time_taken_minutes": 15,
        "notes": "Review went well.",
    }

    authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json=review_data,
    )

    response = authenticated_client.get(f"/problems/{problem_id}/reviews")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["confidence_before"] == 2
    assert data[0]["confidence_after"] == 4


def test_update_review_log(authenticated_client):
    problem_id = create_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 1,
            "confidence_after": 2,
            "was_solved_again": False,
            "time_taken_minutes": 30,
            "notes": "Old review",
        },
    )

    review_id = create_response.json()["id"]

    response = authenticated_client.put(
        f"/reviews/{review_id}",
        json={
            "confidence_after": 5,
            "was_solved_again": True,
            "notes": "Updated review",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["confidence_after"] == 5
    assert data["was_solved_again"] is True
    assert data["notes"] == "Updated review"


def test_delete_review_log(authenticated_client):
    problem_id = create_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 2,
            "confidence_after": 3,
            "was_solved_again": True,
            "time_taken_minutes": 20,
            "notes": "Temporary review",
        },
    )

    review_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/reviews/{review_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Review log deleted successfully"

    get_response = authenticated_client.get(f"/problems/{problem_id}/reviews")

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_create_review_for_missing_problem_fails(authenticated_client):
    response = authenticated_client.post(
        "/problems/999/reviews",
        json={
            "confidence_before": 2,
            "confidence_after": 4,
            "was_solved_again": True,
            "time_taken_minutes": 15,
            "notes": "This should fail",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"