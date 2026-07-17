"""Engine e sessão do SQLAlchemy.
SQLAlchemy síncrono por decisão de simplicidade:
o volume de acesso concorrente esperado para este sistema não justifica a
complexidade adicional de sessions assíncronas."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI: entrega uma sessão por request e garante o
    fechamento ao final, mesmo em caso de exceção."""
    # TODO: quando o domínio auth for implementado, mover está função para app/core/deps.py junto de get_current_user e require_role.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
