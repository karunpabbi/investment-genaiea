from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="GenAI Startup Analyst")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    google_project_id: str | None = Field(default=None, validation_alias="GOOGLE_PROJECT_ID")
    google_location: str = Field(default="us-central1", validation_alias="GOOGLE_LOCATION")
    vertex_model: str = Field(default="gemini-1.5-pro", validation_alias="VERTEX_MODEL")
    bigquery_dataset: str | None = Field(default=None, validation_alias="BIGQUERY_DATASET")
    firebase_storage_bucket: str | None = Field(default=None, validation_alias="FIREBASE_STORAGE_BUCKET")

    enable_google_services: bool = Field(default=True, validation_alias="ENABLE_GOOGLE_SERVICES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
