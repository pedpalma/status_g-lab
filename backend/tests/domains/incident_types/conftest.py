"""Fixtures do domínio incident_types. Segue o mesmo padrão de
tests/domains/routes/conftest.py: app de teste isolado, só com o router
sob teste, dependency_override de get_db."""

from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token, hash_password
from app.domains.incident_types.models import IncidentType
from app.domains.users.models import User
from app.routers.incident_types import router as incident_types_router


@pytest.fixture()
def app(db: Session) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(incident_types_router)

    def override_get_db():
        yield db

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def usuario_admin(db: Session) -> Generator[User, None, None]:
    user = User(
        name="Admin Teste",
        email="admin.teste.incident_types@glab.com.br",
        password_hash=hash_password("senha123"),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(User).filter(User.id == user.id).delete()
    db.commit()


@pytest.fixture()
def usuario_ativo(db: Session) -> Generator[User, None, None]:
    user = User(
        name="Tecnico Teste",
        email="tecnico.teste.incident_types@glab.com.br",
        password_hash=hash_password("senha123"),
        role="tecnico",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(User).filter(User.id == user.id).delete()
    db.commit()


@pytest.fixture()
def admin_headers(usuario_admin: User) -> dict:
    token = create_access_token(subject=str(usuario_admin.id), role=usuario_admin.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def tecnico_headers(usuario_ativo: User) -> dict:
    token = create_access_token(subject=str(usuario_ativo.id), role=usuario_ativo.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def tipo_ativo(db: Session) -> Generator[IncidentType, None, None]:
    incident_type = IncidentType(name="Rompimento Teste", is_active=True)
    db.add(incident_type)
    db.commit()
    db.refresh(incident_type)
    yield incident_type
    db.query(IncidentType).filter(IncidentType.id == incident_type.id).delete()
    db.commit()
