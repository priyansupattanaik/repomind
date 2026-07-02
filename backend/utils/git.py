"""Purpose: clone public Git repositories into a local cache.
Inputs: repository URL, cache directory.
Outputs: local repository path.
"""

from pathlib import Path
from urllib.parse import urlparse
import hashlib
import shutil
import subprocess


def validate_github_url(repo_url: str) -> str:
    parsed = urlparse(repo_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Repository URL must use http or https.")
    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only github.com repository URLs are supported.")
    if len([part for part in parsed.path.split("/") if part]) < 2:
        raise ValueError("Repository URL must include owner and repository name.")
    return repo_url.rstrip("/")


def clone_repository(repo_url: str, cache_dir: Path) -> Path:
    valid_url = validate_github_url(repo_url)
    cache_dir.mkdir(parents=True, exist_ok=True)
    repo_id = hashlib.sha256(valid_url.encode("utf-8")).hexdigest()[:16]
    target = cache_dir / repo_id

    if target.exists():
        shutil.rmtree(target)

    result = subprocess.run(
        ["git", "clone", "--depth", "1", valid_url, str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "git clone failed"
        raise RuntimeError(message)
    return target
