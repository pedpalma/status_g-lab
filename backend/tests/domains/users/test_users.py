from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.domains.users.models import User


# Create
def test_create_user_ok(client: TestClient, admin_headers: dict, db: Session):
    response = client.post(
        "/users",
        json={
            "name": "Novo Tecnico",
            "email": "novo.tecnico@glab.com.br",
            "password": "senha1234",
            "role": "tecnico",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "novo.tecnico@glab.com.br"
    assert body["is_active"] is True
    assert "password" not in body
    assert "password_hash" not in body

    # limpeza: este usuário não vem de fixture, precisa ser removido manualmente
    db.query(User).filter(User.id == body["id"]).delete()
    db.commit()


def test_create_user_email_duplicado(
    client: TestClient, admin_headers: dict, usuario_ativo: User
):
    response = client.post(
        "/users",
        json={
            "name": "Outro Nome",
            "email": usuario_ativo.email,
            "password": "senha1234",
            "role": "tecnico",
        },
        headers=admin_headers,
    )
    assert response.status_code == 409


def test_create_user_role_invalido(client: TestClient, admin_headers: dict):
    response = client.post(
        "/users",
        json={
            "name": "Role Invalido",
            "email": "role.invalido@glab.com.br",
            "password": "senha1234",
            "role": "supervisor",
        },
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_create_user_sem_token(client: TestClient):
    response = client.post(
        "/users",
        json={
            "name": "Sem Token",
            "email": "sem.token@glab.com.br",
            "password": "senha1234",
            "role": "tecnico",
        },
    )
    assert response.status_code == 401


def test_create_user_tecnico_bloqueado(client: TestClient, tecnico_headers: dict):
    response = client.post(
        "/users",
        json={
            "name": "Bloqueado",
            "email": "bloqueado@glab.com.br",
            "password": "senha1234",
            "role": "tecnico",
        },
        headers=tecnico_headers,
    )
    assert response.status_code == 403


# list / get
def test_list_users_admin_ok(
    client: TestClient, admin_headers: dict, usuario_ativo: User
):
    response = client.get("/users", headers=admin_headers)
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert usuario_ativo.email in emails


def test_list_users_tecnico_bloqueado(client: TestClient, tecnico_headers: dict):
    response = client.get("/users", headers=tecnico_headers)
    assert response.status_code == 403


def test_get_user_ok(client: TestClient, admin_headers: dict, usuario_ativo: User):
    response = client.get(f"/users/{usuario_ativo.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["email"] == usuario_ativo.email


def test_get_user_nao_encontrado(client: TestClient, admin_headers: dict):
    response = client.get("/users/999999", headers=admin_headers)
    assert response.status_code == 404


# Update
def test_update_user_nome_e_role(
    client: TestClient, admin_headers: dict, usuario_ativo: User
):
    response = client.patch(
        f"/users/{usuario_ativo.id}",
        json={"name": "Nome Atualizado", "role": "admin"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nome Atualizado"
    assert body["role"] == "admin"


def test_update_user_email_duplicado(
    client: TestClient, admin_headers: dict, usuario_ativo: User, usuario_admin: User
):
    response = client.patch(
        f"/users/{usuario_ativo.id}",
        json={"email": usuario_admin.email},
        headers=admin_headers,
    )
    assert response.status_code == 409


def test_update_user_reativa_via_is_active(
    client: TestClient, admin_headers: dict, usuario_ativo: User
):
    # desativa e depois reativa pelo mesmo endpoint de update
    client.delete(f"/users/{usuario_ativo.id}", headers=admin_headers)
    response = client.patch(
        f"/users/{usuario_ativo.id}",
        json={"is_active": True},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_update_user_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, usuario_ativo: User
):
    response = client.patch(
        f"/users/{usuario_ativo.id}",
        json={"name": "Tentativa"},
        headers=tecnico_headers,
    )
    assert response.status_code == 403


# Deactivate
def test_deactivate_user_ok(
    client: TestClient, admin_headers: dict, usuario_ativo: User
):
    response = client.delete(f"/users/{usuario_ativo.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_deactivate_user_nao_pode_a_si_mesmo(
    client: TestClient, admin_headers: dict, usuario_admin: User
):
    response = client.delete(f"/users/{usuario_admin.id}", headers=admin_headers)
    assert response.status_code == 400


def test_deactivate_user_tecnico_bloqueado(
    client: TestClient, tecnico_headers: dict, usuario_ativo: User
):
    response = client.delete(f"/users/{usuario_ativo.id}", headers=tecnico_headers)
    assert response.status_code == 403
