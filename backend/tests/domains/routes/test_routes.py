from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.domains.routes.models import Route


# create
def test_create_route_ok(client: TestClient, admin_headers: dict, db: Session):
    response = client.post(
        "/routes",
        json={"name": "Backbone SP-RJ", "description": "Rota principal SP-RJ"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Backbone SP-RJ"
    assert body["is_active"] is True

    # limpeza: esta rota não vem de fixture, precisa ser removida manualmente
    db.query(Route).filter(Route.id == body["id"]).delete()
    db.commit()


def test_create_route_nome_duplicado(
    client: TestClient, admin_headers: dict, rota_ativa: Route
):
    response = client.post(
        "/routes",
        json={"name": rota_ativa.name, "description": "Outra descrição"},
        headers=admin_headers,
    )
    assert response.status_code == 409


def test_create_route_nome_vazio(client: TestClient, admin_headers: dict):
    response = client.post(
        "/routes",
        json={"name": "", "description": "Descrição qualquer"},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_create_route_sem_token(client: TestClient):
    response = client.post(
        "/routes",
        json={"name": "Rota Sem Token", "description": None},
    )
    assert response.status_code == 401


def test_create_route_tecnico_bloqueado(client: TestClient, tecnico_headers: dict):
    response = client.post(
        "/routes",
        json={"name": "Rota Tecnico", "description": None},
        headers=tecnico_headers,
    )
    assert response.status_code == 403


# list
def test_list_routes_ok(client: TestClient, admin_headers: dict, rota_ativa: Route):
    response = client.get("/routes", headers=admin_headers)
    assert response.status_code == 200
    nomes = [r["name"] for r in response.json()]
    assert rota_ativa.name in nomes


def test_list_routes_tecnico_bloqueado(client: TestClient, tecnico_headers: dict):
    response = client.get("/routes", headers=tecnico_headers)
    assert response.status_code == 403


# get
def test_get_route_ok(client: TestClient, admin_headers: dict, rota_ativa: Route):
    response = client.get(f"/routes/{rota_ativa.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == rota_ativa.id


def test_get_route_nao_encontrada(client: TestClient, admin_headers: dict):
    response = client.get("/routes/999999", headers=admin_headers)
    assert response.status_code == 404


def test_get_route_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, rota_ativa: Route
):
    response = client.get(f"/routes/{rota_ativa.id}", headers=tecnico_headers)
    assert response.status_code == 403


# update
def test_update_route_ok(client: TestClient, admin_headers: dict, rota_ativa: Route):
    response = client.patch(
        f"/routes/{rota_ativa.id}",
        json={"description": "Descrição atualizada"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Descrição atualizada"


def test_update_route_nome_duplicado(
    client: TestClient, admin_headers: dict, rota_ativa: Route, db: Session
):
    outra = Route(name="Rota Auxiliar Teste", is_active=True)
    db.add(outra)
    db.commit()
    db.refresh(outra)

    response = client.patch(
        f"/routes/{outra.id}",
        json={"name": rota_ativa.name},
        headers=admin_headers,
    )
    assert response.status_code == 409

    db.query(Route).filter(Route.id == outra.id).delete()
    db.commit()


def test_update_route_nao_encontrada(client: TestClient, admin_headers: dict):
    response = client.patch(
        "/routes/999999", json={"description": "Não importa"}, headers=admin_headers
    )
    assert response.status_code == 404


def test_update_route_reativar_via_is_active(
    client: TestClient, admin_headers: dict, rota_ativa: Route, db: Session
):
    rota_ativa.is_active = False
    db.commit()

    response = client.patch(
        f"/routes/{rota_ativa.id}", json={"is_active": True}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_update_route_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, rota_ativa: Route
):
    response = client.patch(
        f"/routes/{rota_ativa.id}",
        json={"description": "Não deveria funcionar"},
        headers=tecnico_headers,
    )
    assert response.status_code == 403


# deactivate
def test_deactivate_route_ok(
    client: TestClient, admin_headers: dict, rota_ativa: Route
):
    response = client.delete(f"/routes/{rota_ativa.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_deactivate_route_nao_encontrada(client: TestClient, admin_headers: dict):
    response = client.delete("/routes/999999", headers=admin_headers)
    assert response.status_code == 404


def test_deactivate_route_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, rota_ativa: Route
):
    response = client.delete(f"/routes/{rota_ativa.id}", headers=tecnico_headers)
    assert response.status_code == 403
