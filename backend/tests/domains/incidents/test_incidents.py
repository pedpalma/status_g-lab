"""Testes do domínio incidents e do router app/routers/incidents.py."""

from sqlalchemy.orm import Session

from app.domains.incidents.models import Incident


def _cleanup_incident(db: Session, incident_id: int) -> None:
    db.query(Incident).filter(Incident.id == incident_id).delete()
    db.commit()


def test_create_incident_tecnico_ok(
    db, client, tecnico_headers, rota_ativa, tipo_ativo, status_aberto
):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "01310-100",
        "description": "Rompimento de cabo na altura do km 12.",
    }
    response = client.post("/incidents", json=payload, headers=tecnico_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["status_id"] == status_aberto.id
    assert body["city"] is None
    assert body["closed_at"] is None
    _cleanup_incident(db, body["id"])


def test_create_incident_admin_ok(db, client, admin_headers, rota_ativa, tipo_ativo):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "01310100",
        "description": "Manutenção preventiva programada.",
    }
    response = client.post("/incidents", json=payload, headers=admin_headers)
    assert response.status_code == 201
    _cleanup_incident(db, response.json()["id"])


def test_create_incident_sem_token(client, rota_ativa, tipo_ativo):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "01310-100",
        "description": "x",
    }
    response = client.post("/incidents", json=payload)
    assert response.status_code == 401


def test_create_incident_token_invalido(client, rota_ativa, tipo_ativo):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "01310-100",
        "description": "x",
    }
    response = client.post(
        "/incidents", json=payload, headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401


def test_create_incident_type_id_invalido(client, tecnico_headers, rota_ativa):
    payload = {
        "type_id": 999999999,
        "route_id": rota_ativa.id,
        "cep": "01310-100",
        "description": "x",
    }
    response = client.post("/incidents", json=payload, headers=tecnico_headers)
    assert response.status_code == 400


def test_create_incident_route_id_invalido(client, tecnico_headers, tipo_ativo):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": 999999999,
        "cep": "01310-100",
        "description": "x",
    }
    response = client.post("/incidents", json=payload, headers=tecnico_headers)
    assert response.status_code == 400


def test_create_incident_cep_muito_curto(
    client, tecnico_headers, rota_ativa, tipo_ativo
):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "123",
        "description": "x",
    }
    response = client.post("/incidents", json=payload, headers=tecnico_headers)
    assert response.status_code == 422


def test_create_incident_description_vazia(
    client, tecnico_headers, rota_ativa, tipo_ativo
):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "01310-100",
        "description": "",
    }
    response = client.post("/incidents", json=payload, headers=tecnico_headers)
    assert response.status_code == 422


def test_create_incident_created_by_e_usuario_autenticado(
    db, client, tecnico_headers, usuario_ativo, rota_ativa, tipo_ativo
):
    payload = {
        "type_id": tipo_ativo.id,
        "route_id": rota_ativa.id,
        "cep": "01310-100",
        "description": "x",
    }
    response = client.post("/incidents", json=payload, headers=tecnico_headers)
    assert response.json()["created_by"] == usuario_ativo.id
    _cleanup_incident(db, response.json()["id"])


def test_list_incidents_publico_sem_token(client, incidente_existente):
    response = client.get("/incidents")
    assert response.status_code == 200
    ids = [i["id"] for i in response.json()]
    assert incidente_existente.id in ids


def test_list_incidents_filtro_status_id(
    client, incidente_existente, status_aberto, status_concluido
):
    response = client.get(f"/incidents?status_id={status_aberto.id}")
    ids = [i["id"] for i in response.json()]
    assert incidente_existente.id in ids

    response = client.get(f"/incidents?status_id={status_concluido.id}")
    ids = [i["id"] for i in response.json()]
    assert incidente_existente.id not in ids


def test_list_incidents_filtro_type_id(
    client, incidente_existente, tipo_ativo, tipo_outro
):
    response = client.get(f"/incidents?type_id={tipo_ativo.id}")
    ids = [i["id"] for i in response.json()]
    assert incidente_existente.id in ids

    response = client.get(f"/incidents?type_id={tipo_outro.id}")
    ids = [i["id"] for i in response.json()]
    assert incidente_existente.id not in ids


def test_get_incident_detail_publico(client, incidente_existente):
    response = client.get(f"/incidents/{incidente_existente.id}")
    assert response.status_code == 200
    assert response.json()["id"] == incidente_existente.id


def test_get_incident_detail_nao_encontrado(client):
    response = client.get("/incidents/999999999")
    assert response.status_code == 404
