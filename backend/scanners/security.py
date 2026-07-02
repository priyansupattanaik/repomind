"""Purpose: detect common insecure code patterns.
Inputs: parsed repository files.
Outputs: security findings with severity and remediation.
"""

from dataclasses import dataclass
import re

from backend.parsers.repository import RepoFile


@dataclass(frozen=True)
class SecurityFinding:
    severity: str
    file: str
    line: int
    title: str
    detail: str
    recommendation: str


RULES = [
    ("high", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{8,}"), "Possible hardcoded secret"),
    ("high", re.compile(r"(?i)\beval\s*\("), "Use of eval"),
    ("medium", re.compile(r"(?i)verify\s*=\s*false"), "TLS verification disabled"),
    ("medium", re.compile(r"(?i)subprocess\.(run|call|popen).*shell\s*=\s*true"), "Shell execution enabled"),
    ("low", re.compile(r"(?i)todo|fixme"), "Open TODO or FIXME"),
]


def scan_security(files: list[RepoFile]) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for repo_file in files:
        for line_number, line in enumerate(repo_file.content.splitlines(), start=1):
            for severity, pattern, title in RULES:
                if pattern.search(line):
                    findings.append(
                        SecurityFinding(
                            severity=severity,
                            file=repo_file.path,
                            line=line_number,
                            title=title,
                            detail=line.strip()[:180],
                            recommendation="Review the code path and replace risky patterns with safer alternatives.",
                        )
                    )
    return findings
