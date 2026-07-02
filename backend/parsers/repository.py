"""Purpose: read repository files for analysis.
Inputs: local repository path and scan limits.
Outputs: RepoFile records with relative paths and text content.
"""

from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", ".next", "__pycache__", "dist", "build", ".venv", "venv"}
TEXT_EXTENSIONS = {
    ".go", ".js", ".jsx", ".ts", ".tsx", ".py", ".rb", ".rs", ".java", ".kt",
    ".php", ".cs", ".c", ".cpp", ".h", ".hpp", ".json", ".toml", ".yaml",
    ".yml", ".md", ".txt", ".html", ".css", ".scss", ".sql", ".sh", ".ps1",
    ".lock", ".env.example",
}


@dataclass(frozen=True)
class RepoFile:
    path: str
    extension: str
    size: int
    content: str
    category: str


def classify_file(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if name in {"package.json", "requirements.txt", "pyproject.toml", "pom.xml", "go.mod"}:
        return "dependency"
    if suffix in {".md", ".txt"}:
        return "documentation"
    if suffix in {".json", ".toml", ".yaml", ".yml", ".env.example"}:
        return "configuration"
    if suffix in TEXT_EXTENSIONS:
        return "source"
    return "other"


def parse_repository(root: Path, max_files: int, max_file_size: int, scan_depth: int) -> list[RepoFile]:
    files: list[RepoFile] = []
    for path in root.rglob("*"):
        if len(files) >= max_files:
            break
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if len(relative_parts) > scan_depth:
            continue
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name.lower() not in TEXT_EXTENSIONS:
            continue
        size = path.stat().st_size
        if size > max_file_size:
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        files.append(
            RepoFile(
                path=str(path.relative_to(root)).replace("\\", "/"),
                extension=path.suffix.lower(),
                size=size,
                content=content,
                category=classify_file(path),
            )
        )
    return files
