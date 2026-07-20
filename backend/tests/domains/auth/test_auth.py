def test_login_com_credenciais_corretas_retorna_token(client, usuario_ativo):
    response = client.post(
        "/auth/login",
        json={"email": usuario_ativo.email, "password": "senha123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_com_senha_errada_retorna_401(client, usuario_ativo):
    response = client.post(
        "/auth/login",
        json={"email": usuario_ativo.email, "password": "senhaErrada"},
    )
    assert response.status_code == 401


def test_login_com_email_inexistente_retorna_401(client):
    response = client.post(
        "/auth/login",
        json={"email": "nao.existe@glab.com.br", "password": "qualquer"},
    )
    assert response.status_code == 401


def test_login_com_usuario_inativo_retorna_401(client, usuario_inativo):
    response = client.post(
        "/auth/login",
        json={"email": usuario_inativo.email, "password": "senha123"},
    )
    assert response.status_code == 401


def test_rota_privada_sem_token_retorna_401(client):
    response = client.get("/private/ping")
    assert response.status_code == 401


def test_rota_privada_com_token_valido_retorna_dados_do_usuario(client, usuario_ativo):
    login_response = client.post(
        "/auth/login",
        json={"email": usuario_ativo.email, "password": "senha123"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/private/ping", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"user_id": usuario_ativo.id, "role": "tecnico"}


def test_rota_privada_com_token_invalido_retorna_401(client):
    response = client.get(
        "/private/ping", headers={"Authorization": "Bearer token.invalido.aqui"}
    )
    assert response.status_code == 401


def test_require_role_bloqueia_papel_sem_permissao(client, usuario_ativo):
    login_response = client.post(
        "/auth/login",
        json={"email": usuario_ativo.email, "password": "senha123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/private/admin-only", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_usuario_desativado_apos_emitir_token_perde_acesso(client, db, usuario_ativo):
    login_response = client.post(
        "/auth/login",
        json={"email": usuario_ativo.email, "password": "senha123"},
    )
    token = login_response.json()["access_token"]

    usuario_ativo.is_active = False
    db.add(usuario_ativo)
    db.commit()

    response = client.get("/private/ping", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
