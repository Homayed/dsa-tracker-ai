def test_recommend_study_plan_no_data(authenticated_client):
    response = authenticated_client.post(
        "/ai/recommend-study-plan",
        json={"days": 7},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "No DSA tracker data found yet."
    assert data["recommendation"] == "Add some problems first, then I can recommend a study plan."
    assert data["data_summary"]["problems"] == 0


def test_recommend_study_plan_with_data(authenticated_client, monkeypatch):
    captured = {}

    def fake_generate_study_recommendation(context: str, days: int):
        captured["context"] = context
        captured["days"] = days
        return "Fake 7-day study plan based on saved tracker data."

    monkeypatch.setattr(
        "routers.ai.generate_study_recommendation",
        fake_generate_study_recommendation,
    )

    problem_response = authenticated_client.post(
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

    assert problem_response.status_code in [200, 201]
    problem_id = problem_response.json()["id"]

    authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={
            "content": "I learned to check the complement before inserting the current number."
        },
    )

    authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic Mistake",
            "description": "I inserted current number before checking complement.",
            "lesson_learned": "Check complement first, then insert current number.",
        },
    )

    authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 3,
            "confidence_after": 5,
            "was_solved_again": True,
            "time_taken_minutes": 18,
            "notes": "Reviewed Two Sum and understood hash map order.",
        },
    )

    response = authenticated_client.post(
        "/ai/recommend-study-plan",
        json={"days": 7},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Study recommendation generated successfully"
    assert data["days"] == 7
    assert data["recommendation"] == "Fake 7-day study plan based on saved tracker data."

    assert data["data_summary"]["problems"] == 1
    assert data["data_summary"]["notes"] == 1
    assert data["data_summary"]["mistakes"] == 1
    assert data["data_summary"]["reviews"] == 1

    assert captured["days"] == 7
    assert "Two Sum" in captured["context"]
    assert "Hash Map" in captured["context"]
    assert "Logic Mistake" in captured["context"]
    assert "Check complement first" in captured["context"]