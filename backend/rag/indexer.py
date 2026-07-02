"""Purpose: create a local Chroma text index for repository search.
Inputs: parsed files and chunk settings.
Outputs: vector store path and a JSON fallback when Chroma is unavailable.
"""

from pathlib import Path
import json

from backend.parsers.repository import RepoFile


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    step = max(1, chunk_size - overlap)
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return chunks


def build_local_index(
    files: list[RepoFile],
    vector_dir: Path,
    chunk_size: int,
    overlap: int,
    collection_name: str = "repomind",
) -> Path:
    vector_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for repo_file in files:
        for index, chunk in enumerate(chunk_text(repo_file.content, chunk_size, overlap)):
            records.append({"file": repo_file.path, "chunk": index, "text": chunk})

    if _write_chroma(records, vector_dir, collection_name):
        return vector_dir

    output = vector_dir / "repo_index.json"
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return output


def _write_chroma(records: list[dict], vector_dir: Path, collection_name: str) -> bool:
    try:
        import chromadb
    except ImportError:
        return False

    try:
        client = chromadb.PersistentClient(path=str(vector_dir))
    except Exception:
        return False

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    try:
        collection = client.get_or_create_collection(collection_name)
        if not records:
            return True

        collection.add(
            ids=[f"{record['file']}::{record['chunk']}" for record in records],
            documents=[record["text"] for record in records],
            metadatas=[{"file": record["file"], "chunk": record["chunk"]} for record in records],
        )
        return True
    except Exception:
        return False
