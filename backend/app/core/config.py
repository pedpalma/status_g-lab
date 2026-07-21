"""
Configurações da aplicação.
Centraliza a leitura de variáveis de ambiente em um único objeto tipado.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Banco de dados. Em docker-compose.yml, DATABASE_URL é composta a
    # partir de POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB e injetada
    # como variável de ambiente do container backend.
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Demais variáveis já usadas pelo projeto.
    VIACEP_BASE_URL: str = "https://viacep.com.br/ws"
    STORAGE_PATH: str = "/app/storage"

    # CORS. O frontend privado chama a API direto do navegador
    # (NEXT_PUBLIC_API_URL), por isso precisa estar liberado aqui.
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()  # type: ignore[call-arg]
