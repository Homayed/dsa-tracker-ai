def test_create_problem(authenticated_client):
    problem_data = {
        "title": "Two Sum",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Hash Map",
        "status": "Solved",
        "confidence_level": 4,
        "time_taken_minutes": 20,
        "solution_code": "def twoSum(nums, target): pass",
        "time_complexity": "O(n)",
        "space_complexity": "O(n)",
    }

    response = authenticated_client.post("/problems/", json=problem_data)

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == problem_data["title"]
    assert data["difficulty"] == problem_data["difficulty"]
    assert data["pattern"] == problem_data["pattern"]
    assert data["user_id"] == 1
    assert "id" in data


def test_get_problems(authenticated_client):
    problem_data = {
        "title": "Two Sum",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Hash Map",
        "status": "Solved",
        "confidence_level": 4,
    }

    authenticated_client.post("/problems/", json=problem_data)

    response = authenticated_client.get("/problems/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Two Sum"


def test_get_single_problem(authenticated_client):
    problem_data = {
        "title": "Valid Anagram",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Hash Map",
        "status": "Solved",
        "confidence_level": 5,
    }

    create_response = authenticated_client.post("/problems/", json=problem_data)
    problem_id = create_response.json()["id"]

    response = authenticated_client.get(f"/problems/{problem_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == problem_id
    assert data["title"] == "Valid Anagram"


def test_update_problem(authenticated_client):
    problem_data = {
        "title": "Move Zeroes",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Two Pointers",
        "status": "Solved",
        "confidence_level": 3,
    }

    create_response = authenticated_client.post("/problems/", json=problem_data)
    problem_id = create_response.json()["id"]

    update_data = {
        "confidence_level": 5,
        "status": "Solved",
    }

    response = authenticated_client.put(
        f"/problems/{problem_id}",
        json=update_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["confidence_level"] == 5
    assert data["status"] == "Solved"


def test_delete_problem(authenticated_client):
    problem_data = {
        "title": "Best Time to Buy and Sell Stock",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Two Pointers",
        "status": "Solved",
        "confidence_level": 4,
    }

    create_response = authenticated_client.post("/problems/", json=problem_data)
    problem_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/problems/{problem_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Problem deleted successfully"

    get_response = authenticated_client.get(f"/problems/{problem_id}")

    assert get_response.status_code == 404


def test_create_problem_without_token_fails(client):
    problem_data = {
        "title": "Two Sum",
        "platform": "LeetCode",
        "difficulty": "Easy",
        "pattern": "Hash Map",
        "status": "Solved",
        "confidence_level": 4,
    }

    response = client.post("/problems/", json=problem_data)

    assert response.status_code == 401