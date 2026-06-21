def create_test_problem(authenticated_client):
    response = authenticated_client.post(
        "/problems/",
        json={
            "title": "Two Sum",
            "platform": "LeetCode",
            "difficulty": "Easy",
            "pattern": "Hash Map",
            "status": "Solved",
            "confidence_level": 4,
            "time_taken_minutes": 20,
            "solution_code": "class Solution: pass",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "solved_at": "2026-06-21T19:18:49.524Z",
        },
    )

    assert response.status_code in [200, 201]
    return response.json()["id"]


def test_embed_problem_creates_embedding(authenticated_client, monkeypatch):
    def fake_create_embedding(text: str):
        return [0.1] * 1536

    monkeypatch.setattr("routers.ai.create_embedding", fake_create_embedding)

    problem_id = create_test_problem(authenticated_client)

    response = authenticated_client.post(f"/ai/problems/{problem_id}/embed")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Problem embedding created successfully"
    assert data["problem_id"] == problem_id
    assert data["vector_dimensions"] == 1536
    assert data["embedding_model"] == "text-embedding-3-small"


def test_embed_problem_not_found_returns_404(authenticated_client, monkeypatch):
    def fake_create_embedding(text: str):
        return [0.1] * 1536

    monkeypatch.setattr("routers.ai.create_embedding", fake_create_embedding)

    response = authenticated_client.post("/ai/problems/999999/embed")

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"