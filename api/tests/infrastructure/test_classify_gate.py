"""Infrastructure tests: the classification gate (scripts/classify_gate.py).

ADR-0012 two-mode consistency: a PR that touches a Way-of-Working surface (method docs,
agent Hoheitswissen, infra config) must carry exactly one classification label,
`rolling` or `breaking`. The gate is default-free — it never infers the label.

The pure decision (`evaluate`) is unit-tested here against the trigger-path matrix. The
workflow wiring (.github/workflows/classify-gate.yml) only collects changed paths + labels
and forwards the exit code; the decision lives in this one importable module so it is
testable without a live PR.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parents[3] / "scripts" / "classify_gate.py"


def _load():
    """Loads scripts/classify_gate.py as a module (it is a standalone script, not a package)."""
    spec = importlib.util.spec_from_file_location("classify_gate", _SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the frozen dataclass with `from __future__ import annotations`
    # resolves its annotations via sys.modules[module.__name__] during class creation.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_gate = _load()


# --- not applicable: no Way-of-Working surface touched -----------------------------------


def test_non_trigger_paths_pass_without_a_label() -> None:
    """Expects PASS when the PR touches only ordinary code/test files and carries no label."""
    result = _gate.evaluate(["api/services/user_service.py", "frontend/src/App.tsx"], set())
    assert result.passed is True


def test_near_miss_adr_path_is_not_a_trigger() -> None:
    """Expects an ADR doc (docs/adr/..) to NOT count as a Way-of-Working surface."""
    result = _gate.evaluate(["docs/adr/0012-worktree-convergence-model.md"], set())
    assert result.passed is True


def test_near_miss_improvement_docs_are_not_a_trigger() -> None:
    """Expects docs/superpowers/improvement/.. to be out of scope (deliberate scope decision)."""
    result = _gate.evaluate(["docs/superpowers/improvement/practices/improvement-step.md"], set())
    assert result.passed is True


# --- each trigger pattern matches a representative path ------------------------------------


def test_each_trigger_pattern_matches_a_representative_path() -> None:
    """Expects every Way-of-Working trigger pattern to be recognised for a representative path."""
    representatives = [
        "CLAUDE.md",
        "docs/superpowers/skills/tdd.md",
        "agents/devops/claude.md",
        ".claude/settings.json",
        "scripts/session_health.py",
        "api/cli.py",
    ]
    for path in representatives:
        assert _gate.is_trigger_path(path) is True, f"expected {path} to be a trigger path"


# --- triggered: exactly one label required ------------------------------------------------


def test_trigger_path_with_rolling_passes() -> None:
    """Expects PASS when a Way-of-Working change carries the 'rolling' label."""
    result = _gate.evaluate(["CLAUDE.md"], {"rolling"})
    assert result.passed is True


def test_trigger_path_with_breaking_passes() -> None:
    """Expects PASS when a Way-of-Working change carries the 'breaking' label."""
    result = _gate.evaluate(["agents/devops/claude.md"], {"breaking"})
    assert result.passed is True


def test_trigger_path_with_no_label_fails() -> None:
    """Expects FAIL when a Way-of-Working change carries neither classification label."""
    result = _gate.evaluate(["scripts/session_health.py"], {"some-other-label"})
    assert result.passed is False


def test_trigger_path_with_both_labels_fails() -> None:
    """Expects FAIL when a Way-of-Working change carries both 'rolling' and 'breaking'."""
    result = _gate.evaluate(["CLAUDE.md"], {"rolling", "breaking"})
    assert result.passed is False


def test_failure_message_names_the_touched_surfaces() -> None:
    """Expects the failure message to name the offending path so the author knows why it tripped."""
    result = _gate.evaluate(["scripts/session_health.py"], set())
    assert result.passed is False
    assert "scripts/session_health.py" in result.message


# --- CLI wiring the workflow depends on ---------------------------------------------------


def test_parse_list_reads_a_json_array() -> None:
    """Expects a JSON array (the shape of GitHub's labels payload) to parse into a list."""
    assert _gate._parse_list('["rolling", "breaking"]') == ["rolling", "breaking"]


def test_parse_list_reads_newline_separated_paths() -> None:
    """Expects newline-separated `git diff --name-only` output to parse into a list."""
    assert _gate._parse_list("CLAUDE.md\nscripts/x.py\n") == ["CLAUDE.md", "scripts/x.py"]


def test_parse_list_treats_empty_as_no_items() -> None:
    """Expects empty / whitespace input to yield an empty list (PR with no labels)."""
    assert _gate._parse_list("   ") == []


def test_main_returns_zero_for_non_trigger_pr() -> None:
    """Expects exit code 0 when no Way-of-Working surface is touched."""
    code = _gate.main(["--changed-paths", "api/services/user_service.py", "--labels", ""])
    assert code == 0


def test_main_returns_one_for_unlabelled_wow_pr() -> None:
    """Expects exit code 1 when a Way-of-Working surface is touched without a label."""
    code = _gate.main(["--changed-paths", "CLAUDE.md", "--labels", "[]"])
    assert code == 1


def test_main_returns_zero_for_labelled_wow_pr() -> None:
    """Expects exit code 0 when a Way-of-Working surface is touched with exactly one label."""
    code = _gate.main(["--changed-paths", "CLAUDE.md", "--labels", '["breaking"]'])
    assert code == 0


# --- QA gap coverage: adversarial path-matching near-misses --------------------------------


def test_near_miss_paths_are_not_triggers() -> None:
    """Expects look-alike paths to NOT match — guards the trigger matcher against false positives.

    Each case targets a specific branch of is_trigger_path:
      * 'CLAUDEXmd'                 — exact-match pattern must not fuzzy-match.
      * 'scripts'                   — bare dir name (no slash) must not match 'scripts/**'.
      * 'xapi/cli.py'               — suffix collision must not match the exact 'api/cli.py'.
      * 'docs/superpowers/skillsX/' — prefix collision: 'skills/**' keeps its trailing slash,
                                       so 'skillsX/...' must NOT match.
      * 'api/cli.py.bak'            — exact-match pattern must not match a longer path.
    """
    near_misses = [
        "CLAUDEXmd",
        "scripts",
        "xapi/cli.py",
        "docs/superpowers/skillsX/foo.md",
        "api/cli.py.bak",
    ]
    for path in near_misses:
        assert _gate.is_trigger_path(path) is False, f"expected {path!r} NOT to be a trigger path"


def test_agents_claude_md_without_intermediate_dir_matches() -> None:
    """Pins the head+tail matcher behaviour: 'agents/**/claude.md' matches even with no middle dir.

    'agents/claude.md' has no intermediate directory, yet startswith('agents/') and
    endswith('/claude.md') both hold, so it is treated as a trigger. This documents the
    current behaviour so a future matcher change cannot silently alter it.
    """
    assert _gate.is_trigger_path("agents/claude.md") is True
    assert _gate.is_trigger_path("agents/a/b/claude.md") is True


# --- QA gap coverage: evaluate branch edges -----------------------------------------------


def test_evaluate_empty_changed_paths_passes() -> None:
    """Expects an empty changed-paths list (no files touched) to pass — gate not applicable."""
    result = _gate.evaluate([], set())
    assert result.passed is True


def test_evaluate_names_only_the_trigger_among_mixed_paths() -> None:
    """Expects a mix of trigger + non-trigger paths to fail and name ONLY the trigger path."""
    result = _gate.evaluate(["api/services/user_service.py", "CLAUDE.md"], set())
    assert result.passed is False
    assert "CLAUDE.md" in result.message
    assert "user_service.py" not in result.message


def test_both_labels_message_distinguishes_from_no_label() -> None:
    """Expects the both-labels failure message to explain 'exactly one is required'.

    The single near-miss already asserts passed is False for both labels; this pins the
    message content so the author sees WHY (both present) rather than a generic failure.
    """
    result = _gate.evaluate(["CLAUDE.md"], {"rolling", "breaking"})
    assert result.passed is False
    assert "both" in result.message.lower()
    assert "exactly one" in result.message.lower()


# --- QA gap coverage: _parse_list input shapes --------------------------------------------


def test_parse_list_reads_comma_separated_input() -> None:
    """Expects comma-separated input (the alternate label shape) to parse into a list."""
    assert _gate._parse_list("rolling, breaking") == ["rolling", "breaking"]


def test_parse_list_reads_mixed_commas_and_newlines() -> None:
    """Expects mixed comma + newline separators to parse into a flat list."""
    assert _gate._parse_list("a,b\nc") == ["a", "b", "c"]


def test_parse_list_drops_empty_strings_in_json_array() -> None:
    """Expects empty strings inside a JSON array to be dropped (GitHub can emit blanks)."""
    assert _gate._parse_list('["rolling", "", "breaking"]') == ["rolling", "breaking"]
