"""Fixtures compartilhadas por todos os domínios. Fixtures específicas
de um domínio ficam em tests/domains/<dominio>/conftest.py."""

from typing import Generator

import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
