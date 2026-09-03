import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./loomiq.db"
    
    # LLM Settings
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
