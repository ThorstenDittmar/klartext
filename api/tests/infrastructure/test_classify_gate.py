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


# --- config-driven trigger patterns: sourced from seed.toml (B-voll unification) -----------


def test_trigger_patterns_are_derived_from_a_seed_toml(tmp_path: Path) -> None:
    """Expects load_trigger_patterns to build the gate's patterns from a given seed.toml.

    The patterns are the config's generic `wow_trigger_paths` plus the parametrized
    `cli_entrypoint` — proving the live gate is config-driven (seed.toml is the single
    source of truth, plan §4), not a hardcoded literal. Feeding a custom seed.toml must
    change the result, which a hardcoded list could never do.
    """
    seed = tmp_path / "seed.toml"
    seed.write_text('cli_entrypoint = "app/main.py"\nwow_trigger_paths = ["GUIDE.md", "ops/**"]\n')
    patterns = _gate.load_trigger_patterns(seed)
    assert patterns == ["GUIDE.md", "ops/**", "app/main.py"]


def test_module_trigger_patterns_come_from_the_repo_seed_toml() -> None:
    """Expects the module-level TRIGGER_PATTERNS to equal the repo seed.toml derivation.

    Pins the default wiring: the constant the workflow consumes is the seed.toml-derived
    list, so editing seed.toml (not this script) is what moves the live gate's scope.
    """
    repo_seed = Path(__file__).parents[3] / "seed" / "seed.toml"
    assert _gate.TRIGGER_PATTERNS == _gate.load_trigger_patterns(repo_seed)


# --- config-driven: fail-loud on a malformed seed.toml (GREEN regression guards) ----------
# These pin the "fail loud, never silently no-op" contract of load_trigger_patterns. A missing
# required key MUST raise (KeyError), not degrade to an empty / partial pattern list — because an
# empty TRIGGER_PATTERNS would make the gate pass every PR, silently disabling WoW classification.
# They are GREEN against the current `config[key]` subscript and would go RED if a regression
# switched to `config.get(key, <default>)`.


def test_load_trigger_patterns_raises_when_cli_entrypoint_key_is_missing(tmp_path: Path) -> None:
    """Expects a KeyError when seed.toml lacks `cli_entrypoint` — fail loud, never silently drop it.

    A regression to `config.get("cli_entrypoint", "")` would silently append an empty pattern
    instead of raising; this guards the loud-failure contract.
    """
    import pytest

    seed = tmp_path / "seed.toml"
    seed.write_text('wow_trigger_paths = ["GUIDE.md"]\n')
    with pytest.raises(KeyError):
        _gate.load_trigger_patterns(seed)


def test_load_trigger_patterns_raises_when_wow_trigger_paths_key_is_missing(tmp_path: Path) -> None:
    """Expects a KeyError when seed.toml lacks `wow_trigger_paths` — fail loud.

    A regression to `config.get("wow_trigger_paths", [])` would silently yield a gate that only
    triggers on the CLI path (every doc/agent/infra WoW surface would slip through unclassified).
    This guards against that silent scope collapse.
    """
    import pytest

    seed = tmp_path / "seed.toml"
    seed.write_text('cli_entrypoint = "app/main.py"\n')
    with pytest.raises(KeyError):
        _gate.load_trigger_patterns(seed)


def test_empty_wow_trigger_paths_yields_only_the_cli_entrypoint(tmp_path: Path) -> None:
    """Expects an empty `wow_trigger_paths` to yield exactly [cli_entrypoint] — no crash.

    Documents the boundary: an empty generic-WoW list is valid config (the gate then
    triggers only on the product CLI path). A non-CLI WoW surface must then PASS, and the
    CLI path must still trip.
    """
    seed = tmp_path / "seed.toml"
    seed.write_text('cli_entrypoint = "app/main.py"\nwow_trigger_paths = []\n')
    assert _gate.load_trigger_patterns(seed) == ["app/main.py"]


# --- not applicable: no Way-of-Working surface touched -----------------------------------


def test_non_trigger_paths_pass_without_a_label() -> None:
    """Expects PASS when the PR touches only ordinary code/test files and carries no label."""
    result = _gate.evaluate(["api/services/user_service.py", "frontend/src/App.tsx"], set())
    assert result.passed is True


def test_near_miss_adr_path_is_not_a_trigger() -> None:
    """Expects an ADR doc (docs/adr/..) to NOT count as a Way-of-Working surface."""
    result = _gate.evaluate(["docs/adr/0012-worktree-convergence-model.md"], set())
    assert result.passed is True


def test_near_miss_legacy_improvement_docs_are_not_a_trigger() -> None:
    """Expects docs/superpowers/improvement/.. to NOT be a trigger — it is the emptied legacy tree.

    The method content moved to docs/method/ in F0.1/F0.2; the live WoW surface is docs/method/**
    (see test below). A stray path under the old, now-empty tree is not a WoW trigger.
    """
    result = _gate.evaluate(["docs/superpowers/improvement/practices/improvement-step.md"], set())
    assert result.passed is True


def test_method_docs_are_a_trigger() -> None:
    """Expects docs/method/** (the migrated WoW method surface) to be a classification trigger.

    Method changes previously escaped the rolling|breaking gate; F0.3 added docs/method/** to close
    that scope gap. A method-doc PR without a label must now FAIL until classified.
    """
    assert _gate.is_trigger_path("docs/method/library/practices/tdd.md") is True
    assert _gate.is_trigger_path("docs/method/enactment/method.md") is True
    result = _gate.evaluate(["docs/method/library/practices/tdd.md"], set())
    assert result.passed is False


# --- each trigger pattern matches a representative path ------------------------------------


def test_github_workflows_are_a_trigger() -> None:
    """Expects .github/workflows/** to be a WoW surface (SA §9 verdict).

    The workflows ARE the mechanical enforcement layer; a change to them is a rolling-vs-breaking
    question (ADR-0006), so a workflow-only PR must carry a classification label. Rule + check in
    the same commit (SA §1 charter).
    """
    assert _gate.is_trigger_path(".github/workflows/test.yml") is True
    result = _gate.evaluate([".github/workflows/classify-gate.yml"], set())
    assert result.passed is False


def test_each_trigger_pattern_matches_a_representative_path() -> None:
    """Expects every Way-of-Working trigger pattern to be recognised for a representative path."""
    representatives = [
        "CLAUDE.md",
        "docs/method/enactment/skills/tdd.md",
        "docs/method/library/practices/tdd.md",
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
      * 'docs/method/enactment/skillsX/' — prefix collision: 'skills/**' keeps its trailing slash,
                                       so 'skillsX/...' must NOT match.
      * 'api/cli.py.bak'            — exact-match pattern must not match a longer path.
    """
    near_misses = [
        "CLAUDEXmd",
        "scripts",
        "xapi/cli.py",
        "docs/methodX/foo.md",
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


def test_parse_list_reads_empty_json_array_as_no_items() -> None:
    """Expects an empty JSON array to parse to no items.

    This is exactly what the workflow's live `gh pr view --json labels --jq '[.labels[].name]'`
    emits for a label-less PR — the gate must read it as "no label present", not choke on it.
    """
    assert _gate._parse_list("[]") == []


def test_parse_list_reads_whitespace_wrapped_empty_json_array_as_no_items() -> None:
    """Expects a `[]` with surrounding whitespace / a trailing newline to still parse to no items.

    The workflow captures the live labels via shell command substitution
    (`labels="$(gh pr view ... --jq '[.labels[].name]')"`), which can carry a trailing newline.
    `_parse_list` strips before the JSON branch, so a surrounding-space or trailing-newline `[]`
    must read as "no label present" — exactly the label-less PR shape the live-read fix relies on.
    """
    assert _gate._parse_list(" [] ") == []
    assert _gate._parse_list("[]\n") == []


def test_evaluate_trigger_with_empty_label_set_fails_with_guidance() -> None:
    """Pins the race red-path: a WoW surface with a truly empty label set FAILs with guidance.

    This is the exact state the live-read fix protects: when the event-payload snapshot raced the
    label attach, the gate saw zero labels on a WoW PR. The verdict must be FAIL and the message
    must tell the author what to do (add exactly one of rolling | breaking) and name the surface —
    not a bare/generic failure.
    """
    result = _gate.evaluate(["docs/method/library/practices/tdd.md"], set())
    assert result.passed is False
    assert "no classification label" in result.message.lower()
    assert "rolling" in result.message and "breaking" in result.message
    assert "docs/method/library/practices/tdd.md" in result.message
