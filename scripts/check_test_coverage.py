#!/usr/bin/env python3
"""Structural test coverage checker for klartext API.

Three invariants:
1. Every source file in models/services/repositories/routers has a test file.
2. Every router test file contains a health endpoint test (function with 'health' in name).
3. Every Supabase repository test file has at least one @pytest.mark.integration marker.

Exits with code 1 if any check fails. Used in CI (qa.yml).

Usage (from repo root):
    python scripts/check_test_coverage.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE_DIRS = ["models", "services", "repositories", "routers"]
EXCLUDED_FILES = {"__init__.py", "dependencies.py", "main.py", "cli.py", "seeddata.py"}


def check_test_files_exist(root: Path | None = None) -> list[str]:
    """Returns source files that have no corresponding test file.

    Checks every .py file in models/, services/, repositories/, routers/
    against tests/test_<name>.py. Excluded files are skipped.
    """
    if root is None:
        root = Path(__file__).parent.parent
    api_dir = root / "api"
    tests_dir = api_dir / "tests"
    missing: list[str] = []
    for source_dir in SOURCE_DIRS:
        dir_path = api_dir / source_dir
        if not dir_path.exists():
            continue
        for source_file in sorted(dir_path.glob("*.py")):
            if source_file.name in EXCLUDED_FILES:
                continue
            test_file = tests_dir / f"test_{source_file.name}"
            if not test_file.exists():
                missing.append(
                    f"  {source_file.relative_to(root)}"
                    f"  →  api/tests/test_{source_file.name}"
                )
    return missing


def check_router_health_tests(root: Path | None = None) -> list[str]:
    """Returns router test files that contain no health endpoint test.

    Every file matching tests/test_*_router.py must have a function
    whose name contains 'health'.
    """
    if root is None:
        root = Path(__file__).parent.parent
    tests_dir = root / "api" / "tests"
    missing: list[str] = []
    for test_file in sorted(tests_dir.glob("test_*_router.py")):
        content = test_file.read_text()
        if "health" not in content.lower():
            missing.append(
                f"  {test_file.relative_to(root)}  →  add test_*_health_* function"
            )
    return missing


def check_supabase_integration_markers(root: Path | None = None) -> list[str]:
    """Returns Supabase repository test files missing @pytest.mark.integration.

    Every supabase_*.py in repositories/ must have a test file that
    contains at least one @pytest.mark.integration marker.
    """
    if root is None:
        root = Path(__file__).parent.parent
    api_dir = root / "api"
    tests_dir = api_dir / "tests"
    missing: list[str] = []
    for repo_file in sorted((api_dir / "repositories").glob("supabase_*.py")):
        test_file = tests_dir / f"test_{repo_file.name}"
        if not test_file.exists():
            continue  # caught by check_test_files_exist
        content = test_file.read_text()
        if "@pytest.mark.integration" not in content:
            missing.append(
                f"  {test_file.relative_to(root)}  →  add @pytest.mark.integration test"
            )
    return missing


def main() -> None:
    """Runs all three checks and exits with code 1 if any fail."""
    errors: list[tuple[str, list[str]]] = []

    missing_files = check_test_files_exist()
    if missing_files:
        errors.append(("Source files without test files", missing_files))

    missing_health = check_router_health_tests()
    if missing_health:
        errors.append(("Router test files without health test", missing_health))

    missing_integration = check_supabase_integration_markers()
    if missing_integration:
        errors.append(
            (
                "Supabase repository tests without @pytest.mark.integration",
                missing_integration,
            )
        )

    if errors:
        print("ERROR: test coverage checks failed:\n")
        for title, items in errors:
            print(f"{title}:")
            for item in items:
                print(item)
            print()
        sys.exit(1)

    print("OK: all structural test coverage checks passed.")


if __name__ == "__main__":
    main()
