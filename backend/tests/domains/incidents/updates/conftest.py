"""Fixtures do sobrecurso incident_updates."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.routers.incident_updates import router as incident_updates_router


@pytest.fixture()
def app(db: Session) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(incident_updates_router)
    test_app.dependency_overrides[get_db] = lambda: db
    return test_app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
