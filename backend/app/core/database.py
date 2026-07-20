"""
REFERÊNCIA — este arquivo já existe no projeto (current_state.txt confirma
app/core/database.py com engine+get_db). Incluído aqui apenas para permitir
testar security.py, deps.py e o domínio auth de forma isolada.

Ponto de atenção: se o database.py real ainda não tiver a classe `Base`
(não mencionada em current_state.txt, e models.py é o primeiro model do
projeto), adicionar apenas o bloco `Base` abaixo ao arquivo real — sem
necessidade de reescrever engine/get_db, que já devem existir e funcionar
(validado por /health/db).
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base declarativa. Todo model novo (users, routes, etc.) herda daqui."""

    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
