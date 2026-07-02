from backend.parsers.repository import RepoFile
from backend.scanners.dependencies import analyze_dependencies


def test_dependency_scan_flags_unpinned_requirements():
    files = [RepoFile("requirements.txt", ".txt", 10, "fastapi\npytest==8.0.0", "dependency")]
    result = analyze_dependencies(files)
    assert "fastapi" in result.packages
    assert result.versions["pytest"] == "==8.0.0"
    assert any("not pinned" in issue for issue in result.issues)
