from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_resources_are_available_without_jwt_in_development_mode():
    response = client.get("/api/v1/pets/")
    assert response.status_code == 200


def test_database_backed_routes_are_documented():
    paths = app.openapi()["paths"]
    assert "/api/v1/auth/register" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/health/db" in paths
    assert "/api/v1/pets/" in paths
    assert "/api/v1/appointments/" in paths
