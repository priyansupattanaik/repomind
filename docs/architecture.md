# Architecture

RepoMind uses a small local pipeline:

1. The FastAPI endpoint accepts a GitHub URL.
2. `backend/utils/git.py` validates and clones the repository.
3. `backend/parsers/repository.py` reads text files within configured limits.
4. `backend/scanners/security.py` checks common risky patterns.
5. `backend/scanners/dependencies.py` summarizes supported manifests.
6. `backend/agents/orchestrator.py` runs analysis through a LangGraph hook when available.
7. `backend/rag/indexer.py` writes a local Chroma index when Chroma is installed.
8. `backend/reports/generator.py` writes a Markdown report.
9. The Next.js dashboard calls `/scan` and renders the returned report.

The code intentionally favors plain functions, direct data flow, and readable files over framework-heavy abstractions.
