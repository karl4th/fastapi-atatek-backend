from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    APP_VERSION: str = os.getenv('APP_VERSION', '3.0.0')
    # По умолчанию используем локальные настройки из docker-compose (порт проброшен 5432:5432)
    DB_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    DB_USER: str = os.getenv('POSTGRES_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'postgres')
    DB_NAME: str = os.getenv('POSTGRES_DB', 'postgres')

    REDIS_HOST: str = os.getenv('REDIS_HOST', 'test')

    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'secret_key')
    


    @property
    def get_base_link(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"
    
    @property
    def get_base_link_for_alembic(self):
        # Используем синхронный драйвер для Alembic, чтобы не требовался event loop
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"
    
    @property
    def get_redis_host(self):
        return f"{self.REDIS_HOST}"

    

settings = Settings()
    