def test_submit_run_and_status(client):
    payload = {"model_id": "crop_yield_predictor", "region": "IA-Central", "year": 2010}
    r = client.post("/api/runs", json=payload)
    assert r.status_code == 200
    run_id = r.json()["run_id"]

    r = client.get(f"/api/runs/{run_id}/status")
    assert r.status_code == 200
    allowed = {"queued","preprocessing","computing","postprocessing","succeeded","failed","running"}
    assert r.json()["status"] in allowed
