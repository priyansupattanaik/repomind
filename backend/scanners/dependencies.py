"""Purpose: summarize dependencies from common manifest files.
Inputs: parsed repository files.
Outputs: dependency issues and package names.
"""

from dataclasses import dataclass
import json
import re

from backend.parsers.repository import RepoFile


@dataclass(frozen=True)
class DependencyResult:
    packages: list[str]
    versions: dict[str, str]
    issues: list[str]


def analyze_dependencies(files: list[RepoFile]) -> DependencyResult:
    packages: list[str] = []
    versions: dict[str, str] = {}
    issues: list[str] = []

    for repo_file in files:
        name = repo_file.path.lower().split("/")[-1]
        if name == "package.json":
            _read_package_json(repo_file.content, packages, versions, issues)
        elif name == "requirements.txt":
            _read_requirements(repo_file.content, packages, versions, issues)
        elif name == "pyproject.toml":
            issues.append(f"{repo_file.path}: pyproject.toml detected; lockfile review recommended.")

    if not packages:
        issues.append("No supported dependency manifest found.")

    return DependencyResult(packages=sorted(set(packages)), versions=versions, issues=issues)


def _read_package_json(content: str, packages: list[str], versions: dict[str, str], issues: list[str]) -> None:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        issues.append("package.json is not valid JSON.")
        return
    for section in ("dependencies", "devDependencies"):
        dependencies = data.get(section, {})
        if isinstance(dependencies, dict):
            for package, version in dependencies.items():
                packages.append(package)
                if isinstance(version, str):
                    versions[package] = version
                if isinstance(version, str) and version in {"*", "latest"}:
                    issues.append(f"{package} uses an unpinned version ({version}).")


def _read_requirements(content: str, packages: list[str], versions: dict[str, str], issues: list[str]) -> None:
    for line in content.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        package = re.split(r"[<>=~!]", clean, maxsplit=1)[0].strip()
        packages.append(package)
        version_match = re.search(r"(==|~=|>=|<=|>|<|!=)\s*(.+)$", clean)
        if version_match:
            versions[package] = f"{version_match.group(1)}{version_match.group(2).strip()}"
        if "==" not in clean:
            issues.append(f"{package} is not pinned with == in requirements.txt.")
