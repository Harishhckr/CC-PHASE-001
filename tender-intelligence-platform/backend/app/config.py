from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql://postgres:password@localhost:5432/tenderdb",
        env="DATABASE_URL",
    )
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    secret_key: str = Field("your-secure-secret-key-here", env="SECRET_KEY")
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    gem_max_pages: int = Field(20, env="GEM_MAX_PAGES")
    tender247_max_pages: int = Field(10, env="TENDER247_MAX_PAGES")
    tendertiger_max_pages: int = Field(10, env="TENDERTIGER_MAX_PAGES")

    mdm_keywords: List[str] = [
        "master data management",
        "material codification",
        "data governance",
        "data cleansing",
        "data enrichment",
        "cataloguing",
        "data standardization",
        "vendor data governance",
        "material master",
        "asset master",
        "service master",
        "bill of material",
        "bom",
        "maximo",
        "estring",
        "spares",
        "materials",
        "services",
    ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
