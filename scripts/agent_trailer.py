#!/usr/bin/env python3
"""ADR-0014 agent-provenance trailer — validate/add `Agent: <slug>` on commits.

Closes the git half of the one-identity model: every agent commit carries an `Agent: <slug>`
trailer (slug = the `agents/<name>/` directory name = the SSOT), spawn-aware as
`Agent: <lead> (spawned <task>)`. Used two ways, both calling the same pure validation:

  * **commit-msg hook** (`main`): at commit time, validate the message; if the trailer is absent and
    the committing agent is derivable from the worktree, **inject** `Agent: <slug>`; otherwise fail
    with a copy-pasteable fix. The committing agent = the worktree basename (same rule as
    `load_agent_identity.py`); a non-agent worktree (main checkout / CI / a clone) is not an agent
    commit — its bypass is the explicit, visible `Agent: human` trailer.
  * **CI check** (`.github/workflows/agent-provenance.yml`): reject a Way-of-Working commit whose
    message lacks a well-formed trailer.

DevOps build-time rulings for ADR-0014's open questions: slug source = `agents/*`; bypass = explicit
`Agent: human`; logic lives here (no `klartext commit` wrapper). SA owns the rule; this is the mechanism.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# A trailer line: `Agent: <slug>` optionally `(spawned <task>)`. Slug charset matches agent dir names
# (lowercase, digits, hyphens — e.g. `system-architect`, `causal-model`).
_TRAILER_RE = re.compile(
    r"^Agent:[ ](?P<slug>[a-z0-9-]+)(?:[ ]\(spawned[ ].+\))?[ ]*$", re.MULTILINE
)

# Explicit, visible bypass for a genuine non-agent (human / main-checkout) commit.
BYPASS_SLUGS: frozenset[str] = frozenset({"human"})


def valid_agent_slugs(repo_root: Path) -> set[str]:
    """Returns the set of agent slugs — the `agents/<name>/` directory names (the SSOT)."""
    agents = repo_root / "agents"
    if not agents.is_dir():
        return set()
    return {d.name for d in agents.iterdir() if d.is_dir()}


def derive_slug(worktree_name: str, valid_slugs: set[str]) -> str | None:
    """Returns the committing agent's slug from the worktree basename, or None if it is not an agent."""
    return worktree_name if worktree_name in valid_slugs else None


def trailer_violation(message: str, valid_slugs: set[str]) -> str | None:
    """Returns a violation string if `message` lacks a well-formed `Agent:` trailer, else None.

    Well-formed = at least one `Agent: <slug>` line whose slug is a known agent or the `human` bypass.
    """
    allowed = valid_slugs | BYPASS_SLUGS
    matches = _TRAILER_RE.findall(message)
    if not matches:
        return (
            "missing the ADR-0014 provenance trailer. Add a footer line "
            "`Agent: <your-slug>` (or `Agent: <lead> (spawned <task>)`); "
            "non-agent commits use `Agent: human`."
        )
    unknown = [slug for slug in matches if slug not in allowed]
    if unknown:
        return (
            f"unknown agent slug(s) in the `Agent:` trailer: {', '.join(sorted(set(unknown)))}. "
            f"Valid: {', '.join(sorted(allowed))}."
        )
    return None


def _inject_trailer(message: str, slug: str) -> str:
    """Appends `Agent: <slug>` as a footer trailer, on a trailing line (blank-line-separated if needed)."""
    body = message.rstrip("\n")
    # Keep the trailer in the footer block: if the last non-empty line is already a trailer
    # (`Key: value`), append directly; otherwise separate the footer with a blank line.
    last = body.splitlines()[-1] if body.splitlines() else ""
    sep = "\n" if re.match(r"^[A-Za-z-]+:[ ]", last) else "\n\n"
    return f"{body}{sep}Agent: {slug}\n"


def main(argv: list[str] | None = None) -> int:
    """commit-msg hook: validate the message file; inject the trailer when the agent is derivable.

    Usage: `agent_trailer.py <commit-msg-file>`. Returns 0 when the message ends well-formed (after a
    possible injection), 1 with a copy-pasteable fix when it cannot be made well-formed automatically.
    """
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: agent_trailer.py <commit-msg-file>", file=sys.stderr)
        return 2
    repo_root = Path(__file__).resolve().parents[1]
    msg_file = Path(argv[0])
    message = msg_file.read_text()
    slugs = valid_agent_slugs(repo_root)

    if trailer_violation(message, slugs) is None:
        return 0  # already well-formed

    # Absent/malformed: inject if we can derive the committing agent from the worktree.
    slug = derive_slug(Path.cwd().name, slugs)
    if slug is not None and not _TRAILER_RE.search(message):
        msg_file.write_text(_inject_trailer(message, slug))
        return 0

    violation = trailer_violation(message, slugs)
    print(f"✗  commit-msg: {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
