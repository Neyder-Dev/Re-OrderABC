from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://gastro:gastro123@localhost:5432/reordena_abc"
    SECRET_KEY: str = "cambia-esto-en-produccion"
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()