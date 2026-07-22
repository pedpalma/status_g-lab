"""Fixtures do domínio incidents."""

from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token, hash_password
from app.domains.incident_status.models import IncidentStatus
from app.domains.incident_types.models import IncidentType
from app.domains.incidents.models import Incident
from app.domains.incidents.services import create_incident
from app.domains.routes.models import Route
from app.domains.users.models import User
from app.routers.incidents import router as incidents_router


@pytest.fixture()
def app(db: Session) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(incidents_router)
    test_app.dependency_overrides[get_db] = lambda: db
    return test_app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def usuario_admin(db: Session) -> Generator[User, None, None]:
    user = User(
        name="Admin Teste Incidents",
        email="admin@teste.com.incidents",
        password_hash=hash_password("senha123"),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(User).filter(User.id == user.id).delete()
    db.commit()


@pytest.fixture()
def usuario_ativo(db: Session) -> Generator[User, None, None]:
    """Usuário tecnico ativo."""
    user = User(
        name="Tecnico Teste Incidents",
        email="tecnico@teste.com.incidents",
        password_hash=hash_password("senha123"),
        role="tecnico",
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
    route = Route(name="Rota Teste Incidents", description=None)
    db.add(route)
    db.commit()
    db.refresh(route)
    yield route
    db.query(Route).filter(Route.id == route.id).delete()
    db.commit()


@pytest.fixture()
def tipo_ativo(db: Session) -> IncidentType:
    """Reaproveita o seed de incident_types (0001_initial.sql), não cria nada."""
    tipo = db.query(IncidentType).filter(IncidentType.name == "rompimento").first()
    assert tipo is not None, (
        "seed 'rompimento' ausente em incident_types (ver 0001_initial.sql)"
    )
    return tipo


@pytest.fixture()
def tipo_outro(db: Session) -> IncidentType:
    """Segundo tipo do seed, usado pra provar que o filtro por type_id exclui."""
    tipo = db.query(IncidentType).filter(IncidentType.name == "furto").first()
    assert tipo is not None, (
        "seed 'furto' ausente em incident_types (ver 0001_initial.sql)"
    )
    return tipo


@pytest.fixture()
def status_aberto(db: Session) -> IncidentStatus:
    """Reaproveita o seed de incident_status (0001_initial.sql), não cria nada."""
    status_row = (
        db.query(IncidentStatus).filter(IncidentStatus.name == "aberto").first()
    )
    assert status_row is not None, (
        "seed 'aberto' ausente em incident_status (ver 0001_initial.sql)"
    )
    return status_row


@pytest.fixture()
def status_concluido(db: Session) -> IncidentStatus:
    status_row = (
        db.query(IncidentStatus).filter(IncidentStatus.name == "concluído").first()
    )
    assert status_row is not None, (
        "seed 'concluído' ausente em incident_status (ver 0001_initial.sql)"
    )
    return status_row


@pytest.fixture()
def incidente_existente(
    db: Session,
    usuario_ativo: User,
    rota_ativa: Route,
    tipo_ativo: IncidentType,
) -> Generator[Incident, None, None]:
    """Incidente já criado no banco, usado pelos testes de leitura (list/get)."""
    incident = create_incident(
        db,
        type_id=tipo_ativo.id,
        route_id=rota_ativa.id,
        cep="01310-100",
        description="Incidente de teste para leitura.",
        created_by=usuario_ativo.id,
    )
    yield incident
    db.query(Incident).filter(Incident.id == incident.id).delete()
    db.commit()
