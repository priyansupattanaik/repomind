from backend.parsers.repository import classify_file, parse_repository


def test_parse_repository_reads_text_files(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "skip.js").write_text("x", encoding="utf-8")

    files = parse_repository(tmp_path, max_files=10, max_file_size=1000, scan_depth=4)

    assert len(files) == 1
    assert files[0].path == "README.md"
    assert files[0].category == "documentation"


def test_classify_dependency_file(tmp_path):
    path = tmp_path / "package.json"
    path.write_text("{}", encoding="utf-8")
    assert classify_file(path) == "dependency"


def test_parse_repository_strips_utf8_bom(tmp_path):
    (tmp_path / "package.json").write_text('\ufeff{"dependencies": {}}', encoding="utf-8")

    files = parse_repository(tmp_path, max_files=10, max_file_size=1000, scan_depth=4)

    assert files[0].content.startswith("{")
