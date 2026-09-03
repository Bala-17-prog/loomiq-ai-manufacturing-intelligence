import os
from pydantic_settings import BaseSettings
from typing import Optional

import shutil

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ORIGINAL_DB_PATH = os.path.join(BASE_DIR, 'loomiq.db')

if os.getenv("VERCEL") == "1":
    DB_PATH = "/tmp/loomiq.db"
    if not os.path.exists(DB_PATH) and os.path.exists(ORIGINAL_DB_PATH):
        try:
            shutil.copy2(ORIGINAL_DB_PATH, DB_PATH)
        except OSError:
            pass
else:
    DB_PATH = ORIGINAL_DB_PATH

class Settings(BaseSettings):
    app_env: str = "development"
    # Ensure robust absolute path for Vercel serverless functions
    database_url: str = f"sqlite:///{DB_PATH}"
    
    # LLM Settings
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
