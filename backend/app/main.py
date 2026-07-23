"""Ponto de entrada da aplicação FastAPI."""

from fastapi import Depends, FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.routers.auth import router as auth_router
from app.routers.incident_types import router as incident_types_router
from app.routers.incident_updates import router as incident_updates_router
from app.routers.incidents import router as incidents_router
from app.routers.routes import router as routes_router
from app.routers.users import router as users_router

app = FastAPI(title="Status G-Lab Telecom API")

# Necessário porque o frontend privado chama a API direto do navegador
# (origem diferente: :3000 -> :8000), não via server-side fetch.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(routes_router)
app.include_router(incident_types_router)
app.include_router(incidents_router)
app.include_router(incident_updates_router)


@app.get("/health")
def health_check() -> dict:
    """Confirma que a aplicação FastAPI está rodando e respondendo.
    Não depende do banco de dados."""
    return {"status": "ok"}


@app.get("/health/db")
def health_check_db(response: Response, db: Session = Depends(get_db)) -> dict:
    """Confirma que o backend consegue se conectar ao container do postgres.
    Retorna 503 quando a conexão falha, para permitir verificação por
    ferramentas de monitoramento além de checagem manual."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "database": "unreachable"}
