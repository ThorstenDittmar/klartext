"""Unit tests for the pure decision logic behind `klartext merge`.

The live gh/git calls in the merge command are not headless-testable, but the
decisions they hang on are pure functions and gated here: which merge methods
are allowed, how a set of CI check states collapses to one verdict, and whether
a PR's state permits merging.
"""

from __future__ import annotations

import pytest
import typer

from api.cli import _evaluate_checks, _evaluate_preconditions, _validate_merge_method

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
