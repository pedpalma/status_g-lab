"""Testes do sobrecurso incident_updates e do router
app/routers/incident_updates.py."""

from app.domains.incidents.models import Incident


def test_create_update_tecnico_ok(
    db, client, tecnico_headers, incidente_existente, status_concluido
):
    payload = {"status_id": status_concluido.id, "comment": "Reparo concluído."}
    response = client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers=tecnico_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["incident_id"] == incidente_existente.id
    assert body["status_id"] == status_concluido.id
    assert body["status_name"] == "concluído"
    assert body["status_is_final"] is True
    assert body["comment"] == "Reparo concluído."


def test_create_update_admin_ok(
    client, admin_headers, incidente_existente, status_aberto
):
    payload = {"status_id": status_aberto.id}
    response = client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers=admin_headers,
    )
    assert response.status_code == 201


def test_create_update_sem_comment(
    client, tecnico_headers, incidente_existente, status_aberto
):
    payload = {"status_id": status_aberto.id}
    response = client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers=tecnico_headers,
    )
    assert response.status_code == 201
    assert response.json()["comment"] is None


def test_create_update_status_final_encerra_incidente(
    db, client, tecnico_headers, incidente_existente, status_concluido
):
    payload = {"status_id": status_concluido.id}
    client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers=tecnico_headers,
    )
    incident = db.get(Incident, incidente_existente.id)
    assert incident.closed_at is not None
    assert incident.status_id == status_concluido.id


def test_create_update_status_nao_final_nao_encerra(
    db, client, tecnico_headers, incidente_existente, status_aberto
):
    payload = {"status_id": status_aberto.id}
    client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers=tecnico_headers,
    )
    incident = db.get(Incident, incidente_existente.id)
    assert incident.closed_at is None
    assert incident.status_id == status_aberto.id


def test_create_update_sem_token(client, incidente_existente, status_aberto):
    payload = {"status_id": status_aberto.id}
    response = client.post(f"/incidents/{incidente_existente.id}/updates", json=payload)
    assert response.status_code == 401


def test_create_update_token_invalido(client, incidente_existente, status_aberto):
    payload = {"status_id": status_aberto.id}
    response = client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers={"Authorization": "Bearer token_invalido"},
    )
    assert response.status_code == 401


def test_create_update_status_id_invalido(client, tecnico_headers, incidente_existente):
    payload = {"status_id": 999999999}
    response = client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json=payload,
        headers=tecnico_headers,
    )
    assert response.status_code == 400


def test_create_update_incident_id_invalido(client, tecnico_headers, status_aberto):
    payload = {"status_id": status_aberto.id}
    response = client.post(
        "/incidents/999999999/updates", json=payload, headers=tecnico_headers
    )
    assert response.status_code == 404


def test_list_updates_publico_sem_token(
    client, tecnico_headers, incidente_existente, status_concluido
):
    client.post(
        f"/incidents/{incidente_existente.id}/updates",
        json={"status_id": status_concluido.id},
        headers=tecnico_headers,
    )
    response = client.get(f"/incidents/{incidente_existente.id}/updates")
    assert response.status_code == 200
    assert len(response.json()) == 1
