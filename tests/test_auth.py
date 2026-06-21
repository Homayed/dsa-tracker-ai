def test_register_user(client, test_user_data):
    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == test_user_data["name"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client, test_user_data):
    client.post("/auth/register", json=test_user_data)

    response = client.post("/auth/register", json=test_user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_user(client, test_user_data):
    client.post("/auth/register", json=test_user_data)

    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_fails(client, test_user_data):
    client.post("/auth/register", json=test_user_data)

    response = client.post(
        "/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_get_current_user(authenticated_client, test_user_data):
    response = authenticated_client.get("/users/me")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == test_user_data["name"]
    assert data["email"] == test_user_data["email"]
    assert "hashed_password" not in data


def test_get_current_user_without_token_fails(client):
    response = client.get("/users/me")

    assert response.status_code == 401