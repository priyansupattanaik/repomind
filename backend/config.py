"""Purpose: load RepoMind settings from environment variables.
Inputs: process environment and optional .env file.
Outputs: a Settings object used by the backend modules.
"""

from dataclasses import dataclass
from pathlib import Path
import os


def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        key, value = clean.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    model_name: str
    embed_model: str
    max_files: int
    max_file_size: int
    chunk_size: int
    chunk_overlap: int
    scan_depth: int
    report_dir: Path
    cache_dir: Path
    vector_dir: Path
    vector_collection: str
    cors_origins: list[str]
    frontend_port: int
    backend_port: int
    debug: bool


def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        model_name=os.getenv("MODEL_NAME", "openrouter/google/gemini-2.5-flash"),
        embed_model=os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5"),
        max_files=_int_env("MAX_FILES", 300),
        max_file_size=_int_env("MAX_FILE_SIZE", 2_000_000),
        chunk_size=_int_env("CHUNK_SIZE", 800),
        chunk_overlap=_int_env("CHUNK_OVERLAP", 100),
        scan_depth=_int_env("SCAN_DEPTH", 8),
        report_dir=Path(os.getenv("REPORT_DIR", "reports")),
        cache_dir=Path(os.getenv("CACHE_DIR", "cache")),
        vector_dir=Path(os.getenv("VECTOR_DIR", "vectors")),
        vector_collection=os.getenv("VECTOR_COLLECTION", "repomind"),
        cors_origins=[
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ],
        frontend_port=_int_env("FRONTEND_PORT", 3000),
        backend_port=_int_env("BACKEND_PORT", 8000),
        debug=_bool_env("DEBUG", True),
    )
