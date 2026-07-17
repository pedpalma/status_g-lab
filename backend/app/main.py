"""Ponto de entrada da aplicação FastAPI.
Neste momento a aplicação contem apenas endpoints de verificação de saúde,
usados para confirmar que os containers docker sobem
corretamente e conseguem se comunicar entre si.
"""

from fastapi import Depends, FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db

app = FastAPI(title="Status G-Lab Telecom API")


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
