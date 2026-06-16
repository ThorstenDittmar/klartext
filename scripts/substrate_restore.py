#!/usr/bin/env python3
"""F2 substrate restore + tested-valid verification (out-of-band rollback for the refactoring).

Restores a backup produced by `substrate_backup.py` and verifies a restore is **tested-valid** per
OE's ratified criterion (2026-06-16): a restore counts only when

  * **(a) C4 index-integrity** — every MEMORY.md entry points at a real file, no duplicates (reused
    from `session_health.check_index_integrity`, #133 — the one contract check, no second C4);
  * **(b) byte-identity** — the whole restored tree is byte-for-byte the source (the real guarantee;
    catches a dropped non-`.md` marker, a truncated file, a missing inbox message);
  * **(c) inbox completeness per slug** — the per-slug message counts (incl. `.read/` archive) match
    (kept explicit as a regression net over the highest-churn part, even though (b) subsumes it).

`Backup → restore-to-sandbox → verify_restore == []` is the hard precondition before F3 may touch the
live substrate. Fail-loud: restoring a missing backup raises.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from session_health import check_index_integrity  # noqa: E402


def restore_substrate(backup: Path, target: Path) -> None:
    """Restores a backup tree to `target` byte-for-byte. Fail-loud if the backup is missing."""
    if not backup.is_dir():
        raise FileNotFoundError(f"backup does not exist: {backup}")
    shutil.copytree(backup, target)


def _relative_files(root: Path) -> set[str]:
    """Returns every file path under `root`, relative and POSIX-formatted."""
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def _byte_identity_violations(source: Path, restored: Path) -> list[str]:
    """(b) Returns a violation per file that is missing, extra, or byte-different in the restore."""
    violations: list[str] = []
    source_files = _relative_files(source)
    restored_files = _relative_files(restored)
    for rel in sorted(source_files - restored_files):
        violations.append(f"(b) byte-identity: {rel} missing from the restore")
    for rel in sorted(restored_files - source_files):
        violations.append(
            f"(b) byte-identity: {rel} is in the restore but not the source"
        )
    for rel in sorted(source_files & restored_files):
        if (source / rel).read_bytes() != (restored / rel).read_bytes():
            violations.append(f"(b) byte-identity: {rel} differs from the source")
    return violations


def _inbox_counts(root: Path) -> dict[str, tuple[int, int]]:
    """Returns {slug: (unread_count, read_archive_count)} for every inbox slug under `root`."""
    counts: dict[str, tuple[int, int]] = {}
    inbox = root / "inbox"
    if not inbox.is_dir():
        return counts
    for slug in sorted(p for p in inbox.iterdir() if p.is_dir()):
        unread = len(list(slug.glob("*.md")))
        read = (
            len(list((slug / ".read").glob("*.md"))) if (slug / ".read").is_dir() else 0
        )
        counts[slug.name] = (unread, read)
    return counts


def _inbox_completeness_violations(source: Path, restored: Path) -> list[str]:
    """(c) Returns a violation per inbox slug whose unread/read-archive counts drifted in the restore."""
    violations: list[str] = []
    source_counts = _inbox_counts(source)
    restored_counts = _inbox_counts(restored)
    for slug in sorted(set(source_counts) | set(restored_counts)):
        if source_counts.get(slug, (0, 0)) != restored_counts.get(slug, (0, 0)):
            violations.append(
                f"(c) inbox completeness: slug '{slug}' counts differ "
                f"(source {source_counts.get(slug, (0, 0))}, restore {restored_counts.get(slug, (0, 0))})"
            )
    return violations


def verify_restore(source: Path, restored: Path) -> list[str]:
    """Returns all tested-valid violations (a)∧(b)∧(c) for a restore; empty list = tested-valid.

    (a) reuses session_health's C4 on the restored tree; (b) byte-identity over the whole tree;
    (c) per-slug inbox completeness. The repo root supplies C4's project gate.
    """
    violations: list[str] = []
    c4 = check_index_integrity(_REPO_ROOT, restored)
    if c4:
        violations.append(f"(a) {c4}")
    violations.extend(_byte_identity_violations(source, restored))
    violations.extend(_inbox_completeness_violations(source, restored))
    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: `substrate_restore.py <backup> <target>` — restores, then returns 0/1."""
    if not argv:
        argv = sys.argv[1:]
    if len(argv) != 2:
        print("usage: substrate_restore.py <backup-dir> <target-dir>", file=sys.stderr)
        return 2
    backup, target = Path(argv[0]), Path(argv[1])
    restore_substrate(backup, target)
    print(f"✓  restored {backup} → {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
