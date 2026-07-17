"""este automatizado do endpoint de health check básico."""
# TODO: adicionar teste para /health/db quando houver uma estrategia de banco de dados de teste definida

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
