"""Purpose: produce deterministic repository intelligence.
Inputs: parsed files and scanner outputs.
Outputs: analysis sections used by reports and API responses.
"""

from collections import Counter

from backend.parsers.repository import RepoFile
from backend.scanners.dependencies import DependencyResult
from backend.scanners.security import SecurityFinding


def understand_business(files: list[RepoFile]) -> str:
    readme = next((file for file in files if file.path.lower().endswith("readme.md")), None)
    if readme:
        first_lines = [line.strip("# ").strip() for line in readme.content.splitlines() if line.strip()]
        if first_lines:
            return " ".join(first_lines[:3])[:600]
    names = ", ".join(file.path for file in files[:8])
    return f"Business purpose could not be confirmed from documentation. Key files include: {names}."


def analyze_architecture(files: list[RepoFile]) -> str:
    top_dirs = Counter(file.path.split("/", 1)[0] for file in files if "/" in file.path)
    categories = Counter(file.category for file in files)
    if not top_dirs:
        return "Repository has a flat structure. Consider grouping source, tests, and documentation."
    dirs = ", ".join(name for name, _ in top_dirs.most_common(8))
    return f"Primary folders: {dirs}. File mix: {dict(categories)}."


def evaluate_code_quality(files: list[RepoFile]) -> list[str]:
    notes: list[str] = []
    large_files = [file.path for file in files if len(file.content.splitlines()) > 500]
    if large_files:
        notes.append(f"Large files may need decomposition: {', '.join(large_files[:5])}.")
    tests = [file for file in files if "test" in file.path.lower() or "spec" in file.path.lower()]
    if not tests:
        notes.append("No test files detected in scanned files.")
    docs = [file for file in files if file.category == "documentation"]
    if not docs:
        notes.append("No documentation files detected.")
    return notes or ["Code organization looks reasonable from the scanned files."]


def find_missing_requirements(files: list[RepoFile], dependencies: DependencyResult) -> list[str]:
    missing: list[str] = []
    lower_paths = {file.path.lower() for file in files}
    if "readme.md" not in lower_paths:
        missing.append("README.md is missing.")
    if not any("test" in path or "spec" in path for path in lower_paths):
        missing.append("Automated tests are missing or outside scan depth.")
    if dependencies.issues:
        missing.append("Dependency hygiene needs review.")
    return missing or ["No obvious missing requirements found from static analysis."]


def build_recommendations(security: list[SecurityFinding], dependencies: DependencyResult, quality: list[str]) -> list[str]:
    recommendations: list[str] = []
    if security:
        recommendations.append("Resolve high and medium security findings before release.")
    if dependencies.issues:
        recommendations.append("Pin dependencies and review lockfiles with a vulnerability scanner.")
    if any("test" in note.lower() for note in quality):
        recommendations.append("Add focused tests for core behavior and security-sensitive paths.")
    return recommendations or ["Continue regular dependency, security, and architecture reviews."]
