def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "career-forge-api"
    assert "status" in body
    assert "database" in body
