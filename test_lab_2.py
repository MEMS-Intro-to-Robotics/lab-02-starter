#!/usr/bin/env python3
"""Automated submission checks for Lab 2: ROS 2 CLI Fundamentals.

Run from the repository root with ``pytest -v``. These tests check objective
submission requirements. Human graders evaluate the ROS 2 evidence and the
quality of the reasoning in ``ros2_cli_record.md``.
"""

from __future__ import annotations

from pathlib import Path
import re
import struct
import subprocess


REPO_ROOT = Path(__file__).resolve().parent

EXPECTED_SCREENSHOTS = (
    "baseline_graph.png",
    "independent_graph.png",
    "independent_result.png",
)

REQUIRED_RECORD_TEXT = (
    "# ROS 2 CLI Investigation Record",
    "## Known-Good Baseline",
    "Nodes observed:",
    "Topic and message type:",
    "Publisher/subscriber relationship:",
    "## Independent System Contract",
    "Chosen simulator node name:",
    "Chosen second turtle name and spawn pose:",
    "Chosen background RGB values:",
    "Chosen velocity command:",
    "Prediction before publishing the velocity command:",
    "## Inspection Evidence",
    "Commands used to identify nodes:",
    "Commands used to identify the command topic and message type:",
    "Commands used to identify the spawn service and service type:",
    "Commands used to inspect parameters:",
    "Relevant output from your run:",
    "## Validation",
    "What changed in the simulator:",
    "Graph interpretation:",
    "Prediction compared with observation:",
    "Why a topic, service, and parameter were appropriate for their respective jobs:",
    "## Recovery",
    "Mismatch encountered and diagnosis, or a likely mismatch and the first CLI",
)

STARTER_MARKERS = (
    "[Your Name]",
    "Replace this paragraph",
    "YOUR_NETID",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def check_required_files(repo: Path) -> list[str]:
    errors: list[str] = []
    required = (
        "README.md",
        ".gitignore",
        "ros2_cli_record.md",
        "test_lab_2.py",
    )
    for relative in required:
        path = repo / relative
        if not path.is_file():
            errors.append(f"Missing required file: {relative}")
        elif path.stat().st_size == 0:
            errors.append(f"Required file is empty: {relative}")

    docs = repo / "docs"
    if not docs.is_dir():
        errors.append("Missing required directory: docs/")
        return errors

    for filename in EXPECTED_SCREENSHOTS:
        path = docs / filename
        if not path.is_file():
            errors.append(f"Missing required screenshot: docs/{filename}")
            continue
        dimensions = _png_dimensions(path)
        if dimensions is None or dimensions[0] < 1 or dimensions[1] < 1:
            errors.append(f"docs/{filename} is not a valid PNG image")
    return errors


def check_readme_and_record(repo: Path) -> list[str]:
    errors: list[str] = []
    readme_path = repo / "README.md"
    if readme_path.is_file():
        readme = _read_text(readme_path)
        for marker in STARTER_MARKERS:
            if marker in readme:
                errors.append(f"README.md still contains starter text: {marker}")

    record_path = repo / "ros2_cli_record.md"
    if record_path.is_file():
        record = _read_text(record_path)
        missing = [item for item in REQUIRED_RECORD_TEXT if item not in record]
        if missing:
            errors.append(
                "ros2_cli_record.md is missing required headings or prompts: "
                + ", ".join(missing)
            )
        if len(re.findall(r"\b[\w'-]+\b", record)) < 300:
            errors.append(
                "ros2_cli_record.md needs more run-specific evidence and explanation"
            )
        if re.search(r"\b(?:TODO|TBD|YOUR_[A-Z_]+)\b", record):
            errors.append("ros2_cli_record.md still contains an unanswered placeholder")
    return errors


def check_repository_hygiene(repo: Path) -> list[str]:
    if not (repo / ".git").exists():
        return ["Run the grading script inside the cloned Git repository; .git is missing"]

    result = _run_git(repo, "ls-files")
    if result.returncode != 0:
        return ["Could not inspect tracked files with 'git ls-files'"]

    forbidden_names = {"__pycache__", ".pytest_cache", ".DS_Store", "Thumbs.db"}
    tracked = [Path(line) for line in result.stdout.splitlines() if line]
    prohibited = [
        path.as_posix()
        for path in tracked
        if set(path.parts) & forbidden_names or path.suffix in {".pyc", ".pyo"}
    ]
    if prohibited:
        return ["Generated artifacts are tracked: " + ", ".join(prohibited)]
    return []


def _assert_no_errors(errors: list[str]) -> None:
    assert not errors, "\n- " + "\n- ".join(errors)


def test_required_files_and_screenshots() -> None:
    _assert_no_errors(check_required_files(REPO_ROOT))


def test_readme_and_investigation_record() -> None:
    _assert_no_errors(check_readme_and_record(REPO_ROOT))


def test_repository_hygiene() -> None:
    _assert_no_errors(check_repository_hygiene(REPO_ROOT))
