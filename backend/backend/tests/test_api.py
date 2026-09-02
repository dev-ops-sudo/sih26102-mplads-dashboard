def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"]
    assert client.get("/health/ready").json()["database"] == "ok"


def test_dashboard_bootstrap(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert len(body["projects"]) >= 7
    assert body["projects"][0]["riskScore"] >= body["projects"][-1]["riskScore"]
    assert body["alerts"]
    assert body["monthlyTrend"]
    assert body["situationBrief"]


def test_project_filters_and_intelligence(client):
    projects = client.get("/api/v1/projects", params=[("states", "Delhi")])
    assert projects.status_code == 200
    assert all(project["state"] == "Delhi" for project in projects.json())

    project_id = projects.json()[0]["id"]
    intelligence = client.get(f"/api/v1/projects/{project_id}/intelligence")
    assert intelligence.status_code == 200
    body = intelligence.json()
    assert sum(item["weight"] for item in body["riskContributions"]) == 100
    assert body["anomalies"]
    assert body["timeline"]
    assert body["media"]

    assert client.get(f"/api/v1/projects/{project_id}/risk").status_code == 200
    assert client.get(f"/api/v1/projects/{project_id}/timeline").json()
    assert client.get(f"/api/v1/projects/{project_id}/financials").json()
    assert client.get(f"/api/v1/projects/{project_id}/inspections").json()
    assert client.get(f"/api/v1/projects/{project_id}/media").json()


def test_panel_resource_endpoints(client):
    assert client.get("/api/v1/agencies").json()
    assert client.get("/api/v1/anomalies").json()
    assert client.get("/api/v1/predictions").json()
    assert client.get("/api/v1/duplicate-relationships").json()


def test_duplicate_detection_is_exposed(client):
    response = client.get("/api/v1/projects/MP-102-UP-117/intelligence")
    assert response.status_code == 200
    relationships = response.json()["duplicateRelationships"]
    assert relationships
    assert relationships[0]["similarityScore"] >= 55
    assert relationships[0]["distanceKm"] < 15


def test_investigation_uses_evidence_without_api_key(client):
    response = client.post(
        "/api/v1/investigation/query",
        json={"projectId": "MP-102-DEL-014", "question": "What financial evidence should be verified first?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "rules-based-demo"
    assert body["evidence"]
    assert "risk indicators" in body["answer"].lower()


def test_alert_acknowledgement_is_auditable_mutation(client):
    alerts = client.get("/api/v1/alerts", params={"acknowledged": "false"}).json()
    assert alerts
    alert_id = alerts[0]["id"]
    response = client.patch(f"/api/v1/alerts/{alert_id}/acknowledge")
    assert response.status_code == 200
    assert response.json()["acknowledged"] is True


def test_local_upload_contract(client):
    from pathlib import Path

    response = client.post(
        "/api/v1/uploads/presign",
        json={
            "projectId": "MP-102-DEL-014",
            "stage": "during",
            "filename": "inspection.jpg",
            "contentType": "image/jpeg",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "PUT"
    assert body["objectKey"].startswith("projects/MP-102-DEL-014/during/")
    stored_file = Path("work/uploads") / body["objectKey"]
    try:
        uploaded = client.put(body["uploadUrl"], content=b"demonstration-image-bytes", headers=body["headers"])
        assert uploaded.status_code == 204
        completed = client.post(
            "/api/v1/uploads/complete",
            json={
                "projectId": "MP-102-DEL-014",
                "stage": "during",
                "objectKey": body["objectKey"],
                "latitude": 28.61,
                "longitude": 77.20,
            },
        )
        assert completed.status_code == 200
        assert completed.json()["status"] == "registered"
    finally:
        if stored_file.exists():
            stored_file.unlink()


def test_state_officer_scope_is_enforced_in_sqlite_development(client):
    from app.auth import Principal, get_current_user
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: Principal(
        id="state-officer",
        name="State Officer",
        roles={"StateOfficer"},
        state="Delhi",
    )
    try:
        projects = client.get("/api/v1/projects")
        assert projects.status_code == 200
        assert projects.json()
        assert all(project["state"] == "Delhi" for project in projects.json())
        blocked = client.get("/api/v1/projects/MP-102-UP-117")
        assert blocked.status_code == 404
    finally:
        app.dependency_overrides.clear()
