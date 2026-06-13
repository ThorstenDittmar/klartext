#!/usr/bin/env python3
"""SessionStart hook: inject the agent's Hoheitswissen into the session context.

ADR-0011 G1. On session start — and on ``/clear``, which the Claude desktop app reports as
``source=startup`` — this loads ``agents/<slug>/claude.md`` (slug = basename of the worktree /
``CLAUDE_PROJECT_DIR``) and emits it as SessionStart ``additionalContext``, so an app session
knows its identity without a ``start-agent.sh`` launcher. This replaces the previous manual
convention "every agent reads its claude.md at session start" with a mechanical guarantee.

Behaviour:
- agent worktree (``agents/<slug>/claude.md`` exists) -> inject preamble + full file content
- any other directory (main checkout, clones, CI) -> no output, exit 0 (graceful no-op)

Only the preamble is wrapped in ``EXTREMELY_IMPORTANT`` (OE identity wording); the file content
follows below, clearly delimited, so the strongest tag is not diluted over kilobytes of prose.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_RULE = "─" * 40

_PREAMBLE = """<EXTREMELY_IMPORTANT>
You are the **{slug}** agent in the klartext multi-agent system. The document below is your
Hoheitswissen — your sovereign knowledge: who you are, the domain you own, the files you may
write, and your domain-specific rules. It is authoritative and binding for this entire session,
and it is injected here in full — you do not need to open the file.

Two boundaries override convenience and even your own capability:

1. Stay inside your domain. Do not create, modify, or delete files outside your declared
   write-access — not even when you easily could. Work that belongs to another agent is not
   yours to do: formulate a briefing for the responsible agent and hand it to the user, who
   decides whether to route it. Offering out-of-domain work undermines the clarity of the system.

2. This is the agent layer on top of the project CLAUDE.md. Where your Hoheitswissen is silent,
   the project CLAUDE.md and the user's explicit instructions govern. User instructions always
   take precedence.

Act as the {slug} agent from your first response onward.
</EXTREMELY_IMPORTANT>"""


def _project_dir() -> Path:
    """Returns the project root — CLAUDE_PROJECT_DIR if set, else the current working directory."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def build_context(project_dir: Path) -> str | None:
    """Builds the SessionStart additionalContext for project_dir.

    Returns None if project_dir is not an agent worktree (no agents/<slug>/claude.md),
    so the caller emits nothing and the hook is a graceful no-op.
    """
    slug = project_dir.name
    claude_md = project_dir / "agents" / slug / "claude.md"
    if not claude_md.is_file():
        return None
    content = claude_md.read_text(encoding="utf-8")
    header = f"\n\n{_RULE}\nYour Hoheitswissen (agents/{slug}/claude.md):\n{_RULE}\n"
    return _PREAMBLE.format(slug=slug) + header + content


def main() -> int:
    """Emits the SessionStart additionalContext JSON, or nothing for a non-agent directory."""
    context = build_context(_project_dir())
    if context is None:
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
