from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    cdp_endpoint: str = "http://127.0.0.1:9222"
    log_file: str = "parser.log"
    results_file: str = "results.txt"
    default_pause_min: float = 1.5
    default_pause_max: float = 4.5
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорировать дополнительные поля в .env

settings = Settings()
