from pydantic import BaseModel

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


# Загрузка переменных окружения из файла .env
load_dotenv()


class DatabaseConfig(BaseModel):
    url: str


class AdmConfig(BaseModel):
    tg_id: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    db: DatabaseConfig
    su: AdmConfig
    channel__link: int


settings = Settings()
