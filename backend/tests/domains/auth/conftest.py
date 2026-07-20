from typing import Generator

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_role
from app.core.security import hash_password
from app.domains.users.models import User
from app.routers.auth import router as auth_router


@pytest.fixture()
def app(db: Session) -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(auth_router)

    # rotas de apoio só para os testes, validam get_current_user/require_role
    @test_app.get("/private/ping")
    def ping(user: User = Depends(get_current_user)):
        return {"user_id": user.id, "role": user.role}

    @test_app.get("/private/admin-only")
    def admin_only(user: User = Depends(require_role("admin"))):
        return {"user_id": user.id, "role": user.role}

    def override_get_db():
        yield db

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def usuario_ativo(db: Session) -> Generator[User, None, None]:
    user = User(
        name="Tecnico Teste",
        email="tecnico.teste@glab.com.br",
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
def usuario_inativo(db: Session) -> Generator[User, None, None]:
    user = User(
        name="Ex Funcionario",
        email="inativo.teste@glab.com.br",
        password_hash=hash_password("senha123"),
        role="tecnico",
        is_active=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(User).filter(User.id == user.id).delete()
    db.commit()
