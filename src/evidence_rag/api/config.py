"""Configuration settings for CMO Agent Path B API Service."""
import os
from pathlib import Path
from pydantic import BaseModel, Field

from evidence_rag.config import REPO_ROOT


class APISettings(BaseModel):
    """Runtime settings for Path B microservice."""
    api_title: str = "CMO Agent - Evidence Grounded Decision Intelligence (Path B)"
    api_version: str = "2.0.0"
    api_host: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8001")))
    masterdb_url: str = Field(default_factory=lambda: os.getenv("MASTERDB_URL", "http://127.0.0.1:8000"))
    masterdb_app_id: str = Field(default_factory=lambda: os.getenv("MASTERDB_APP_ID", "CMO_AGENT"))
    masterdb_capability_id: str = Field(
        default_factory=lambda: os.getenv("MASTERDB_CAPABILITY_ID", "cap-cmo-marketing-intelligence")
    )
    auth_enabled: bool = Field(
        default_factory=lambda: os.getenv("API_AUTH_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    auth_strict_rs256: bool = Field(
        default_factory=lambda: os.getenv("AUTH_STRICT_RS256", "false").lower() in ("true", "1", "yes")
    )
    base_dir: Path = REPO_ROOT


api_settings = APISettings()
