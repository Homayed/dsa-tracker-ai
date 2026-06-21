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


def test_create_note_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_note_embedding(db, note, problem, user_id):
        calls.append(
            {
                "note_id": note.id,
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.notes.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.notes.upsert_note_embedding", fake_upsert_note_embedding)

    problem_id = create_test_problem(authenticated_client)

    response = authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={
            "content": "I learned to check the complement before inserting the current number."
        },
    )

    assert response.status_code in [200, 201]
    assert len(calls) == 1
    assert calls[0]["note_id"] == response.json()["id"]
    assert calls[0]["problem_id"] == problem_id


def test_update_note_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_note_embedding(db, note, problem, user_id):
        calls.append(
            {
                "note_id": note.id,
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.notes.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.notes.upsert_note_embedding", fake_upsert_note_embedding)

    problem_id = create_test_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={
            "content": "Initial note."
        },
    )

    assert create_response.status_code in [200, 201]
    note_id = create_response.json()["id"]

    calls.clear()

    update_response = authenticated_client.put(
        f"/notes/{note_id}",
        json={
            "content": "Updated note about checking complement first."
        },
    )

    assert update_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["note_id"] == note_id
    assert calls[0]["problem_id"] == problem_id


def test_delete_note_calls_delete_embedding(authenticated_client, monkeypatch):
    calls = []

    def fake_delete_source_embedding(db, user_id, source_type, source_id):
        calls.append(
            {
                "user_id": user_id,
                "source_type": source_type,
                "source_id": source_id,
            }
        )

    monkeypatch.setattr("routers.notes.delete_source_embedding", fake_delete_source_embedding)

    problem_id = create_test_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/notes",
        json={
            "content": "Note to delete."
        },
    )

    assert create_response.status_code in [200, 201]
    note_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/notes/{note_id}")

    assert delete_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["source_type"] == "note"
    assert calls[0]["source_id"] == note_id


def test_create_mistake_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_mistake_embedding(db, mistake, problem, user_id):
        calls.append(
            {
                "mistake_id": mistake.id,
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.mistakes.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.mistakes.upsert_mistake_embedding", fake_upsert_mistake_embedding)

    problem_id = create_test_problem(authenticated_client)

    response = authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic Mistake",
            "description": "I inserted the current number before checking the complement.",
            "lesson_learned": "Check complement first, then insert current number.",
        },
    )

    assert response.status_code in [200, 201]
    assert len(calls) == 1
    assert calls[0]["mistake_id"] == response.json()["id"]
    assert calls[0]["problem_id"] == problem_id


def test_update_mistake_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_mistake_embedding(db, mistake, problem, user_id):
        calls.append(
            {
                "mistake_id": mistake.id,
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.mistakes.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.mistakes.upsert_mistake_embedding", fake_upsert_mistake_embedding)

    problem_id = create_test_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic Mistake",
            "description": "Initial mistake.",
            "lesson_learned": "Initial lesson.",
        },
    )

    assert create_response.status_code in [200, 201]
    mistake_id = create_response.json()["id"]

    calls.clear()

    update_response = authenticated_client.put(
        f"/mistakes/{mistake_id}",
        json={
            "mistake_category": "Logic Mistake",
            "description": "I inserted current number before checking complement.",
            "lesson_learned": "In one-pass hash map, check complement first.",
        },
    )

    assert update_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["mistake_id"] == mistake_id
    assert calls[0]["problem_id"] == problem_id


def test_delete_mistake_calls_delete_embedding(authenticated_client, monkeypatch):
    calls = []

    def fake_delete_source_embedding(db, user_id, source_type, source_id):
        calls.append(
            {
                "user_id": user_id,
                "source_type": source_type,
                "source_id": source_id,
            }
        )

    monkeypatch.setattr("routers.mistakes.delete_source_embedding", fake_delete_source_embedding)

    problem_id = create_test_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/mistakes",
        json={
            "mistake_category": "Logic Mistake",
            "description": "Mistake to delete.",
            "lesson_learned": "Lesson to delete.",
        },
    )

    assert create_response.status_code in [200, 201]
    mistake_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/mistakes/{mistake_id}")

    assert delete_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["source_type"] == "mistake"
    assert calls[0]["source_id"] == mistake_id


def test_create_review_log_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_review_log_embedding(db, review_log, problem, user_id):
        calls.append(
            {
                "review_log_id": review_log.id,
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.reviews.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.reviews.upsert_review_log_embedding", fake_upsert_review_log_embedding)

    problem_id = create_test_problem(authenticated_client)

    response = authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 3,
            "confidence_after": 5,
            "was_solved_again": True,
            "time_taken_minutes": 18,
            "notes": "Reviewed Two Sum and understood complement lookup order.",
        },
    )

    assert response.status_code in [200, 201]
    assert len(calls) == 1
    assert calls[0]["review_log_id"] == response.json()["id"]
    assert calls[0]["problem_id"] == problem_id


def test_update_review_log_calls_auto_embedding_when_enabled(authenticated_client, monkeypatch):
    calls = []

    def fake_is_auto_embed_enabled():
        return True

    def fake_upsert_review_log_embedding(db, review_log, problem, user_id):
        calls.append(
            {
                "review_log_id": review_log.id,
                "problem_id": problem.id,
                "user_id": user_id,
            }
        )

    monkeypatch.setattr("routers.reviews.is_auto_embed_enabled", fake_is_auto_embed_enabled)
    monkeypatch.setattr("routers.reviews.upsert_review_log_embedding", fake_upsert_review_log_embedding)

    problem_id = create_test_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 2,
            "confidence_after": 3,
            "was_solved_again": False,
            "time_taken_minutes": 25,
            "notes": "Initial review.",
        },
    )

    assert create_response.status_code in [200, 201]
    review_log_id = create_response.json()["id"]

    calls.clear()

    update_response = authenticated_client.put(
        f"/reviews/{review_log_id}",
        json={
            "confidence_before": 3,
            "confidence_after": 5,
            "was_solved_again": True,
            "time_taken_minutes": 18,
            "notes": "Updated review. I solved it again and understood the hash map order.",
        },
    )

    assert update_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["review_log_id"] == review_log_id
    assert calls[0]["problem_id"] == problem_id


def test_delete_review_log_calls_delete_embedding(authenticated_client, monkeypatch):
    calls = []

    def fake_delete_source_embedding(db, user_id, source_type, source_id):
        calls.append(
            {
                "user_id": user_id,
                "source_type": source_type,
                "source_id": source_id,
            }
        )

    monkeypatch.setattr("routers.reviews.delete_source_embedding", fake_delete_source_embedding)

    problem_id = create_test_problem(authenticated_client)

    create_response = authenticated_client.post(
        f"/problems/{problem_id}/reviews",
        json={
            "confidence_before": 3,
            "confidence_after": 4,
            "was_solved_again": True,
            "time_taken_minutes": 20,
            "notes": "Review to delete.",
        },
    )

    assert create_response.status_code in [200, 201]
    review_log_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/reviews/{review_log_id}")

    assert delete_response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["source_type"] == "review_log"
    assert calls[0]["source_id"] == review_log_id