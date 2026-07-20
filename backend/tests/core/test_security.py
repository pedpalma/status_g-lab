import time

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_gera_hash_diferente_da_senha():
    hashed = hash_password("minhaSenha123")
    assert hashed != "minhaSenha123"
    assert hashed.startswith("$2b$")


def test_verify_password_aceita_senha_correta():
    hashed = hash_password("minhaSenha123")
    assert verify_password("minhaSenha123", hashed) is True


def test_verify_password_rejeita_senha_incorreta():
    hashed = hash_password("minhaSenha123")
    assert verify_password("outraSenha", hashed) is False


def test_verify_password_nao_lanca_excecao_para_hash_invalido():
    assert verify_password("qualquer", "hash-invalido") is False


def test_verify_password_nao_lanca_excecao_para_senha_maior_que_72_bytes():
    senha_longa = "a" * 200
    hashed = hash_password("senha_normal")
    assert verify_password(senha_longa, hashed) is False


def test_create_and_decode_access_token_roundtrip():
    token = create_access_token(subject="42", role="tecnico")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "tecnico"
    assert "exp" in payload


def test_decode_access_token_rejeita_token_adulterado():
    token = create_access_token(subject="42", role="tecnico")
    token_adulterado = token[:-2] + "xx"
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token_adulterado)
