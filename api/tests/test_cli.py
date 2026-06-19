"""Unit tests for the pure decision logic behind `klartext merge`.

The live gh/git calls in the merge command are not headless-testable, but the
decisions they hang on are pure functions and gated here: which merge methods
are allowed, how a set of CI check states collapses to one verdict, and whether
a PR's state permits merging.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import typer
from wow_cli.landed import LandedStatus, _landed_verdict
from wow_cli.skills import SkillsSyncAction, _sync_skills

from api.cli import (
    ConvergeAction,
    _converge_decision,
    _evaluate_checks,
    _evaluate_preconditions,
    _is_home_branch,
    _is_worktree_clean,
    _parse_worktree_list,
    _validate_merge_method,
)

# ---------------------------------------------------------------------------
# Merge-method policy: squash + merge allowed, rebase excluded (stack footgun)
# ---------------------------------------------------------------------------


def test_validate_merge_method_accepts_squash() -> None:
    """Expects 'squash' to be accepted and returned unchanged."""
    assert _validate_merge_method("squash") == "squash"


def test_validate_merge_method_accepts_merge() -> None:
    """Expects 'merge' (merge-commit) to be accepted for SHA-preserving stacks."""
    assert _validate_merge_method("merge") == "merge"


def test_validate_merge_method_rejects_rebase() -> None:
    """Expects 'rebase' to be rejected — it rewrites SHAs and breaks stacks."""
    with pytest.raises(typer.BadParameter):
        _validate_merge_method("rebase")


def test_validate_merge_method_rejects_unknown() -> None:
    """Expects an unknown method to be rejected."""
    with pytest.raises(typer.BadParameter):
        _validate_merge_method("fast-forward")


@pytest.mark.parametrize(
    ("given", "expected"),
    [("SQUASH", "squash"), ("Merge", "merge"), ("Squash", "squash"), ("MERGE", "merge")],
)
def test_validate_merge_method_is_case_insensitive(given: str, expected: str) -> None:
    """Expects mixed/upper-case methods to be accepted and normalized to lowercase.

    The function lowercases before checking — a real behaviour (a user typing
    `--method Squash` must work) that the lowercasing line silently provides. Pinned
    here so a refactor that drops `.lower()` is caught instead of breaking the CLI.
    """
    assert _validate_merge_method(given) == expected


def test_validate_merge_method_rejects_rebase_with_specific_message() -> None:
    """Expects the rebase rejection to explain *why* (SHA rewrite / stacks), not a generic error.

    The rebase branch carries a tailored message distinct from the unknown-method
    branch; the guidance is the point, so it is asserted rather than just the raise.
    """
    with pytest.raises(typer.BadParameter) as exc:
        _validate_merge_method("rebase")
    message = str(exc.value)
    assert "rebase" in message
    assert "squash" in message and "merge" in message


def test_validate_merge_method_rejects_mixed_case_rebase() -> None:
    """Expects 'Rebase' to hit the rebase-specific branch, not the unknown-method branch.

    Lowercasing happens before the rebase check, so case must not let a rebase slip
    into the generic 'unknown method' path with the wrong guidance.
    """
    with pytest.raises(typer.BadParameter) as exc:
        _validate_merge_method("Rebase")
    assert "rewrites commit SHAs" in str(exc.value)


# ---------------------------------------------------------------------------
# Check evaluation: a list of gh check buckets → one verdict
# ---------------------------------------------------------------------------


def test_evaluate_checks_all_pass() -> None:
    """Expects 'pass' when every check is in the pass bucket."""
    checks = [{"bucket": "pass"}, {"bucket": "pass"}]
    assert _evaluate_checks(checks) == "pass"


def test_evaluate_checks_any_fail_is_fail() -> None:
    """Expects 'fail' when at least one check failed, even if others pass."""
    checks = [{"bucket": "pass"}, {"bucket": "fail"}, {"bucket": "pass"}]
    assert _evaluate_checks(checks) == "fail"


def test_evaluate_checks_cancel_counts_as_fail() -> None:
    """Expects a cancelled check to count as a failure, not a pass."""
    checks = [{"bucket": "pass"}, {"bucket": "cancel"}]
    assert _evaluate_checks(checks) == "fail"


def test_evaluate_checks_pending_when_not_failed() -> None:
    """Expects 'pending' when a check is still running and none have failed."""
    checks = [{"bucket": "pass"}, {"bucket": "pending"}]
    assert _evaluate_checks(checks) == "pending"


def test_evaluate_checks_fail_takes_precedence_over_pending() -> None:
    """Expects 'fail' to win over 'pending' — a red PR is never worth waiting on."""
    checks = [{"bucket": "pending"}, {"bucket": "fail"}]
    assert _evaluate_checks(checks) == "fail"


def test_evaluate_checks_skipping_does_not_block() -> None:
    """Expects skipped checks to be treated as non-blocking (verdict 'pass')."""
    checks = [{"bucket": "pass"}, {"bucket": "skipping"}]
    assert _evaluate_checks(checks) == "pass"


def test_evaluate_checks_empty_is_pass() -> None:
    """Expects an empty check list to be 'pass' — nothing is blocking the merge."""
    assert _evaluate_checks([]) == "pass"


def test_evaluate_checks_skipping_and_pending_is_pending() -> None:
    """Expects 'skipping' to stay non-blocking while a real 'pending' still forces a wait.

    The skipping+pass case is covered elsewhere; this pins the mixed case so a
    skipped check can never mask a still-running one and let a not-yet-green PR merge.
    """
    checks = [{"bucket": "skipping"}, {"bucket": "pending"}]
    assert _evaluate_checks(checks) == "pending"


def test_evaluate_checks_skipping_and_fail_is_fail() -> None:
    """Expects a failure to win over a skipped check — skipping never softens a red run."""
    checks = [{"bucket": "skipping"}, {"bucket": "fail"}]
    assert _evaluate_checks(checks) == "fail"


def test_evaluate_checks_missing_bucket_is_conservative() -> None:
    """Expects a check dict without a 'bucket' key to be treated as not-yet-passing.

    A check with no recognizable status must not silently count toward 'pass'. For a
    gatekeeper, only explicitly 'pass'/'skipping' buckets satisfy a check; anything
    else (None, unknown string) blocks the merge as 'pending' — the poll waits and
    ultimately times out rather than letting an unrecognized status through.
    """
    checks = [{"bucket": "pass"}, {"name": "weird-check-without-bucket"}]
    assert _evaluate_checks(checks) == "pending"


def test_evaluate_checks_unknown_bucket_value_is_conservative() -> None:
    """Expects an unrecognized bucket string to block (pending), not pass."""
    checks = [{"bucket": "pass"}, {"bucket": "teleported"}]
    assert _evaluate_checks(checks) == "pending"


def test_evaluate_checks_missing_bucket_does_not_mask_pending() -> None:
    """Expects an unknown/None bucket alongside a pending check to still read as 'pending'.

    A check with no bucket must not collapse a genuinely pending run to 'pass'.
    """
    checks = [{"name": "no-bucket"}, {"bucket": "pending"}]
    assert _evaluate_checks(checks) == "pending"


# ---------------------------------------------------------------------------
# Precondition evaluation: PR state JSON → (ok, reason)
# ---------------------------------------------------------------------------


def test_preconditions_ok_for_open_clean_pr() -> None:
    """Expects an OPEN, mergeable, clean PR to pass preconditions."""
    pr = {"state": "OPEN", "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"}
    ok, reason = _evaluate_preconditions(pr)
    assert ok is True
    assert reason == ""


def test_preconditions_reject_closed_pr() -> None:
    """Expects a non-OPEN PR to be rejected with a reason mentioning its state."""
    pr = {"state": "MERGED", "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"}
    ok, reason = _evaluate_preconditions(pr)
    assert ok is False
    assert "MERGED" in reason


def test_preconditions_reject_conflicting_pr() -> None:
    """Expects a PR with merge conflicts to be rejected."""
    pr = {"state": "OPEN", "mergeable": "CONFLICTING", "mergeStateStatus": "DIRTY"}
    ok, reason = _evaluate_preconditions(pr)
    assert ok is False
    assert reason != ""


def test_preconditions_allow_unknown_merge_state() -> None:
    """Expects an OPEN PR whose merge state GitHub is still computing to proceed.

    UNKNOWN/UNSTABLE/BEHIND are transient or check-related — the check-poll step
    handles CI status, so preconditions must not hard-abort on them.
    """
    pr = {"state": "OPEN", "mergeable": "MERGEABLE", "mergeStateStatus": "UNKNOWN"}
    ok, _ = _evaluate_preconditions(pr)
    assert ok is True


def test_preconditions_allow_unknown_mergeable_value() -> None:
    """Expects an OPEN PR whose `mergeable` is still UNKNOWN (not CONFLICTING) to proceed.

    GitHub computes mergeability asynchronously; right after opening, `mergeable` can be
    UNKNOWN. Only CONFLICTING (or a DIRTY merge state) is a hard conflict, so UNKNOWN must
    not be conflated with it — otherwise every freshly opened PR would be wrongly blocked.
    """
    pr = {"state": "OPEN", "mergeable": "UNKNOWN", "mergeStateStatus": "UNKNOWN"}
    ok, reason = _evaluate_preconditions(pr)
    assert ok is True
    assert reason == ""


def test_preconditions_allow_blocked_merge_state() -> None:
    """Documents that an OPEN PR with mergeStateStatus BLOCKED proceeds — by design.

    BLOCKED typically means required checks/reviews are not yet satisfied. The function
    deliberately does NOT hard-fail here; the check-poll step owns CI gating. This test
    pins that intended hand-off so it can't silently flip to a hard abort. Flagged for
    DevOps: confirm relying on the check-poll for BLOCKED is the intended contract.
    """
    pr = {"state": "OPEN", "mergeable": "MERGEABLE", "mergeStateStatus": "BLOCKED"}
    ok, reason = _evaluate_preconditions(pr)
    assert ok is True
    assert reason == ""


def test_preconditions_reject_dirty_state_even_if_mergeable_unknown() -> None:
    """Expects a DIRTY merge state to be rejected on its own, independent of `mergeable`.

    The two conflict signals are OR'd: a DIRTY merge state must block even when
    `mergeable` has not resolved to CONFLICTING yet.
    """
    pr = {"state": "OPEN", "mergeable": "UNKNOWN", "mergeStateStatus": "DIRTY"}
    ok, reason = _evaluate_preconditions(pr)
    assert ok is False
    assert reason != ""


# ---------------------------------------------------------------------------
# `klartext converge` — pure guard logic (ADR-0012: guarded voluntary convergence)
#
# The live git fetch/rebase is gated end-to-end against real temp repos in
# api/tests/infrastructure/test_converge.py. Here we pin the pure decisions the
# guards hang on: what counts as a home branch, what counts as clean, and which
# action a (branch, clean, behind) triple resolves to.
# ---------------------------------------------------------------------------


def test_is_home_branch_true_for_agent_slug() -> None:
    """Expects `agent/<slug>` to be recognised as a home branch (the converge target)."""
    assert _is_home_branch("agent/devops") is True


def test_is_home_branch_false_for_feature_branch() -> None:
    """Expects a feature branch (feat/…) to be rejected — converge never touches it (ADR §B)."""
    assert _is_home_branch("feat/klartext-converge") is False


def test_is_home_branch_false_for_nested_under_agent() -> None:
    """Expects `agent/<slug>/<more>` to be rejected — only the exact `agent/<slug>` is home."""
    assert _is_home_branch("agent/devops/experiment") is False


def test_is_home_branch_false_for_main() -> None:
    """Expects `main` to be rejected — the home branch is an agent branch, not main itself."""
    assert _is_home_branch("main") is False


def test_worktree_clean_for_empty_porcelain() -> None:
    """Expects an empty `git status --porcelain` to count as clean."""
    assert _is_worktree_clean("") is True


def test_worktree_clean_ignores_untracked_venv() -> None:
    """Expects an untracked `api/.venv` (the symlinked venv) to be ignored — still clean.

    Every worktree carries an untracked `api/.venv` symlink; it must never count as WIP.
    """
    assert _is_worktree_clean("?? api/.venv\n") is True


def test_worktree_dirty_for_modified_file() -> None:
    """Expects a modified tracked file to count as dirty (WIP must block convergence)."""
    assert _is_worktree_clean(" M api/cli.py\n") is False


def test_worktree_dirty_for_other_untracked_file() -> None:
    """Expects an untracked file other than api/.venv to count as dirty."""
    assert _is_worktree_clean("?? scratch.py\n") is False


def test_worktree_dirty_mixes_venv_and_real_change() -> None:
    """Expects dirty when api/.venv is untracked AND a real change exists — the real change wins."""
    assert _is_worktree_clean("?? api/.venv\n M api/cli.py\n") is False


def test_converge_skips_feature_branch() -> None:
    """Expects SKIP_NOT_HOME_BRANCH on a feature branch even when behind — never touch it."""
    assert (
        _converge_decision("feat/x", is_clean=True, commits_behind=5)
        == ConvergeAction.SKIP_NOT_HOME_BRANCH
    )


def test_converge_skips_feature_branch_even_if_dirty() -> None:
    """Expects the home-branch guard to take precedence over the dirty guard on a feature branch."""
    assert (
        _converge_decision("feat/x", is_clean=False, commits_behind=5)
        == ConvergeAction.SKIP_NOT_HOME_BRANCH
    )


def test_converge_skips_dirty_home_branch() -> None:
    """Expects SKIP_DIRTY on a home branch with WIP — convergence must not disturb it (consent)."""
    assert (
        _converge_decision("agent/devops", is_clean=False, commits_behind=3)
        == ConvergeAction.SKIP_DIRTY
    )


def test_converge_already_current_when_not_behind() -> None:
    """Expects ALREADY_CURRENT on a clean home branch with 0 commits behind — idempotent no-op."""
    assert (
        _converge_decision("agent/devops", is_clean=True, commits_behind=0)
        == ConvergeAction.ALREADY_CURRENT
    )


def test_converge_syncs_clean_home_branch_behind() -> None:
    """Expects SYNC on a clean home branch that is behind main — the one case that rebases."""
    assert (
        _converge_decision("agent/devops", is_clean=True, commits_behind=3) == ConvergeAction.SYNC
    )


def test_parse_worktree_list_extracts_paths() -> None:
    """Expects the worktree paths to be pulled from `git worktree list --porcelain` output."""
    porcelain = (
        "worktree /a/main\nHEAD aaa\nbranch refs/heads/agent/devops\n\n"
        "worktree /a/wt/qa\nHEAD bbb\nbranch refs/heads/agent/qa\n\n"
    )
    assert _parse_worktree_list(porcelain) == [Path("/a/main"), Path("/a/wt/qa")]


def test_parse_worktree_list_empty_is_empty() -> None:
    """Expects empty porcelain output to yield no worktrees."""
    assert _parse_worktree_list("") == []


# ---------------------------------------------------------------------------
# `klartext skills sync` — mirror repo skills into ~/.claude/skills/
#
# The repo is the single source of truth (no second truth-centre). Each skill in
# the source is either a flat `<name>.md` file or a `<name>/` directory (multi-file,
# e.g. qa-review with companion docs). Both map to `<target>/<name>/SKILL.md`. Sync
# is idempotent, marks every managed dir with `.repo-managed`, prunes managed dirs
# whose source disappeared (handles renames like pre-compact→anchor), and never
# touches unmarked foreign/plugin skills. The pure mirror logic is gated here against
# real temp dirs; the command only wires source=repo, target=~/.claude/skills/.
# ---------------------------------------------------------------------------


def test_sync_skills_installs_flat_md_as_skill_dir(tmp_path: Path) -> None:
    """Expects a flat `<name>.md` source to install as `<target>/<name>/SKILL.md` with a marker."""
    source = tmp_path / "src"
    target = tmp_path / "dst"
    source.mkdir()
    (source / "tdd.md").write_text("tdd body")

    result = _sync_skills(source, target)

    assert result["tdd"] == SkillsSyncAction.INSTALLED
    assert (target / "tdd" / "SKILL.md").read_text() == "tdd body"
    assert (target / "tdd" / ".repo-managed").exists()


def test_sync_skills_installs_directory_skill_with_companions(tmp_path: Path) -> None:
    """Expects a `<name>/` source directory to copy SKILL.md plus its companion files."""
    source = tmp_path / "src"
    target = tmp_path / "dst"
    (source / "qa-review").mkdir(parents=True)
    (source / "qa-review" / "SKILL.md").write_text("qa main")
    (source / "qa-review" / "report-format.md").write_text("report fmt")

    result = _sync_skills(source, target)

    assert result["qa-review"] == SkillsSyncAction.INSTALLED
    assert (target / "qa-review" / "SKILL.md").read_text() == "qa main"
    assert (target / "qa-review" / "report-format.md").read_text() == "report fmt"
    assert (target / "qa-review" / ".repo-managed").exists()


def test_sync_skills_is_idempotent(tmp_path: Path) -> None:
    """Expects a second sync of unchanged sources to report UNCHANGED and keep content intact."""
    source = tmp_path / "src"
    target = tmp_path / "dst"
    source.mkdir()
    (source / "tdd.md").write_text("tdd body")

    _sync_skills(source, target)
    result = _sync_skills(source, target)

    assert result["tdd"] == SkillsSyncAction.UNCHANGED
    assert (target / "tdd" / "SKILL.md").read_text() == "tdd body"


def test_sync_skills_updates_changed_content(tmp_path: Path) -> None:
    """Expects a changed source to overwrite the installed skill and report UPDATED."""
    source = tmp_path / "src"
    target = tmp_path / "dst"
    source.mkdir()
    skill = source / "tdd.md"
    skill.write_text("old body")
    _sync_skills(source, target)

    skill.write_text("new body")
    result = _sync_skills(source, target)

    assert result["tdd"] == SkillsSyncAction.UPDATED
    assert (target / "tdd" / "SKILL.md").read_text() == "new body"


def test_sync_skills_prunes_managed_skill_whose_source_disappeared(tmp_path: Path) -> None:
    """Expects a managed target dir with no matching source to be pruned (e.g. a rename)."""
    source = tmp_path / "src"
    target = tmp_path / "dst"
    source.mkdir()
    (source / "anchor.md").write_text("anchor body")
    # An earlier sync left `pre-compact` managed; it is gone from the source now.
    stale = target / "pre-compact"
    stale.mkdir(parents=True)
    (stale / "SKILL.md").write_text("old skill")
    (stale / ".repo-managed").write_text("")

    result = _sync_skills(source, target)

    assert result["pre-compact"] == SkillsSyncAction.PRUNED
    assert not stale.exists()
    assert (target / "anchor" / "SKILL.md").read_text() == "anchor body"


def test_sync_skills_empty_source_does_not_prune_managed_targets(tmp_path: Path) -> None:
    """Expects an empty (but existing) source to prune nothing — same wipe guard as a missing one.

    An empty source yields zero skills; that must not be read as 'every skill deleted'. The prune
    step only follows a non-empty source, so already-installed managed skills survive untouched.
    """
    source = tmp_path / "src"
    target = tmp_path / "dst"
    source.mkdir()  # exists but holds no skills
    managed = target / "tdd"
    managed.mkdir(parents=True)
    (managed / "SKILL.md").write_text("tdd body")
    (managed / ".repo-managed").write_text("")

    result = _sync_skills(source, target)

    assert "tdd" not in result
    assert managed.exists()
    assert (managed / "SKILL.md").read_text() == "tdd body"


def test_sync_skills_leaves_foreign_skill_untouched(tmp_path: Path) -> None:
    """Expects an unmarked (plugin/foreign) target dir to be left untouched — never pruned."""
    source = tmp_path / "src"
    target = tmp_path / "dst"
    source.mkdir()
    (source / "tdd.md").write_text("tdd body")
    # A foreign skill (no `.repo-managed` marker) must survive a sync untouched.
    foreign = target / "superpowers-skill"
    foreign.mkdir(parents=True)
    (foreign / "SKILL.md").write_text("plugin skill")

    result = _sync_skills(source, target)

    assert "superpowers-skill" not in result
    assert (foreign / "SKILL.md").read_text() == "plugin skill"


def test_sync_skills_nonexistent_source_does_not_prune_managed_targets(tmp_path: Path) -> None:
    """Expects a missing source dir to be treated as 'no sources', NOT as 'every skill deleted'.

    A vanished/mis-wired source path must not be read as an instruction to wipe every
    repo-managed skill out of ~/.claude/skills/. This guards against a path typo nuking
    the install. If the code prunes here, that is a destructive bug.
    """
    source = tmp_path / "does-not-exist"
    target = tmp_path / "dst"
    managed = target / "tdd"
    managed.mkdir(parents=True)
    (managed / "SKILL.md").write_text("tdd body")
    (managed / ".repo-managed").write_text("")

    result = _sync_skills(source, target)

    assert "tdd" not in result
    assert managed.exists(), "a missing source must not prune already-installed managed skills"
    assert (managed / "SKILL.md").read_text() == "tdd body"


# ---------------------------------------------------------------------------
# "landed?" verdict: did a ref's work reach origin/main? Distinguishes SHA-
# reachability from content-presence — the squash-merge trap (a squash gets a
# NEW sha on main, so the branch commit is never reachable, yet its content is
# fully present). Reasoning by `--contains` alone reports landed work as orphaned.
# ---------------------------------------------------------------------------


def test_landed_verdict_reports_sha_when_commit_reachable_from_main() -> None:
    """Expects LANDED_BY_SHA when the ref is reachable from main (merge-commit / fast-forward)."""
    assert _landed_verdict(sha_contained=True, changes_in_main=True) == LandedStatus.LANDED_BY_SHA


def test_landed_verdict_reports_sha_even_when_main_moved_on() -> None:
    """Expects LANDED_BY_SHA when the ref is reachable but main has advanced past it.

    Reachability is the stronger statement: the ref's work is in main regardless of a non-empty
    diff caused by main moving on afterwards.
    """
    assert _landed_verdict(sha_contained=True, changes_in_main=False) == LandedStatus.LANDED_BY_SHA


def test_landed_verdict_reports_content_when_squash_merged_sha_absent() -> None:
    """Expects LANDED_BY_CONTENT when the SHA is absent from main but the content is fully present.

    The squash-merge trap: a squash-merged branch commit gets a new SHA on main, so it is never
    reachable (sha_contained False), yet `git diff <ref> origin/main` is empty. This is the exact
    false conclusion (f0fc0b6 read as orphaned, though landed via #120) this verdict guards against.
    """
    assert (
        _landed_verdict(sha_contained=False, changes_in_main=True) == LandedStatus.LANDED_BY_CONTENT
    )


def test_landed_verdict_reports_not_landed_when_content_differs() -> None:
    """Expects NOT_LANDED when the ref is neither reachable from nor content-subsumed by main."""
    assert _landed_verdict(sha_contained=False, changes_in_main=False) == LandedStatus.NOT_LANDED
