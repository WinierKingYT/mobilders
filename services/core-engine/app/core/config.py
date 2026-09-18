"""
Core Engine Configuration Loader.
Loads production settings from .env file with zero-PII security guarantees.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import List


class Settings:
    def __init__(self):
        # Determine .env path
        base_dir = Path(__file__).resolve().parent.parent.parent
        env_file = base_dir / ".env"
        if env_file.exists():
            self._load_env_file(env_file)

        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "ple_default_secret_key_change_in_production")
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.PORT: int = int(os.getenv("PORT", "8000"))

        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "postgresql://ple_user:ple_password@127.0.0.1:5432/ple_db"
        )
        self.REDIS_URL: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

        # Focus V1 Alpha remains default-off until explicitly enabled.
        self.FOCUS_V1_ENABLED: bool = (
            os.getenv("FOCUS_V1_ENABLED", "false").strip().lower() == "true"
        )
        # Canary routing percentage (0..100). If 0, only FOCUS_V1_ENABLED governs access.
        self.FOCUS_CANARY_PERCENTAGE: int = int(os.getenv("FOCUS_CANARY_PERCENTAGE", "0"))
        # Emergency kill switch: if true, immediately shuts off Focus V1 routes regardless of canary.
        self.FOCUS_KILL_SWITCH: bool = (
            os.getenv("FOCUS_KILL_SWITCH", "false").strip().lower() == "true"
        )

        # Parse CORS Origins list
        cors_raw = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:8000,http://10.0.2.2:8000,app://ple.local",
        )
        self.CORS_ORIGINS: List[str] = [orig.strip() for orig in cors_raw.split(",") if orig.strip()]

        self.WS_RATE_LIMIT: int = int(os.getenv("WS_RATE_LIMIT", "2"))
        self.CAS_TIMEOUT_MS: int = int(os.getenv("CAS_TIMEOUT_MS", "500"))
        self.MAX_AST_DEPTH: int = int(os.getenv("MAX_AST_DEPTH", "15"))
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def _load_env_file(self, filepath: Path) -> None:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    # Set into os.environ if not already present
                    if key not in os.environ:
                        os.environ[key] = val
        except Exception:
            pass


settings = Settings()
