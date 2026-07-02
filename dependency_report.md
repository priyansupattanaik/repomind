# Dependency Report

Generated: 2026-07-02

## Environment

- OS: Microsoft Windows NT 10.0.26200.0
- Default Python: 3.14.6 at `D:\Python\python.exe`
- Supported project Python: 3.11.9 at `C:\Users\ircpr\AppData\Local\Programs\Python\Python311\python.exe`
- Active project venv: `.venv`
- Project venv Python: 3.11.9
- Project venv pip: 24.0
- Node: v24.18.0
- npm: 11.4.0

## Root Cause

The original install path used Python 3.14.6. The pinned backend stack includes `pydantic==2.10.4`, which depends on `pydantic-core==2.27.2`.

On Python 3.14, pip did not find a compatible prebuilt `pydantic-core` wheel and attempted a Rust source build. That build failed because the bundled PyO3 version supports Python up to 3.13:

```text
the configured Python interpreter version (3.14) is newer than PyO3's maximum supported version (3.13)
```

This is a Python compatibility issue, not an application-code issue.

## Supported Python Version

Use Python 3.11 for this project.

Verified working:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Python 3.14 is not currently supported by the pinned dependency set.

## Requirements Split

`requirements.txt` is now the lightweight core install:

- `fastapi==0.115.6`
- `uvicorn==0.34.0`
- `pydantic==2.10.4`
- `pytest==8.3.4`
- `requests==2.32.3`

`requirements-ai.txt` contains optional AI/vector dependencies:

- `litellm==1.55.9`
- `langgraph==0.2.60`
- `chromadb==0.5.23`
- `sentence-transformers==3.3.1`

This keeps the normal backend install fast and avoids forcing heavy packages such as `torch`, `transformers`, and `tokenizers` into the default path.

## Installation Results

Clean rebuild:

- Removed old `.venv`, `.venv311`, pytest caches, and Python bytecode caches.
- Recreated `.venv` using Python 3.11.
- Repaired `ensurepip` under elevated permissions because Windows denied a file rename during venv bootstrap.
- Installed core requirements successfully.

Measured install times:

- Core install: 22.08 seconds.
- Optional AI install: 504.64 seconds.

The optional install is slow because it pulls large packages, including `torch`, `transformers`, `tokenizers`, `onnxruntime`, `scipy`, and `scikit-learn`.

## Wheel And Compatibility Notes

Core stack on Python 3.11:

- `pydantic-core==2.27.2`: prebuilt `cp311-win_amd64` wheel available.
- `fastapi`, `uvicorn`, `pytest`, `requests`: pure Python or wheel-backed install, no compiler required.

Optional stack on Python 3.11:

- `chroma-hnswlib==0.7.6`: prebuilt `cp311-win_amd64` wheel available.
- `torch==2.12.1`: prebuilt `cp311-win_amd64` wheel available.
- `tokenizers==0.20.3`: prebuilt Windows wheel available.
- `sentence-transformers==3.3.1`: installs successfully, but brings heavy ML transitive dependencies.

Python 3.14:

- Fails for the pinned Pydantic stack because `pydantic-core` falls back to source build and PyO3 rejects Python 3.14.

## Import Verification

Core imports passed:

```powershell
.\.venv\Scripts\python.exe -B -c "import fastapi, pydantic, uvicorn, requests"
```

Optional imports passed:

```powershell
.\.venv\Scripts\python.exe -B -c "import chromadb"
.\.venv\Scripts\python.exe -B -c "import torch"
.\.venv\Scripts\python.exe -B -c "import sentence_transformers"
.\.venv\Scripts\python.exe -B -c "import litellm, langgraph"
```

Note: `sentence_transformers` may use Hugging Face cache directories. If cache permissions are noisy, set `HF_HOME` to a writable local path.

## Test Results

Full test suite passed:

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests -p no:cacheprovider --basetemp=pytest_tmp_local
```

Result:

```text
7 passed, 1 warning
```

The warning is from `langgraph` deprecation messaging and does not fail the suite.

## Application Startup

Backend startup passed:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

Health check passed:

```text
GET /health -> 200 {"status":"ok"}
```

Frontend checks:

- `npx tsc --noEmit`: passed.
- `npm audit --omit=dev`: 0 vulnerabilities.
- `npm run build`: passed when run with normal process/file permissions.
- `npm run dev -- --hostname 127.0.0.1 --port 3000`: passed when run with normal process-spawn permissions.

The restricted sandbox produced `EPERM` errors for Next.js spawn and `.next` file rename operations. Elevated/normal execution resolved those errors, so they are environment permission issues rather than project dependency issues.

## Bugs Fixed During This Pass

- Split heavyweight optional dependencies into `requirements-ai.txt`.
- Reduced `requirements.txt` to the core runtime/test stack.
- Updated README installation instructions to use Python 3.11.
- Added generated local dependency/cache artifacts to `.gitignore`.
- Fixed Chroma runtime fallback so indexing falls back to JSON if Chroma is installed but fails during client/write operations.
- Updated orchestration test to accept either Chroma-backed index path or JSON fallback path.

## Recommended Setup

Use this exact flow:

```powershell
cd "D:\My Creations\Projects\repomind"

py -3.11 -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt
```

Optional:

```powershell
pip install -r requirements-ai.txt
```

Run backend:

```powershell
python -m uvicorn backend.api.main:app --reload --port 8000
```

Run frontend:

```powershell
cd frontend
npm install
npm run dev -- --port 3000
```

## Known Issues

- Do not use Python 3.14 with the current pins.
- Optional AI dependencies are large and slow to install.
- Next.js requires normal process-spawn and filesystem rename permissions; restricted shells may fail with `EPERM`.
- Hugging Face/Transformers cache should point to a writable directory if model imports are used heavily.

