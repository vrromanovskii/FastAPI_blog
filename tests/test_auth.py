def test_register_success(api_client):
    resp = api_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "secret123"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data


def test_register_duplicate_username(api_client, test_user):
    resp = api_client.post(
        "/auth/register",
        json={
            "username": test_user["username"],
            "email": "unique@example.com",
            "password": "secret123"
        }
    )
    assert resp.status_code == 400
    assert "Username already registered" in resp.json()["detail"]


def test_register_duplicate_email(api_client, test_user):
    resp = api_client.post(
        "/auth/register",
        json={
            "username": "uniqueuser",
            "email": test_user["email"],
            "password": "secret123"
        }
    )
    assert resp.status_code == 400
    assert "Email already registered" in resp.json()["detail"]


def test_login_success(api_client, test_user):
    resp = api_client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(api_client, test_user):
    resp = api_client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_nonexistent_user(api_client):
    resp = api_client.post(
        "/auth/login",
        data={"username": "noone", "password": "any"}
    )
    assert resp.status_code == 401


def test_get_current_user_success(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = api_client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(api_client):
    resp = api_client.get("/auth/me")
    assert resp.status_code == 401