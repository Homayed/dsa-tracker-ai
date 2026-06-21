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


def test_create_note(authenticated_client):
    problem_id = create_problem(authenticated_client)

    note_data = {
        "content": "Use a hash map to store visited numbers."
    }

    response = authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json=note_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == note_data["content"]
    assert data["problem_id"] == problem_id
    assert data["user_id"] == 1
    assert "id" in data


def test_get_notes(authenticated_client):
    problem_id = create_problem(authenticated_client)

    note_data = {
        "content": "Check complement before inserting current number."
    }

    authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json=note_data,
    )

    response = authenticated_client.get(f"/problems/{problem_id}/notes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["content"] == note_data["content"]


def test_update_note(authenticated_client):
    problem_id = create_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={"content": "Old note"},
    )

    note_id = create_response.json()["id"]

    response = authenticated_client.put(
        f"/notes/{note_id}",
        json={"content": "Updated note"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "Updated note"


def test_delete_note(authenticated_client):
    problem_id = create_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={"content": "Temporary note"},
    )

    note_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/notes/{note_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Note deleted successfully"

    get_response = authenticated_client.get(f"/problems/{problem_id}/notes")

    assert get_response.status_code == 200
    assert get_response.json() == []


def test_create_note_for_missing_problem_fails(authenticated_client):
    response = authenticated_client.post(
        "/problems/999/notes",
        json={"content": "This should fail"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"