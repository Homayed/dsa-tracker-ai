def create_problem(authenticated_client, title, difficulty, pattern, status, confidence_level):
    problem_data = {
        "title": title,
        "platform": "LeetCode",
        "difficulty": difficulty,
        "pattern": pattern,
        "status": status,
        "confidence_level": confidence_level,
    }

    response = authenticated_client.post("/problems/", json=problem_data)

    return response.json()["id"]


def test_dashboard_summary(authenticated_client):
    problem_id = create_problem(
        authenticated_client,
        title="Two Sum",
        difficulty="Easy",
        pattern="Hash Map",
        status="Review Again",
        confidence_level=2,
    )

    authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={"content": "Use hash map complement lookup."},
    )

    authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic",
            "description": "Forgot to check complement first.",
            "lesson_learned": "Check complement before insert.",
        },
    )

    authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 2,
            "confidence_after": 4,
            "was_solved_again": True,
            "time_taken_minutes": 15,
            "notes": "Improved after review.",
        },
    )

    response = authenticated_client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_problems"] == 1
    assert data["easy_count"] == 1
    assert data["medium_count"] == 0
    assert data["hard_count"] == 0
    assert data["review_again_count"] == 1
    assert data["struggling_count"] == 0
    assert data["average_confidence"] == 2.0
    assert data["total_notes"] == 1
    assert data["total_mistakes"] == 1
    assert data["total_reviews"] == 1


def test_weak_patterns(authenticated_client):
    problem_id = create_problem(
        authenticated_client,
        title="Two Sum",
        difficulty="Easy",
        pattern="Hash Map",
        status="Review Again",
        confidence_level=2,
    )

    authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic",
            "description": "Forgot complement lookup.",
            "lesson_learned": "Check complement first.",
        },
    )

    response = authenticated_client.get("/progress/weak-patterns")

    assert response.status_code == 200

    data = response.json()

    assert len(data["weak_patterns"]) == 1

    weak_pattern = data["weak_patterns"][0]

    assert weak_pattern["pattern"] == "Hash Map"
    assert weak_pattern["problem_count"] == 1
    assert weak_pattern["average_confidence"] == 2.0
    assert weak_pattern["low_confidence_count"] == 1
    assert weak_pattern["review_again_count"] == 1
    assert weak_pattern["mistake_count"] == 1
    assert "Has low-confidence problems" in weak_pattern["reasons"]


def test_review_needed(authenticated_client):
    create_problem(
        authenticated_client,
        title="Move Zeroes",
        difficulty="Easy",
        pattern="Two Pointers",
        status="Struggling",
        confidence_level=2,
    )

    response = authenticated_client.get("/progress/review-needed")

    assert response.status_code == 200

    data = response.json()

    assert len(data["review_needed"]) == 1

    problem = data["review_needed"][0]

    assert problem["title"] == "Move Zeroes"
    assert problem["pattern"] == "Two Pointers"
    assert problem["status"] == "Struggling"
    assert problem["confidence_level"] == 2
    assert "Low confidence level" in problem["reasons"]
    assert "Marked as Struggling" in problem["reasons"]