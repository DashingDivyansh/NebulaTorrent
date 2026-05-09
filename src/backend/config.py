import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    APP_NAME: str = "NebulaTorrent API"
    DEBUG: bool = False
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # Security
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"] # Restrict in prod
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PLUGINS_DIR: str = os.path.join(BASE_DIR, "src", "backend", "plugins")
    DB_PATH: str = os.path.join(BASE_DIR, "nebula.db")
    
    # Timeouts
    SEARCH_TIMEOUT: float = 25.0
    PLUGIN_TIMEOUT: float = 12.0
    HEARTBEAT_INTERVAL: float = 5.0
    CACHE_TTL_SECONDS: int = 900
    CIRCUIT_BREAKER_FAILURES: int = 3
    CIRCUIT_BREAKER_COOLDOWN_SECONDS: int = 300
    PLUGIN_RETRIES: int = 2
    PLUGIN_RETRY_BASE_DELAY: float = 0.35
    PLUGIN_DEFAULT_RATE_LIMIT: int = 1
    PLUGIN_SANDBOX_ENABLED: bool = True
    PLUGIN_SANDBOX_PROCESS_GRACE_SECONDS: float = 2.0
    PLUGIN_SANDBOX_MAX_RESULTS: int = 500

    # Proxy
    PROXY_URL: Optional[str] = None
    PROXY_FALLBACK: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
