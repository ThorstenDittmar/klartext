"""Infrastructure test: the Classification Gate concurrency group is keyed on the PR head SHA.

A ref-keyed concurrency group (refs/pull/N/merge is identical across a PR's SHAs) makes a
`gh pr update-branch` cancel the prior SHA's run, leaving a CANCELLED entry for this REQUIRED
check that blocks the merge (ambiguous required status) even though the new run is green —
observed 3× on 2026-06-19 (#179, #191, #198). The fix keys the group on the head SHA so a new
commit never cancels the old run.

This guard enforces the fix (ADR-0006: a rule needs an automated check) so a future edit can't
silently regress the group back to a ref-only key and reintroduce the BLOCKED-despite-green bug.
"""

from __future__ import annotations

import re
from pathlib import Path

_WORKFLOW = Path(__file__).parents[3] / ".github" / "workflows" / "classify-gate.yml"


def _concurrency_group() -> str:
    """Returns the `group:` expression from the workflow's top-level concurrency block."""
    text = _WORKFLOW.read_text()
    pattern = r"^concurrency:\n(?:[ \t]+.*\n)*?[ \t]+group:[ \t]*(?P<group>.+)$"
    match = re.search(pattern, text, re.M)
    assert match, "could not find a top-level concurrency.group in classify-gate.yml"
    return match.group("group").strip()


def _concurrency_block() -> str:
    """Returns the full top-level concurrency block (group + cancel-in-progress) text."""
    text = _WORKFLOW.read_text()
    pattern = r"^concurrency:\n(?P<block>(?:[ \t]+.*\n)+)"
    match = re.search(pattern, text, re.M)
    assert match, "could not find a top-level concurrency block in classify-gate.yml"
    return match.group("block")


def test_concurrency_group_is_keyed_on_head_sha() -> None:
    """Expects the concurrency group to include the PR head SHA, not only the ref.

    Per-SHA keying is what stops update-branch from cancelling the prior run and leaving a
    cancelled required-check status that blocks the merge.
    """
    group = _concurrency_group()
    assert "head.sha" in group, (
        f"classify-gate concurrency group must be keyed on the PR head SHA to avoid the "
        f"cancelled-required-check BLOCKED bug; got: {group}"
    )


def test_concurrency_group_does_not_key_on_ref_alone() -> None:
    """Expects the group NOT to be the ref-only key that caused the cross-SHA cancellation bug."""
    group = _concurrency_group()
    ref_only = group.endswith("github.ref }}") and "head.sha" not in group
    assert not ref_only, f"ref-only concurrency key reintroduces the BLOCKED bug: {group}"


def test_concurrency_cancels_in_progress() -> None:
    """Expects cancel-in-progress: true so a same-SHA rerun supersedes the prior run.

    Green regression guard. Per-SHA keying only dedups redundant runs on the same commit if
    cancel-in-progress stays on; with it off, two runs for the same SHA would race instead.
    """
    block = _concurrency_block()
    assert re.search(r"^[ \t]+cancel-in-progress:[ \t]*true[ \t]*$", block, re.M), (
        f"classify-gate concurrency must keep cancel-in-progress: true; got block:\n{block}"
    )


def test_gate_has_no_path_filter() -> None:
    """Expects the trigger to carry no `paths:`/`paths-ignore:` filter.

    Green regression guard. As a REQUIRED check the job must always run and report a status;
    a path filter would skip it on unrelated PRs, and a skipped required check blocks merge
    forever. The script itself decides applicability (non-WoW PRs pass instantly).
    """
    text = _WORKFLOW.read_text()
    assert not re.search(r"^[ \t]+paths(?:-ignore)?:", text, re.M), (
        "classify-gate must have no path filter — a skipped required check blocks merge forever"
    )
