#!/usr/bin/env python3
"""SessionStart hook: drift warning — "verify current before resume".

ADR-0012 detection half + the Controlled-Method-Rollout practice. A fail-soft, **non-blocking**
check run at session start (and ``/clear``): if the worktree is behind ``origin/main``, it warns —
pointing at ``klartext converge`` — so a session does not resume work on a stale substrate. It
**never** blocks or fails a session: any error, or an unreachable remote, exits 0 with no output.

Stdlib only, runs under system ``python3``. The detection sharpness is behind a ``DriftSignal``
port (L1 = commit-count) so a later L2 (shared-layer-weighted) is an adapter swap, not a rewrite.

Behaviour:
- worktree behind origin/main -> emit a SessionStart additionalContext warning
- up to date / not a git repo / offline / any error -> no output, exit 0 (graceful)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DriftContext:
    """What a drift signal judges: how far behind, and which paths changed (for a future L2)."""

    commits_behind: int
    changed_paths: tuple[str, ...] = ()


class DriftSignal(ABC):
    """Port: decides whether a worktree's drift warrants a warning."""

    @abstractmethod
    def should_warn(self, ctx: DriftContext) -> bool:
        """Returns True if the drift described by ctx should produce a warning."""


class CommitCountDrift(DriftSignal):
    """L1 adapter: warn on any commits behind (coarse). L2 would weigh shared-layer paths."""

    def should_warn(self, ctx: DriftContext) -> bool:
        """Warns whenever the worktree is at least one commit behind origin/main."""
        return ctx.commits_behind > 0


def _project_dir() -> Path:
    """Returns the project root — CLAUDE_PROJECT_DIR if set, else the current working directory."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def _git(project_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Runs a git command in project_dir, capturing output. Never raises (check=False)."""
    return subprocess.run(
        ["git", "-C", str(project_dir), *args], capture_output=True, text=True
    )


def assess_drift(project_dir: Path, signal: DriftSignal | None = None) -> str | None:
    """Returns a drift warning for project_dir, or None when current / offline / not assessable.

    Fail-soft by design: a fetch failure (offline) or any git error yields None — the hook stays
    quiet rather than nagging on a state it cannot verify, and never blocks the session.
    """
    signal = signal or CommitCountDrift()
    fetch = _git(project_dir, "fetch", "origin", "--quiet")
    if fetch.returncode != 0:
        return None  # offline / no remote — cannot assess, stay quiet
    behind = _git(project_dir, "rev-list", "--count", "HEAD..origin/main")
    if behind.returncode != 0:
        return None  # no origin/main ref (non-main default) — cannot assess
    count = int(behind.stdout.strip() or "0")
    if not signal.should_warn(DriftContext(commits_behind=count)):
        return None
    plural = "s" if count != 1 else ""
    return (
        f"⚠ Worktree is {count} commit{plural} behind origin/main — the shared way-of-working "
        f"may be stale. Run `klartext converge` before starting new work (it rebases a clean "
        f"home branch and safely skips otherwise)."
    )


def build_warnings(project_dir: Path) -> str | None:
    """Collects all session-health warnings for project_dir, or None if everything is healthy.

    PR2 carries the drift check; the memory-substrate (C1/C3) and Local-mode checks attach here.
    """
    parts = [w for w in (assess_drift(project_dir),) if w]
    return "\n".join(parts) if parts else None


def main() -> int:
    """Emits a SessionStart additionalContext warning if unhealthy. Never fails the session."""
    try:
        warnings = build_warnings(_project_dir())
    except Exception:
        return 0  # fail-soft: a health check must never block a session
    if not warnings:
        return 0
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": warnings,
            }
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
