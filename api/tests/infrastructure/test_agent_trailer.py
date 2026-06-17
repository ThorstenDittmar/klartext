"""Infrastructure tests: the ADR-0014 agent-provenance trailer (`scripts/agent_trailer.py`).

ADR-0014 closes the git half of the one-identity model: every agent commit carries an
`Agent: <slug>` trailer (slug = the `agents/<name>/` directory name, the SSOT), spawn-aware as
`Agent: <lead> (spawned <task>)`. A commit-msg hook adds/validates it at commit time and a CI
check rejects a WoW commit without a well-formed trailer.

DevOps build-time rulings (ADR-0014 "Open questions"):
- **slug source** = `agents/*` dir names; the **committing agent** is derived from the worktree
  basename (same rule as `load_agent_identity.py`); a non-agent worktree (main checkout / CI) is not
  an agent commit.
- **bypass** for genuine non-agent commits = the explicit, visible `Agent: human` trailer.
- the pure validation lives here (testable); the hook + CI call it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import agent_trailer as at  # noqa: E402

_SLUGS = {"devops", "oe", "qa", "system-architect", "causal-model"}


def test_well_formed_trailer_passes() -> None:
    """Expects a plain `Agent: <slug>` with a valid slug to be well-formed (no violation)."""
    msg = "feat: do a thing\n\nbody\n\nCo-Authored-By: x <y>\nAgent: devops\n"
    assert at.trailer_violation(msg, _SLUGS) is None


def test_spawn_aware_trailer_passes() -> None:
    """Expects the spawn-aware `Agent: <lead> (spawned <task>)` form to be well-formed."""
    msg = "docs: extract\n\nAgent: oe (spawned f3-skill-relocation)\n"
    assert at.trailer_violation(msg, _SLUGS) is None


def test_missing_trailer_is_violation() -> None:
    """Expects a commit with no Agent trailer to be flagged with an actionable message."""
    msg = "fix: something\n\nCo-Authored-By: x <y>\n"
    violation = at.trailer_violation(msg, _SLUGS)
    assert violation is not None
    assert "Agent:" in violation


def test_unknown_slug_is_violation() -> None:
    """Expects an Agent trailer whose slug is not a known agent (or bypass) to be flagged."""
    msg = "feat: x\n\nAgent: bogus\n"
    violation = at.trailer_violation(msg, _SLUGS)
    assert violation is not None
    assert "bogus" in violation


def test_hyphenated_slug_passes() -> None:
    """Expects a hyphenated agent slug (system-architect) to be accepted."""
    assert at.trailer_violation("x\n\nAgent: system-architect\n", _SLUGS) is None


def test_human_bypass_passes() -> None:
    """Expects the explicit `Agent: human` bypass for a genuine non-agent commit to pass."""
    assert at.trailer_violation("chore: manual\n\nAgent: human\n", _SLUGS) is None


def test_valid_agent_slugs_reads_agents_dir() -> None:
    """Expects the valid-slug set to come from the real `agents/*` directories (the SSOT)."""
    slugs = at.valid_agent_slugs(_REPO_ROOT)
    assert {"devops", "oe", "qa", "system-architect"} <= slugs
    assert "klartext" not in slugs  # the main-checkout basename is not an agent


def test_derive_slug_from_agent_worktree() -> None:
    """Expects the committing agent to be derived from an agent worktree's basename."""
    assert at.derive_slug("devops", _SLUGS) == "devops"


def test_derive_slug_none_for_non_agent_worktree() -> None:
    """Expects a non-agent worktree (main checkout) to derive no agent slug."""
    assert at.derive_slug("klartext", _SLUGS) is None


# --- malformed Agent: lines that must NOT count as a well-formed trailer ----------------


def test_agent_line_without_slug_is_violation() -> None:
    """Expects a bare `Agent:` line with no slug to NOT satisfy the trailer (still a violation)."""
    assert at.trailer_violation("feat: x\n\nAgent:\n", _SLUGS) is not None


def test_agent_line_with_only_trailing_space_is_violation() -> None:
    """Expects `Agent: ` (slug position empty) to NOT satisfy the trailer."""
    assert at.trailer_violation("feat: x\n\nAgent: \n", _SLUGS) is not None


def test_uppercase_slug_is_violation() -> None:
    """Expects an uppercase slug (charset is lowercase/digits/hyphen) to NOT match the trailer."""
    assert at.trailer_violation("feat: x\n\nAgent: DEVOPS\n", _SLUGS) is not None


def test_slug_with_trailing_junk_is_violation() -> None:
    """Expects junk after the slug (`Agent: devops xyz`) to NOT count as a well-formed trailer."""
    assert at.trailer_violation("feat: x\n\nAgent: devops xyz\n", _SLUGS) is not None


def test_underscore_slug_is_violation() -> None:
    """Expects an underscore slug (`causal_model`) to NOT match — dir names use hyphens."""
    assert at.trailer_violation("feat: x\n\nAgent: causal_model\n", _SLUGS) is not None


def test_agent_inline_in_prose_is_violation() -> None:
    """Expects `Agent: <slug>` embedded mid-line in prose to NOT count (must be a line start)."""
    assert at.trailer_violation("feat Agent: devops in subject\n\nbody\n", _SLUGS) is not None


# --- multiple trailers: all must be valid -----------------------------------------------


def test_multiple_trailers_one_invalid_is_violation() -> None:
    """Expects a message with one valid and one unknown Agent trailer to be flagged (strict-all)."""
    violation = at.trailer_violation("feat: x\n\nAgent: devops\nAgent: bogus\n", _SLUGS)
    assert violation is not None
    assert "bogus" in violation


# --- valid_agent_slugs: no agents/ dir --------------------------------------------------


def test_valid_agent_slugs_empty_when_no_agents_dir() -> None:
    """Expects valid_agent_slugs to return an empty set when the repo has no `agents/` directory."""
    with tempfile.TemporaryDirectory() as tmp:
        assert at.valid_agent_slugs(Path(tmp)) == set()


# --- _inject_trailer placement ----------------------------------------------------------


def test_inject_after_prose_separates_with_blank_line() -> None:
    """Expects injection after a prose body to add a blank-line-separated footer trailer."""
    result = at._inject_trailer("feat: x\n\nbody text", "devops")
    assert result == "feat: x\n\nbody text\n\nAgent: devops\n"


def test_inject_after_existing_trailer_block_appends_directly() -> None:
    """Expects injection after an existing `Key: value` trailer to append without a blank line."""
    result = at._inject_trailer("feat: x\n\nCo-Authored-By: a <b>", "devops")
    assert result == "feat: x\n\nCo-Authored-By: a <b>\nAgent: devops\n"


# --- main(): inject and fail paths ------------------------------------------------------


def test_main_injects_trailer_for_agent_worktree(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Expects main() to inject `Agent: <slug>` and exit 0 when cwd basename is a real agent."""
    with tempfile.TemporaryDirectory() as tmp:
        worktree = Path(tmp) / "devops"
        worktree.mkdir()
        msg_file = worktree / "COMMIT_EDITMSG"
        msg_file.write_text("feat: thing\n\nbody\n")
        monkeypatch.chdir(worktree)
        rc = at.main([str(msg_file)])
        result = msg_file.read_text()
    assert rc == 0
    assert result == "feat: thing\n\nbody\n\nAgent: devops\n"


def test_main_fails_for_non_agent_worktree(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Expects main() to exit 1 and leave the message untouched for a non-agent worktree."""
    with tempfile.TemporaryDirectory() as tmp:
        worktree = Path(tmp) / "klartext"
        worktree.mkdir()
        msg_file = worktree / "COMMIT_EDITMSG"
        msg_file.write_text("chore: manual\n\nbody\n")
        monkeypatch.chdir(worktree)
        rc = at.main([str(msg_file)])
        result = msg_file.read_text()
    assert rc == 1
    assert result == "chore: manual\n\nbody\n"
