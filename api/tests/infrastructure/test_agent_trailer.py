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
