"""Infrastructure tests: the CI path-scope decision (scripts/ci_scope.py).

#1a coarse CI scoping (ADR: methode/app separation): a PR that touches only the
collaboration method / environment (docs/**, agents/**, .claude/**) must not run the
App checks. The App checks are *required* status checks, so the workflow job always
runs and reports success — only the expensive steps are skipped. The skip decision
lives in this one importable module so it is testable without a live PR.

Safety contract: NEVER skip an App group on shared/unknown/empty input — when in doubt,
run everything. A wrongly-skipped required check is invisible breakage.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parents[3] / "scripts" / "ci_scope.py"


def _load():
    """Loads scripts/ci_scope.py as a module (it is a standalone script, not a package)."""
    spec = importlib.util.spec_from_file_location("ci_scope", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_scope = _load()


# --- the saving case: pure method/environment change skips all App checks ----------------


def test_pure_method_change_skips_all_app_checks() -> None:
    """Expects api=False and frontend=False when every path is method/environment only."""
    result = _scope.decide(["docs/superpowers/skills/frontend.md", "agents/devops/claude.md"])
    assert result.api is False
    assert result.frontend is False


def test_dotclaude_only_change_skips_all_app_checks() -> None:
    """Expects all App checks skipped for a change confined to .claude/."""
    result = _scope.decide([".claude/settings.json"])
    assert result.api is False
    assert result.frontend is False


# --- granular app scoping ----------------------------------------------------------------


def test_api_only_change_runs_api_skips_frontend() -> None:
    """Expects api=True, frontend=False when only backend files changed."""
    result = _scope.decide(["api/services/user_service.py"])
    assert result.api is True
    assert result.frontend is False


def test_frontend_only_change_runs_frontend_skips_api() -> None:
    """Expects frontend=True, api=False when only frontend files changed."""
    result = _scope.decide(["frontend/src/lib/api.ts"])
    assert result.frontend is True
    assert result.api is False


def test_api_and_frontend_change_runs_both() -> None:
    """Expects both groups relevant when both app trees changed."""
    result = _scope.decide(["api/cli.py", "frontend/src/main.tsx"])
    assert result.api is True
    assert result.frontend is True


def test_method_change_mixed_with_api_runs_api_only() -> None:
    """Expects api=True, frontend=False when a method doc and a backend file changed together."""
    result = _scope.decide(["docs/superpowers/skills/tdd.md", "api/cli.py"])
    assert result.api is True
    assert result.frontend is False


# --- safety: conservative default on shared / unknown / empty input ----------------------


def test_shared_uncertain_path_runs_all_conservatively() -> None:
    """Expects both groups True for a shared/unknown path (e.g. a CI workflow change)."""
    result = _scope.decide([".github/workflows/test.yml"])
    assert result.api is True
    assert result.frontend is True


def test_root_config_change_runs_all_conservatively() -> None:
    """Expects both groups True for a repo-root file that is neither app tree nor method-only."""
    result = _scope.decide(["README.md"])
    assert result.api is True
    assert result.frontend is True


def test_empty_changed_paths_runs_all_conservatively() -> None:
    """Expects both groups True when no changed paths are known (push / diff failure)."""
    result = _scope.decide([])
    assert result.api is True
    assert result.frontend is True


def test_shared_path_mixed_with_method_still_runs_all() -> None:
    """Expects a single shared path to force all checks even alongside method-only paths."""
    result = _scope.decide(["docs/superpowers/skills/tdd.md", "pyproject.toml"])
    assert result.api is True
    assert result.frontend is True


# --- CLI: GITHUB_OUTPUT-style key=value lines, never fails the job -----------------------


def test_main_emits_lowercase_booleans_for_method_change(capsys) -> None:
    """Expects 'api=false' and 'frontend=false' on stdout for a method-only change."""
    code = _scope.main(["--changed-paths", "docs/superpowers/skills/tdd.md"])
    out = capsys.readouterr().out
    assert "api=false" in out
    assert "frontend=false" in out
    assert code == 0


def test_main_emits_true_for_api_change(capsys) -> None:
    """Expects 'api=true' and 'frontend=false' for a backend-only change."""
    _scope.main(["--changed-paths", "api/cli.py"])
    out = capsys.readouterr().out
    assert "api=true" in out
    assert "frontend=false" in out


def test_main_always_returns_zero_it_is_not_a_gate(capsys) -> None:
    """Expects exit code 0 even when both groups run — ci_scope reports, never blocks."""
    assert _scope.main(["--changed-paths", "README.md"]) == 0


def test_main_reads_json_array_of_paths(capsys) -> None:
    """Expects the CLI to parse a JSON array (as a workflow would pass label-style input)."""
    _scope.main(["--changed-paths", '["frontend/src/main.tsx"]'])
    out = capsys.readouterr().out
    assert "frontend=true" in out
    assert "api=false" in out
