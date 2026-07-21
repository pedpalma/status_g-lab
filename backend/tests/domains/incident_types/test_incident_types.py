from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.domains.incident_types.models import IncidentType


# create
def test_create_incident_type_ok(client: TestClient, admin_headers: dict, db: Session):
    response = client.post(
        "/incident-types",
        json={"name": "Queda de Energia"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Queda de Energia"
    assert body["is_active"] is True

    # limpeza: este tipo não vem de fixture, precisa ser removido manualmente
    db.query(IncidentType).filter(IncidentType.id == body["id"]).delete()
    db.commit()


def test_create_incident_type_nome_duplicado(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType
):
    response = client.post(
        "/incident-types",
        json={"name": tipo_ativo.name},
        headers=admin_headers,
    )
    assert response.status_code == 409


def test_create_incident_type_nome_vazio(client: TestClient, admin_headers: dict):
    response = client.post(
        "/incident-types",
        json={"name": ""},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_create_incident_type_sem_token(client: TestClient):
    response = client.post(
        "/incident-types",
        json={"name": "Tipo Sem Token"},
    )
    assert response.status_code == 401


def test_create_incident_type_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict
):
    response = client.post(
        "/incident-types",
        json={"name": "Tipo Tecnico"},
        headers=tecnico_headers,
    )
    assert response.status_code == 403


# list
def test_list_incident_types_ok(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType
):
    response = client.get("/incident-types", headers=admin_headers)
    assert response.status_code == 200
    nomes = [t["name"] for t in response.json()]
    assert tipo_ativo.name in nomes


def test_list_incident_types_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict
):
    response = client.get("/incident-types", headers=tecnico_headers)
    assert response.status_code == 403


# get
def test_get_incident_type_ok(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType
):
    response = client.get(f"/incident-types/{tipo_ativo.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == tipo_ativo.id


def test_get_incident_type_nao_encontrado(client: TestClient, admin_headers: dict):
    response = client.get("/incident-types/999999", headers=admin_headers)
    assert response.status_code == 404


def test_get_incident_type_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, tipo_ativo: IncidentType
):
    response = client.get(f"/incident-types/{tipo_ativo.id}", headers=tecnico_headers)
    assert response.status_code == 403


# update
def test_update_incident_type_ok(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType
):
    response = client.patch(
        f"/incident-types/{tipo_ativo.id}",
        json={"name": "Nome Atualizado"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Nome Atualizado"


def test_update_incident_type_nome_duplicado(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType, db: Session
):
    outro = IncidentType(name="Tipo Auxiliar Teste", is_active=True)
    db.add(outro)
    db.commit()
    db.refresh(outro)

    response = client.patch(
        f"/incident-types/{outro.id}",
        json={"name": tipo_ativo.name},
        headers=admin_headers,
    )
    assert response.status_code == 409

    db.query(IncidentType).filter(IncidentType.id == outro.id).delete()
    db.commit()


def test_update_incident_type_nao_encontrado(client: TestClient, admin_headers: dict):
    response = client.patch(
        "/incident-types/999999", json={"name": "Não importa"}, headers=admin_headers
    )
    assert response.status_code == 404


def test_update_incident_type_reativar_via_is_active(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType, db: Session
):
    tipo_ativo.is_active = False
    db.commit()

    response = client.patch(
        f"/incident-types/{tipo_ativo.id}",
        json={"is_active": True},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_update_incident_type_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, tipo_ativo: IncidentType
):
    response = client.patch(
        f"/incident-types/{tipo_ativo.id}",
        json={"name": "Não deveria funcionar"},
        headers=tecnico_headers,
    )
    assert response.status_code == 403


# deactivate
def test_deactivate_incident_type_ok(
    client: TestClient, admin_headers: dict, tipo_ativo: IncidentType
):
    response = client.delete(f"/incident-types/{tipo_ativo.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_deactivate_incident_type_nao_encontrado(
    client: TestClient, admin_headers: dict
):
    response = client.delete("/incident-types/999999", headers=admin_headers)
    assert response.status_code == 404


def test_deactivate_incident_type_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, tipo_ativo: IncidentType
):
    response = client.delete(
        f"/incident-types/{tipo_ativo.id}", headers=tecnico_headers
    )
    assert response.status_code == 403
