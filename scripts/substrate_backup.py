#!/usr/bin/env python3
"""F2 substrate backup — out-of-band rollback for the method/product refactoring.

The git axis covers versioned code; the **substrate** (team memory + inbox + the MEMORY.md index +
non-`.md` markers) lives outside git and is touched by F3. This script captures it before the rebuild.

OE-ratified scope (2026-06-16): the **whole tree** `~/.claude/klartext-team-memory/` byte-for-byte —
**not** a `*.md` glob. The root holds a non-`.md` marker (`compact-log-lastcheck`) that a glob would
silently drop, and any future non-`.md` file too; whole-tree is the robust, drift-proof invariant.

Target: `~/klartext-substrate-backups/<UTC-timestamp>/` — outside every git worktree and outside
`~/.claude`. **Fail-loud**: a missing source or an unwritable base raises rather than producing a
silent empty backup. Restore + tested-valid verification live in `substrate_restore.py`.
"""

from __future__ import annotations

import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path


def _team_memory_dir() -> Path:
    """Returns the live substrate root (the pinned shared team memory)."""
    return Path.home() / ".claude" / "klartext-team-memory"


def _default_backup_base() -> Path:
    """Returns the external backup base — outside every worktree and outside ~/.claude."""
    return Path.home() / "klartext-substrate-backups"


def backup_substrate(
    source: Path, dest_base: Path, *, timestamp: str | None = None
) -> Path:
    """Copies the whole substrate tree byte-for-byte into dest_base/<timestamp>/ and returns the path.

    Whole-tree (`shutil.copytree`) — never an extension-filtered subset — so non-`.md` markers and any
    future files travel with it. Fail-loud: raises FileNotFoundError if the source does not exist.
    """
    if not source.is_dir():
        raise FileNotFoundError(f"substrate source does not exist: {source}")
    stamp = timestamp or datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    backup = dest_base / stamp
    # copytree creates dest_base + backup; a non-writable base raises here (fail-loud), not silently.
    shutil.copytree(source, backup)
    return backup


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: backs up the live substrate to the external base, prints the path, returns 0/1."""
    source = _team_memory_dir()
    if not source.is_dir():
        print(f"✗  substrate not found: {source}", file=sys.stderr)
        return 1
    backup = backup_substrate(source, _default_backup_base())
    print(f"✓  substrate backed up → {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
