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


# --- safety: prefix-boundary discipline (the trailing-slash contract) --------------------
# These pin the single most dangerous regression: matching by bare prefix instead of
# "prefix + /". A bare-prefix match would let a sibling path (apifoo/, agentsfoo/) or a
# repo-root file (apidocs.md) be mis-classified — silently skipping a *required* check.


def test_sibling_of_api_prefix_is_not_treated_as_api() -> None:
    """Expects 'apifoo/x.py' to be shared/unknown — it only resembles the api/ tree."""
    result = _scope.decide(["apifoo/x.py"])
    assert result.api is True, "apifoo/ is not the api/ tree — must run conservatively"
    assert result.frontend is True, "apifoo/ is not method-only — frontend must also run"


def test_sibling_of_frontend_prefix_is_not_treated_as_frontend() -> None:
    """Expects 'frontendx/y.ts' to be shared/unknown — it only resembles frontend/."""
    result = _scope.decide(["frontendx/y.ts"])
    assert result.api is True
    assert result.frontend is True, "frontendx/ is not the frontend/ tree"


def test_sibling_of_agents_prefix_is_not_treated_as_method_only() -> None:
    """Expects 'agentsfoo/x' to force all checks — it must NOT be skipped as method-only.

    This is the critical invisible-breakage case: a bare 'agents' prefix match would skip
    BOTH App groups for a path that is not actually under agents/.
    """
    result = _scope.decide(["agentsfoo/x"])
    assert result.api is True, "agentsfoo/ is not under agents/ — must not skip api"
    assert result.frontend is True, "agentsfoo/ is not under agents/ — must not skip frontend"


def test_root_file_resembling_docs_prefix_is_not_method_only() -> None:
    """Expects 'documentation.md' at repo root to run all checks (it is not under docs/)."""
    result = _scope.decide(["documentation.md"])
    assert result.api is True
    assert result.frontend is True


def test_path_equal_to_app_prefix_without_slash_runs_all() -> None:
    """Expects a bare 'api' (no trailing slash) to be shared/unknown, not the api/ tree."""
    result = _scope.decide(["api"])
    assert result.api is True
    assert result.frontend is True, "bare 'api' is not provably the api/ tree only"


def test_path_equal_to_method_prefix_without_slash_runs_all() -> None:
    """Expects a bare 'docs' (no trailing slash) to NOT be skipped as method-only."""
    result = _scope.decide(["docs"])
    assert result.api is True, "bare 'docs' is not under docs/ — must not skip"
    assert result.frontend is True


def test_path_matching_is_case_sensitive() -> None:
    """Expects an upper-case 'API/foo.py' to be shared/unknown — matching is case-sensitive."""
    result = _scope.decide(["API/foo.py"])
    assert result.api is True
    assert result.frontend is True, "uppercase API/ does not match the api/ tree"


# --- safety: padded entries are stripped before classification ---------------------------


def test_whitespace_padded_path_is_classified_after_stripping() -> None:
    """Expects a padded '  api/x.py  ' to still classify as api-only after stripping."""
    result = _scope.decide(["  api/cli.py  "])
    assert result.api is True
    assert result.frontend is False, "padded api path must not be misread as shared"


# --- CLI parsing edge cases: comma- and newline-separated input --------------------------


def test_main_parses_comma_separated_paths(capsys) -> None:
    """Expects the CLI to split a comma-separated string (gh output piped as one arg).

    The api/ path is the SECOND segment on purpose: if comma-splitting were dropped the
    whole string would be one method-only-looking line and api would be wrongly skipped.
    """
    _scope.main(["--changed-paths", "docs/superpowers/skills/tdd.md, api/cli.py"])
    out = capsys.readouterr().out
    assert "api=true" in out, "comma-separated api/ path must be detected after splitting"
    assert "frontend=false" in out


def test_main_parses_newline_separated_paths(capsys) -> None:
    """Expects the CLI to split newline-separated paths (the gh pr diff --name-only shape)."""
    _scope.main(["--changed-paths", "frontend/src/main.tsx\napi/cli.py"])
    out = capsys.readouterr().out
    assert "api=true" in out
    assert "frontend=true" in out
