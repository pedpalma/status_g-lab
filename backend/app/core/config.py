"""
Configurações da aplicação.
Centraliza a leitura de variáveis de ambiente em um único objeto tipado.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Banco de dados
    database_url: str

    # Autenticação
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Integração externa (backend/app/external/cep.py)
    viacep_base_url: str = "https://viacep.com.br/ws"

    # Armazenamento de imagens
    storage_path: str = "/app/storage"


settings = Settings()  # type: ignore[call-arg]
