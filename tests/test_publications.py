def test_create_publication_success(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "title": "Test Article",
        "text": "Content",
        "category": "Test",
        "image_url": "https://example.com/img.jpg"
    }
    resp = api_client.post("/publication/create", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Article"
    assert "publication_id" in data
    assert "created_at" in data


def test_create_publication_unauthorized(api_client):
    payload = {"title": "No Auth", "text": "Content", "category": "Test", "image_url": "http://a.com"}
    resp = api_client.post("/publication/create", json=payload)
    assert resp.status_code == 401


def test_get_all_publications_paginated(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    for i in range(3):
        api_client.post("/publication/create", json={
            "title": f"Article {i}",
            "text": "Content",
            "category": "Test",
            "image_url": "http://a.com"
        }, headers=headers)

    resp = api_client.get("/publication/get_all?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_get_all_publications_default_pagination(api_client):
    resp = api_client.get("/publication/get_all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_update_publication_success(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Создаём
    create = api_client.post("/publication/create", json={
        "title": "Original", "text": "Text", "category": "Cat", "image_url": "http://a.com"
    }, headers=headers)
    pub_id = create.json()["publication_id"]
    # Обновляем
    update = api_client.patch(f"/publication/edit/{pub_id}", json={"title": "Updated"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["title"] == "Updated"


def test_update_publication_not_found(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = api_client.patch(f"/publication/edit/{fake_id}", json={"title": "New"}, headers=headers)
    assert resp.status_code == 404


def test_update_publication_forbidden(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Публикация первого пользователя
    create = api_client.post("/publication/create", json={
        "title": "Original", "text": "Text", "category": "Cat", "image_url": "http://a.com"
    }, headers=headers)
    pub_id = create.json()["publication_id"]

    # Второй пользователь
    api_client.post("/auth/register", json={
        "username": "seconduser", "email": "second@example.com", "password": "pass"
    })
    login = api_client.post("/auth/login", data={"username": "seconduser", "password": "pass"})
    token2 = login.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp = api_client.patch(f"/publication/edit/{pub_id}", json={"title": "Hacked"}, headers=headers2)
    assert resp.status_code == 403
    assert "Not enough permissions" in resp.json()["detail"]


def test_soft_delete_publication(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    create = api_client.post("/publication/create", json={
        "title": "To Delete", "text": "Content", "category": "Test", "image_url": "http://a.com"
    }, headers=headers)
    pub_id = create.json()["publication_id"]

    delete = api_client.delete(f"/publication/delete/{pub_id}", headers=headers)
    assert delete.status_code == 204

    all_pub = api_client.get("/publication/get_all")
    assert all(p["publication_id"] != pub_id for p in all_pub.json()["items"])

    deleted = api_client.get("/publication/deleted")
    assert any(d["publication_id"] == pub_id for d in deleted.json()["items"])


def test_restore_publication(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    create = api_client.post("/publication/create", json={
        "title": "To Restore", "text": "Content", "category": "Test", "image_url": "http://a.com"
    }, headers=headers)
    pub_id = create.json()["publication_id"]

    api_client.delete(f"/publication/delete/{pub_id}", headers=headers)
    restore = api_client.post(f"/publication/restore/{pub_id}", headers=headers)
    assert restore.status_code == 200
    assert restore.json()["publication_id"] == pub_id

    all_pub = api_client.get("/publication/get_all")
    assert any(p["publication_id"] == pub_id for p in all_pub.json()["items"])


def test_get_deleted_publications(api_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    create = api_client.post("/publication/create", json={
        "title": "For Deleted List", "text": "Content", "category": "Test", "image_url": "http://a.com"
    }, headers=headers)
    pub_id = create.json()["publication_id"]
    api_client.delete(f"/publication/delete/{pub_id}", headers=headers)

    resp = api_client.get("/publication/deleted")
    assert resp.status_code == 200
    assert any(item["publication_id"] == pub_id for item in resp.json()["items"])