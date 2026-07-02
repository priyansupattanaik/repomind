"""Purpose: run the full RepoMind analysis pipeline.
Inputs: GitHub repository URL.
Outputs: scan report dictionary and Markdown report path.
"""

from pathlib import Path
import time

from backend.agents.analyzer import (
    analyze_architecture,
    build_recommendations,
    evaluate_code_quality,
    find_missing_requirements,
    understand_business,
)
from backend.agents.graph import run_graph
from backend.config import Settings
from backend.parsers.repository import parse_repository
from backend.rag.indexer import build_local_index
from backend.reports.generator import write_report
from backend.scanners.dependencies import analyze_dependencies
from backend.scanners.security import scan_security
from backend.utils.git import clone_repository


def scan_repository(repo_url: str, settings: Settings) -> dict:
    repo_path = clone_repository(repo_url, settings.cache_dir)
    return scan_local_repository(repo_url, repo_path, settings)


def scan_local_repository(repo_url: str, repo_path: Path, settings: Settings) -> dict:
    return run_graph(
        {"repo_url": repo_url, "repo_path": repo_path, "settings": settings},
        _analyze_repository_state,
    )


def _analyze_repository_state(state: dict) -> dict:
    repo_url = state["repo_url"]
    repo_path = state["repo_path"]
    settings = state["settings"]
    scan_started = time.perf_counter()
    parse_started = time.perf_counter()
    files = parse_repository(repo_path, settings.max_files, settings.max_file_size, settings.scan_depth)
    parse_seconds = time.perf_counter() - parse_started
    analysis_started = time.perf_counter()
    security = scan_security(files)
    dependencies = analyze_dependencies(files)
    business = understand_business(files)
    architecture = analyze_architecture(files)
    quality = evaluate_code_quality(files)
    missing = find_missing_requirements(files, dependencies)
    recommendations = build_recommendations(security, dependencies, quality)
    analysis_seconds = time.perf_counter() - analysis_started
    index_started = time.perf_counter()
    index_path = build_local_index(
        files,
        settings.vector_dir,
        settings.chunk_size,
        settings.chunk_overlap,
        settings.vector_collection,
    )
    index_seconds = time.perf_counter() - index_started

    report = {
        "repository": repo_url,
        "file_count": len(files),
        "technology_stack": sorted({file.extension.lstrip(".") for file in files if file.extension}),
        "executive_summary": f"Scanned {len(files)} files. Found {len(security)} security findings and {len(dependencies.issues)} dependency notes.",
        "security_issues": [finding.__dict__ for finding in security],
        "dependency_packages": dependencies.packages,
        "dependency_versions": dependencies.versions,
        "dependency_issues": dependencies.issues,
        "architecture_review": architecture,
        "business_intent": business,
        "code_quality": quality,
        "missing_requirements": missing,
        "recommendations": recommendations,
        "index_path": str(index_path),
        "timings": {
            "parse_seconds": round(parse_seconds, 3),
            "analysis_seconds": round(analysis_seconds, 3),
            "index_seconds": round(index_seconds, 3),
        },
    }
    report_started = time.perf_counter()
    report_path = write_report(report, settings.report_dir)
    report["timings"]["report_seconds"] = round(time.perf_counter() - report_started, 3)
    report["scan_duration_seconds"] = round(time.perf_counter() - scan_started, 3)
    report_path = write_report(report, settings.report_dir)
    report["report_path"] = str(report_path)
    return report
