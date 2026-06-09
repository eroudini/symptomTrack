import json

def register_and_login(client, email="user@test.com", password="password123"):
    client.post(
        "/auth/register",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json"
    )
    resp = client.post(
        "/auth/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json"
    )
    return resp.get_json()["token"]

def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

LOG_DATA = {
    "pain_level": 4,
    "fatigue_level": 7,
    "mood_level": 6,
    "notes": "Test note"
}

# creation

def test_create_log_success(client):
    token = register_and_login(client)
    resp = client.post("/logs", data=json.dumps(LOG_DATA),
                       headers=auth_headers(token))
    assert resp.status_code == 201
    assert resp.get_json()["log"]["pain_level"] == 4

def test_create_log_without_token(client):
    resp = client.post("/logs", data=json.dumps(LOG_DATA),
                       content_type="application/json")
    assert resp.status_code == 401

def test_create_log_invalid_level(client):
    token = register_and_login(client)
    bad = {**LOG_DATA, "pain_level": 15}
    resp = client.post("/logs", data=json.dumps(bad),
                       headers=auth_headers(token))
    assert resp.status_code == 400


def test_create_duplicate_same_day(client):
    token = register_and_login(client)
    h = auth_headers(token)
    client.post("/logs", data=json.dumps(LOG_DATA), headers=h)
    resp = client.post("/logs", data=json.dumps(LOG_DATA), headers=h)
    assert resp.status_code == 409

# lecture

def test_get_logs_empty(client):
    token = register_and_login(client)
    h = auth_headers(token)
    resp = client.get("/logs", headers=h)
    assert resp.status_code == 200
    assert resp.get_json()["count"] == 0

def test_get_logs_after_create(client):
    token = register_and_login(client)
    h = auth_headers(token)
    client.post("/logs", data=json.dumps(LOG_DATA), headers=h)
    resp = client.get("/logs", headers=h)
    assert resp.get_json()["count"] == 1

def test_get_single_log(client):
    token = register_and_login(client)
    h = auth_headers(token)
    create = client.post("/logs", data=json.dumps(LOG_DATA), headers=h)
    log_id = create.get_json()["log"]["id"]
    resp = client.get(f"/logs/{log_id}", headers=h)
    assert resp.status_code == 200
    assert resp.get_json()["log"]["id"] == log_id

def test_get_nonexistant_log(client):
    token = register_and_login(client)
    resp = client.get("/logs/9999", headers=auth_headers(token))
    assert resp.status_code == 404

# sécurité isolation utilisateurs

def test_user_cannot_access_other_user_log(client):
    token_a = register_and_login(client, "a@test.com")
    token_b = register_and_login(client, "b@test.com")

    create = client.post("/logs", data=json.dumps(LOG_DATA),
                         headers=auth_headers(token_a))
    log_id = create.get_json()["log"]["id"]

    resp = client.get(f"/logs/{log_id}", headers=auth_headers(token_b))
    assert resp.status_code == 404

def test_user_cannot_delete_other_user_log(client):
    """User A ne peut PAS supprimer les logs de User B."""
    token_a = register_and_login(client, "a2@test.com")
    token_b = register_and_login(client, "b2@test.com")

    create = client.post("/logs", data=json.dumps(LOG_DATA),
                         headers=auth_headers(token_a))
    log_id = create.get_json()["log"]["id"]

    resp = client.delete(f"/logs/{log_id}", headers=auth_headers(token_b))
    assert resp.status_code == 404


#  Modification / Suppression 

def test_update_log(client):
    token = register_and_login(client)
    h = auth_headers(token)
    create = client.post("/logs", data=json.dumps(LOG_DATA), headers=h)
    log_id = create.get_json()["log"]["id"]

    updated = {**LOG_DATA, "pain_level": 1}
    resp = client.put(f"/logs/{log_id}", data=json.dumps(updated), headers=h)
    assert resp.status_code == 200
    assert resp.get_json()["log"]["pain_level"] == 1


def test_delete_log(client):
    token = register_and_login(client)
    h = auth_headers(token)
    create = client.post("/logs", data=json.dumps(LOG_DATA), headers=h)
    log_id = create.get_json()["log"]["id"]

    resp = client.delete(f"/logs/{log_id}", headers=h)
    assert resp.status_code == 200

    resp = client.get(f"/logs/{log_id}", headers=h)
    assert resp.status_code == 404


#  Stats 

def test_stats_empty(client):
    token = register_and_login(client)
    resp = client.get("/logs/stats", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.get_json()["total_logs"] == 0


def test_stats_with_logs(client):
    token = register_and_login(client)
    h = auth_headers(token)
    client.post("/logs", data=json.dumps(LOG_DATA), headers=h)

    resp = client.get("/logs/stats", headers=h)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "averages" in data
    assert "daily" in data
    assert data["total_logs"] == 1
    assert data["averages"]["pain"] == 4.0



