#!/usr/bin/env python3
"""F2 substrate restore + tested-valid verification (Frozen Plan §6.3, OE-ratified 2026-06-16).

Restores a four-group backup (`substrate_backup.py`) and verifies it is **tested-valid**. A restore
counts only when every group's integrity holds against the backup + manifest:

  * **G1 team-memory/** — (a) C4 index-integrity (reused from `session_health`, #133 — no second C4)
    ∧ (b) byte-identity vs the backup ∧ (c) inbox completeness per slug incl. `.read/`.
  * **G2 claude-user-state/** — (b) byte-identity vs the backup.
  * **G3 secrets/** — (b) byte-identity vs the backup, **confidential-safe**: a mismatch names the
    path only, never the secret bytes.
  * **G4 wip/<worktree>/** — each manifest stash is recoverable: the bundle exists and lists the
    recorded stash commit.
  * **manifest** — present, and the recomputed SHA256 of each tree matches what was recorded.

`Backup → restore-to-sandbox → verify_restore == []` is the hard precondition before F3 may touch the
live substrate. Fail-loud: restoring a missing backup raises.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from session_health import check_index_integrity  # noqa: E402
from substrate_backup import tree_sha256  # noqa: E402


def restore_substrate(backup: Path, target: Path) -> None:
    """Restores a backup tree to `target` byte-for-byte. Fail-loud if the backup is missing."""
    if not backup.is_dir():
        raise FileNotFoundError(f"backup does not exist: {backup}")
    shutil.copytree(backup, target)


def _relative_files(root: Path) -> set[str]:
    """Returns every file path under `root`, relative and POSIX-formatted ('' set if absent)."""
    if not root.is_dir():
        return set()
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def _byte_identity_violations(
    backup: Path, restored: Path, group: str, *, confidential: bool = False
) -> list[str]:
    """(b) Returns violations for files missing/extra/byte-different between backup and restore.

    With confidential=True the messages name the path only — never the differing bytes (G3 secrets).
    """
    violations: list[str] = []
    a, b = backup / group, restored / group
    backup_files, restored_files = _relative_files(a), _relative_files(b)
    for rel in sorted(backup_files - restored_files):
        violations.append(f"(b) {group}: {rel} missing from the restore")
    for rel in sorted(restored_files - backup_files):
        violations.append(f"(b) {group}: {rel} is in the restore but not the backup")
    for rel in sorted(backup_files & restored_files):
        if (a / rel).read_bytes() != (b / rel).read_bytes():
            detail = "" if confidential else " (content differs)"
            violations.append(f"(b) {group}: {rel} differs from the backup{detail}")
    return violations


def _inbox_counts(team_memory: Path) -> dict[str, tuple[int, int]]:
    """Returns {slug: (unread, read_archive)} for every inbox slug under a team-memory tree."""
    counts: dict[str, tuple[int, int]] = {}
    inbox = team_memory / "inbox"
    if not inbox.is_dir():
        return counts
    for slug in sorted(p for p in inbox.iterdir() if p.is_dir()):
        unread = len(list(slug.glob("*.md")))
        read = (
            len(list((slug / ".read").glob("*.md"))) if (slug / ".read").is_dir() else 0
        )
        counts[slug.name] = (unread, read)
    return counts


def _inbox_completeness_violations(backup: Path, restored: Path) -> list[str]:
    """(c) Returns a violation per inbox slug whose unread/read-archive counts drifted in the restore."""
    violations: list[str] = []
    src = _inbox_counts(backup / "team-memory")
    dst = _inbox_counts(restored / "team-memory")
    for slug in sorted(set(src) | set(dst)):
        if src.get(slug, (0, 0)) != dst.get(slug, (0, 0)):
            violations.append(
                f"(c) inbox completeness: slug '{slug}' counts differ "
                f"(backup {src.get(slug, (0, 0))}, restore {dst.get(slug, (0, 0))})"
            )
    return violations


def _manifest_sha_violations(restored: Path, manifest: dict) -> list[str]:
    """Returns a violation per tree whose recomputed SHA256 no longer matches the manifest."""
    violations: list[str] = []
    for group, recorded in manifest.get("sha256", {}).items():
        actual = tree_sha256(restored / group)
        if actual != recorded:
            violations.append(
                f"manifest: SHA256 of {group}/ does not match the recorded backup"
            )
    return violations


def _wip_violations(restored: Path, manifest: dict) -> list[str]:
    """(G4) Returns a violation per recorded stash whose bundle is missing or omits the stash commit."""
    violations: list[str] = []
    for entry in manifest.get("wip", []):
        stash = entry.get("stash")
        if not stash:
            continue  # a clean worktree had no WIP to bundle
        bundle = restored / "wip" / str(entry["worktree"]) / "wip.bundle"
        if not bundle.is_file():
            violations.append(
                f"(G4) wip: bundle missing for worktree '{entry['worktree']}'"
            )
            continue
        heads = subprocess.run(
            ["git", "bundle", "list-heads", str(bundle)],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
        ).stdout
        if stash not in heads:
            violations.append(
                f"(G4) wip: bundle for '{entry['worktree']}' does not record the stash commit"
            )
    return violations


def verify_restore(backup: Path, restored: Path) -> list[str]:
    """Returns all tested-valid violations across the four groups + manifest; empty list = valid."""
    violations: list[str] = []
    manifest_path = backup / "manifest.json"
    if not manifest_path.is_file():
        return ["manifest.json missing from the backup"]
    manifest = json.loads(manifest_path.read_text())

    # G1 — (a) C4 on the restored team-memory, (b) byte-identity, (c) inbox completeness.
    c4 = check_index_integrity(_REPO_ROOT, restored / "team-memory")
    if c4:
        violations.append(f"(a) {c4}")
    violations.extend(_byte_identity_violations(backup, restored, "team-memory"))
    violations.extend(_inbox_completeness_violations(backup, restored))
    # G2 / G3 — byte-identity (secrets confidential-safe).
    violations.extend(_byte_identity_violations(backup, restored, "claude-user-state"))
    violations.extend(
        _byte_identity_violations(backup, restored, "secrets", confidential=True)
    )
    # G4 + manifest integrity.
    violations.extend(_wip_violations(restored, manifest))
    violations.extend(_manifest_sha_violations(restored, manifest))
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
