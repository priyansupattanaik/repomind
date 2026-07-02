from backend.parsers.repository import RepoFile
from backend.scanners.security import scan_security


def test_security_scan_finds_eval():
    files = [RepoFile("app.py", ".py", 12, "eval(user_input)", "source")]
    findings = scan_security(files)
    assert findings
    assert findings[0].title == "Use of eval"
