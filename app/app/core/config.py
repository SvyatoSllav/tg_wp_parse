import enum
from typing import Any, Dict, List, Optional, Union
import json

from pydantic import BaseSettings, PostgresDsn, validator


class EnvEnum(enum.Enum):
    development = 'development'
    production = 'production'
    test = 'test'


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"   

    ASYNC_SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SYNC_SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("ASYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    @validator("SYNC_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_sync_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    REDIS_PORT:str
    REDIS_HOST: str
    REDIS_DB_BOT: str = "REDIS_DB_BOT"

    ROLLBAR_TOKEN: str
    PYTHON_ENV: EnvEnum = EnvEnum.development

    SERVER_IP: str

    class Config:
        case_sensitive = True


settings = Settings()
