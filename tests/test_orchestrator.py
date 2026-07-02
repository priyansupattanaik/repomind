from backend.agents.orchestrator import scan_local_repository
from backend.config import Settings
from pathlib import Path


def test_scan_local_repository_generates_report(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Useful API\nHelps teams inspect code.", encoding="utf-8")
    (repo / "requirements.txt").write_text("fastapi==0.1.0", encoding="utf-8")

    settings = Settings(
        openrouter_api_key="",
        model_name="test-model",
        embed_model="test-embed",
        max_files=20,
        max_file_size=10000,
        chunk_size=100,
        chunk_overlap=10,
        scan_depth=4,
        report_dir=tmp_path / "reports",
        cache_dir=tmp_path / "cache",
        vector_dir=tmp_path / "vectors",
        vector_collection="test",
        cors_origins=["*"],
        frontend_port=3000,
        backend_port=8000,
        debug=True,
    )

    report = scan_local_repository("https://github.com/example/repo", repo, settings)

    assert report["file_count"] == 2
    assert (tmp_path / "reports" / "example__repo.md").exists()
    assert Path(report["index_path"]).exists()
