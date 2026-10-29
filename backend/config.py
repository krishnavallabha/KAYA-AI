from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "FlowSense Backend"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./flowsense.db"

    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""  # Temporary compatibility; remove after migration.


settings = Settings()
