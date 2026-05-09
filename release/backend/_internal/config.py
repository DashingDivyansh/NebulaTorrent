import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "NebulaTorrent API"
    DEBUG: bool = False
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # Security
    CORS_ORIGINS: list[str] = ["http://localhost:5173"] # Restrict in prod
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PLUGINS_DIR: str = os.path.join(BASE_DIR, "src", "backend", "plugins")
    DB_PATH: str = os.path.join(BASE_DIR, "nebula.db")
    
    # Timeouts
    SEARCH_TIMEOUT: float = 15.0
    HEARTBEAT_INTERVAL: float = 5.0

    class Config:
        env_file = ".env"

settings = Settings()
