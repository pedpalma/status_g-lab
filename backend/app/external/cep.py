"""Cliente ViaCEP: resolve cidade e logradouro a partir do CEP."""

import re
from dataclasses import dataclass

import httpx

from app.core.config import settings

TIMEOUT_SECONDS = 3.0


@dataclass
class CepLookupResult:
    city: str | None
    street: str | None


_LOOKUP_FALHOU = CepLookupResult(city=None, street=None)


def lookup_cep(cep: str) -> CepLookupResult:
    """Consulta cidade e logradouro correspondentes ao CEP via ViaCEP."""
    digits = re.sub(r"\D", "", cep)
    if len(digits) != 8:
        return _LOOKUP_FALHOU

    url = f"{settings.VIACEP_BASE_URL}/{digits}/json/"
    try:
        response = httpx.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return _LOOKUP_FALHOU

    if data.get("erro"):
        return _LOOKUP_FALHOU

    return CepLookupResult(
        city=data.get("localidade") or None,
        street=data.get("logradouro") or None,
    )
