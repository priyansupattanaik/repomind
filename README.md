# RepoMind AI

RepoMind AI is a local-first repository intelligence tool. It accepts a GitHub repository URL, clones the repository, scans the code, detects common security risks, summarizes dependencies, reviews architecture, creates a local retrieval index, writes a Markdown report, and shows the results in a minimal web dashboard.

## Setup

Fill in your OpenRouter key in `.env`.

```bash
OPENROUTER_API_KEY=your_openrouter_key
```

The scanner works without API keys for deterministic static analysis. LiteLLM is available for future AI summaries when `OPENROUTER_API_KEY` is configured.

## Installation

Backend:

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional AI/vector integrations:

```bash
pip install -r requirements-ai.txt
```

Frontend:

```bash
cd frontend
npm install
```

## Environment Variables

- `OPENROUTER_API_KEY`: optional OpenRouter provider key.
- `MODEL_NAME`: LiteLLM model name.
- `EMBED_MODEL`: embedding model name.
- `MAX_FILES`: maximum files scanned per repository.
- `MAX_FILE_SIZE`: maximum size for a single scanned file.
- `CHUNK_SIZE`, `CHUNK_OVERLAP`: local retrieval chunk settings.
- `SCAN_DEPTH`: maximum folder depth scanned.
- `REPORT_DIR`, `CACHE_DIR`, `VECTOR_DIR`: local storage paths.
- `VECTOR_COLLECTION`: Chroma collection name.
- `CORS_ORIGINS`: comma-separated backend CORS origins.
- `FRONTEND_PORT`, `BACKEND_PORT`: local server ports.
- `DEBUG`: enables development behavior.
- `NEXT_PUBLIC_BACKEND_URL`: frontend API base URL.

## Running Backend

```bash
python -m uvicorn backend.api.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Running Frontend

```bash
cd frontend
npm run dev -- --port 3000
```

Open `http://localhost:3000`.

## Running Scans

Use the dashboard form or call the API directly:

```bash
curl -X POST http://localhost:8000/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"repo_url\":\"https://github.com/owner/repo\"}"
```

Reports are written to `REPORT_DIR`. Repositories are cloned into `CACHE_DIR`. Retrieval data is stored under `VECTOR_DIR` using Chroma when `requirements-ai.txt` is installed, otherwise a JSON fallback index is written.

## Understanding Reports

Each report contains:

1. Executive summary
2. Technology stack
3. Security issues
4. Dependency issues
5. Architecture review
6. Business intent
7. Code quality
8. Recommendations

Security findings are static rule matches, not a replacement for tools such as Semgrep, CodeQL, Dependabot, or npm audit. Dependency analysis focuses on manifest hygiene and should be paired with ecosystem-specific vulnerability scanners.
