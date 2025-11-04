def test_models_list(client):
    r = client.get("/api/models")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
