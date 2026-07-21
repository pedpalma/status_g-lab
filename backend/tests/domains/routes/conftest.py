"""Fixtures do domínio routes. Segue o mesmo padrão de
tests/domains/users/conftest.py: app de teste isolado, só com o router
sob teste, dependency_override de get_db."""

from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token, hash_password
from app.domains.routes.models import Route
from app.domains.users.models import User
from app.routers.routes import router as routes_router


@pytest.fixture()
def app(db: Session) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(routes_router)

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
        email="admin.teste.routes@glab.com.br",
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
        email="tecnico.teste.routes@glab.com.br",
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
def rota_ativa(db: Session) -> Generator[Route, None, None]:
    route = Route(
        name="Backbone SP-RJ Teste", description="Rota de teste", is_active=True
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    yield route
    db.query(Route).filter(Route.id == route.id).delete()
    db.commit()
