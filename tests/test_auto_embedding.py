def test_create_problem_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_problem_embedding(db, problem, user_id):
        calls.append(
            {
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.problems.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.problems.upsert_problem_embedding", fake_upsert_problem_embedding)

    response = authenticated_client.post(
        "/problems/",
        json={
            "title": "Valid Anagram",
            "platform": "LeetCode",
            "difficulty": "Easy",
            "pattern": "Hash Map",
            "status": "Solved",
            "confidence_level": 4,
            "time_taken_minutes": 15,
            "solution_code": "class Solution: pass",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "solved_at": "2026-06-21T19:18:49.524Z",
        },
    )

    assert response.status_code in [200, 201]
    assert len(calls) == 1
    assert calls[0]["problem_id"] == response.json()["id"]


def test_update_problem_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_problem_embedding(db, problem, user_id):
        calls.append(
            {
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.problems.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.problems.upsert_problem_embedding", fake_upsert_problem_embedding)

    create_response = authenticated_client.post(
        "/problems/",
        json={
            "title": "Contains Duplicate",
            "platform": "LeetCode",
            "difficulty": "Easy",
            "pattern": "Hash Set",
            "status": "Solved",
            "confidence_level": 4,
            "time_taken_minutes": 10,
            "solution_code": "class Solution: pass",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "solved_at": "2026-06-21T19:18:49.524Z",
        },
    )

    assert create_response.status_code in [200, 201]
    problem_id = create_response.json()["id"]

    calls.clear()

    update_response = authenticated_client.put(
        f"/problems/{problem_id}",
        json={
            "title": "Contains Duplicate",
            "platform": "LeetCode",
            "difficulty": "Easy",
            "pattern": "Hash Set",
            "status": "Review Again",
            "confidence_level": 3,
            "time_taken_minutes": 12,
            "solution_code": "class Solution: pass",
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "solved_at": "2026-06-21T19:18:49.524Z",
        },
    )

    assert update_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["problem_id"] == problem_id