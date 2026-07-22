"""Testes do cliente ViaCEP (app/external/cep.py). Sem dependência de banco."""

import httpx
import pytest

from app.external.cep import CepLookupResult, lookup_cep


def _fake_response(
    url: str, status: int = 200, json_data: dict | None = None
) -> httpx.Response:
    request = httpx.Request("GET", url)
    return httpx.Response(status, request=request, json=json_data or {})


def test_lookup_cep_ok(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.external.cep.httpx.get",
        lambda url, timeout: _fake_response(
            url,
            json_data={
                "localidade": "São Paulo",
                "logradouro": "Avenida Paulista",
                "erro": False,
            },
        ),
    )
    resultado = lookup_cep("01310-100")
    assert resultado == CepLookupResult(city="São Paulo", street="Avenida Paulista")


def test_lookup_cep_formato_invalido():
    assert lookup_cep("123") == CepLookupResult(city=None, street=None)


def test_lookup_cep_nao_encontrado(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.external.cep.httpx.get",
        lambda url, timeout: _fake_response(url, json_data={"erro": True}),
    )
    assert lookup_cep("00000000") == CepLookupResult(city=None, street=None)


def test_lookup_cep_timeout(monkeypatch: pytest.MonkeyPatch):
    def _raise_timeout(url, timeout):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr("app.external.cep.httpx.get", _raise_timeout)
    assert lookup_cep("01310-100") == CepLookupResult(city=None, street=None)


def test_lookup_cep_erro_http(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.external.cep.httpx.get",
        lambda url, timeout: _fake_response(url, status=500),
    )
    assert lookup_cep("01310-100") == CepLookupResult(city=None, street=None)


def test_lookup_cep_resposta_sem_logradouro(monkeypatch: pytest.MonkeyPatch):
    """Alguns CEPs (ex: zona rural) retornam localidade sem logradouro."""
    monkeypatch.setattr(
        "app.external.cep.httpx.get",
        lambda url, timeout: _fake_response(
            url, json_data={"localidade": "Cidade Exemplo", "erro": False}
        ),
    )
    resultado = lookup_cep("01310-100")
    assert resultado == CepLookupResult(city="Cidade Exemplo", street=None)
