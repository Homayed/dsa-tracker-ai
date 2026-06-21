def create_problem(authenticated_client):
    problem_data = {
        "title": "Two Sum",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Hash Map",
        "status": "Solved",
        "confidence_level": 4,
    }

    response = authenticated_client.post("/problems/", json=problem_data)

    return response.json()["id"]


def test_create_mistake(authenticated_client):
    problem_id = create_problem(authenticated_client)

    mistake_data = {
        "mistake_category": "Logic",
        "description": "I inserted the current number before checking the complement.",
        "lesson_learned": "Check complement first, then insert current number.",
    }

    response = authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json=mistake_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mistake_category"] == mistake_data["mistake_category"]
    assert data["description"] == mistake_data["description"]
    assert data["lesson_learned"] == mistake_data["lesson_learned"]
    assert data["problem_id"] == problem_id
    assert data["user_id"] == 1
    assert "id" in data


def test_get_mistakes(authenticated_client):
    problem_id = create_problem(authenticated_client)

    mistake_data = {
        "mistake_category": "Logic",
        "description": "Forgot complement lookup order.",
        "lesson_learned": "Lookup before insert.",
    }

    authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json=mistake_data,
    )

    response = authenticated_client.get(f"/problems/{problem_id}/mistakes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["description"] == mistake_data["description"]


def test_update_mistake(authenticated_client):
    problem_id = create_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic",
            "description": "Old mistake",
            "lesson_learned": "Old lesson",
        },
    )

    mistake_id = create_response.json()["id"]

    response = authenticated_client.put(
        f"/mistakes/{mistake_id}",
        json={
            "mistake_category": "Implementation",
            "description": "Updated mistake",
            "lesson_learned": "Updated lesson",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["mistake_category"] == "Implementation"
    assert data["description"] == "Updated mistake"
    assert data["lesson_learned"] == "Updated lesson"


def test_delete_mistake(authenticated_client):
    problem_id = create_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic",
            "description": "Temporary mistake",
            "lesson_learned": "Temporary lesson",
        },
    )

    mistake_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/mistakes/{mistake_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Mistake deleted successfully"

    get_response = authenticated_client.get(f"/problems/{problem_id}/mistakes")

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_create_mistake_for_missing_problem_fails(authenticated_client):
    response = authenticated_client.post(
        "/problems/999/mistakes",
        json={
            "mistake_category": "Logic",
            "description": "This should fail",
            "lesson_learned": "No lesson",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"