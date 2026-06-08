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

EXCLUDED_FILES: set[str] = {
    # Standard infrastructure files (no domain logic)
    "__init__.py",
    "dependencies.py",
    "main.py",
    "cli.py",
    "seeddata.py",
    # Abstract repository interface — no implementation to unit-test directly
    "user_repository.py",
    # Supabase base client wrapper — infrastructure helper, no domain logic
    "_supabase.py",
    # Supabase repository implementations — their tests live in test_<abstract_name>_repository.py;
    # integration coverage is enforced separately by check_supabase_integration_markers.
    "supabase_causal_model_repository.py",
    "supabase_claim_repository.py",
    "supabase_narrative_repository.py",
    "supabase_narrative_unit_repository.py",
    "supabase_user_repository.py",
    # HealthService is thin and tested indirectly through the health router (test_health_router.py).
    "health_service.py",
}

# Source files whose test file uses a different naming convention than the default test_<stem>*.py.
# Key: source filename, Value: expected test filename (relative to api/tests/).
TEST_FILE_OVERRIDES: dict[str, str] = {
    # Router resource uses plural (causal_models.py) but test follows domain singular naming.
    "causal_models.py": "test_causal_model_router.py",
}

# Supabase repository files where the test file does not match test_<abstract_stem>*.py.
# Key: supabase_*.py filename, Value: test filename (relative to api/tests/).
SUPABASE_TEST_OVERRIDES: dict[str, str] = {
    # test_users_repository.py uses plural 'users' — does not match test_user_repository*.py.
    "supabase_user_repository.py": "test_users_repository.py",
}


def check_test_files_exist(root: Path | None = None) -> list[str]:
    """Returns source files that have no corresponding test file.

    Checks every .py file in models/, services/, repositories/, routers/.
    Excluded files are skipped. Files in TEST_FILE_OVERRIDES are matched by explicit name.
    All other files use prefix matching: any test_<stem>*.py file is accepted.
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
            if source_file.name in TEST_FILE_OVERRIDES:
                expected = TEST_FILE_OVERRIDES[source_file.name]
                if not (tests_dir / expected).exists():
                    missing.append(
                        f"  {source_file.relative_to(root)}  →  api/tests/{expected}"
                    )
                continue
            # Prefix match: accept any test_<stem>*.py
            if not list(tests_dir.glob(f"test_{source_file.stem}*.py")):
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

    For each supabase_*.py in repositories/, resolves the corresponding test file:
    first checks SUPABASE_TEST_OVERRIDES, then falls back to glob test_<abstract_stem>*.py
    (i.e., the name without the supabase_ prefix). If no test file is found, skips
    (its absence is caught by check_test_files_exist where applicable).
    """
    if root is None:
        root = Path(__file__).parent.parent
    api_dir = root / "api"
    tests_dir = api_dir / "tests"
    missing: list[str] = []
    for repo_file in sorted((api_dir / "repositories").glob("supabase_*.py")):
        if repo_file.name in SUPABASE_TEST_OVERRIDES:
            test_file = tests_dir / SUPABASE_TEST_OVERRIDES[repo_file.name]
        else:
            abstract_stem = repo_file.stem.removeprefix("supabase_")
            matches = sorted(tests_dir.glob(f"test_{abstract_stem}*.py"))
            test_file = matches[0] if matches else tests_dir / f"test_{repo_file.name}"
        if not test_file.exists():
            continue  # no test file found — caught by check_test_files_exist where applicable
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
