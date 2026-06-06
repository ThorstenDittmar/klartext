"""Tests for scripts/check_test_coverage.py.

Tests use a temporary directory that mimics the klartext API structure.
"""

from __future__ import annotations

# Add scripts/ to path so we can import the module
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from check_test_coverage import (
    check_router_health_tests,
    check_supabase_integration_markers,
    check_test_files_exist,
)


@pytest.fixture()
def api_tree(tmp_path: Path) -> Path:
    """Creates a temporary directory tree that mimics the klartext API structure."""
    (tmp_path / "api" / "models").mkdir(parents=True)
    (tmp_path / "api" / "services").mkdir(parents=True)
    (tmp_path / "api" / "repositories").mkdir(parents=True)
    (tmp_path / "api" / "routers").mkdir(parents=True)
    (tmp_path / "api" / "tests").mkdir(parents=True)
    return tmp_path


class TestCheckTestFilesExist:
    def test_returns_empty_when_all_source_files_have_tests(self, api_tree: Path) -> None:
        """Expects no missing files when every source file has a test counterpart."""
        (api_tree / "api" / "models" / "user.py").touch()
        (api_tree / "api" / "tests" / "test_user.py").touch()
        missing = check_test_files_exist(root=api_tree)
        assert missing == []

    def test_returns_missing_when_test_file_absent(self, api_tree: Path) -> None:
        """Expects the source file path when no test file exists."""
        (api_tree / "api" / "models" / "user.py").touch()
        missing = check_test_files_exist(root=api_tree)
        assert len(missing) == 1
        assert "user.py" in missing[0]

    def test_excludes_init_and_main_files(self, api_tree: Path) -> None:
        """Expects __init__.py, main.py, dependencies.py, cli.py, seeddata.py to be excluded."""
        for name in ["__init__.py", "main.py", "dependencies.py", "cli.py", "seeddata.py"]:
            (api_tree / "api" / "routers" / name).touch()
        missing = check_test_files_exist(root=api_tree)
        assert missing == []


class TestCheckRouterHealthTests:
    def test_returns_empty_when_health_test_present(self, api_tree: Path) -> None:
        """Expects no missing files when the router test has a health test."""
        test_file = api_tree / "api" / "tests" / "test_users_router.py"
        test_file.write_text("def test_users_health_returns_200(): pass\n")
        missing = check_router_health_tests(root=api_tree)
        assert missing == []

    def test_returns_file_when_health_test_absent(self, api_tree: Path) -> None:
        """Expects the test file path when no health test is found."""
        test_file = api_tree / "api" / "tests" / "test_users_router.py"
        test_file.write_text("def test_create_user(): pass\n")
        missing = check_router_health_tests(root=api_tree)
        assert len(missing) == 1
        assert "test_users_router.py" in missing[0]

    def test_only_checks_router_test_files(self, api_tree: Path) -> None:
        """Expects non-router test files to be ignored."""
        test_file = api_tree / "api" / "tests" / "test_user_service.py"
        test_file.write_text("def test_something(): pass\n")
        missing = check_router_health_tests(root=api_tree)
        assert missing == []


class TestCheckSupabaseIntegrationMarkers:
    def test_returns_empty_when_integration_marker_present(self, api_tree: Path) -> None:
        """Expects no missing files when the Supabase repo test has @pytest.mark.integration."""
        (api_tree / "api" / "repositories" / "supabase_user_repository.py").touch()
        test_file = api_tree / "api" / "tests" / "test_supabase_user_repository.py"
        test_file.write_text("@pytest.mark.integration\nasync def test_save(): pass\n")
        missing = check_supabase_integration_markers(root=api_tree)
        assert missing == []

    def test_returns_file_when_integration_marker_absent(self, api_tree: Path) -> None:
        """Expects the test file path when @pytest.mark.integration is missing."""
        (api_tree / "api" / "repositories" / "supabase_user_repository.py").touch()
        test_file = api_tree / "api" / "tests" / "test_supabase_user_repository.py"
        test_file.write_text("async def test_save(): pass\n")
        missing = check_supabase_integration_markers(root=api_tree)
        assert len(missing) == 1
        assert "test_supabase_user_repository.py" in missing[0]

    def test_skips_repo_if_test_file_missing(self, api_tree: Path) -> None:
        """Expects no error if the test file does not exist.

        Missing test files are caught by check_test_files_exist, not here.
        """
        (api_tree / "api" / "repositories" / "supabase_user_repository.py").touch()
        missing = check_supabase_integration_markers(root=api_tree)
        assert missing == []

    def test_only_checks_supabase_repositories(self, api_tree: Path) -> None:
        """Expects non-Supabase repository test files to be ignored."""
        (api_tree / "api" / "repositories" / "user_repository.py").touch()
        test_file = api_tree / "api" / "tests" / "test_user_repository.py"
        test_file.write_text("def test_something(): pass\n")
        missing = check_supabase_integration_markers(root=api_tree)
        assert missing == []
