"""Purpose: expose RepoMind scanning APIs.
Inputs: HTTP requests with GitHub repository URLs.
Outputs: JSON scan results and health status.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from backend.agents.orchestrator import scan_repository
from backend.config import get_settings


class ScanRequest(BaseModel):
    repo_url: HttpUrl


settings = get_settings()
app = FastAPI(title="RepoMind AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/scan")
def scan(request: ScanRequest) -> dict:
    try:
        return scan_repository(str(request.repo_url), get_settings())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Repository could not be cloned. {exc}") from exc
