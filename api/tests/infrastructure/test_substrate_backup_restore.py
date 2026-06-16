"""Infrastructure tests: F2 substrate backup + restore (out-of-band rollback for the refactoring).

Before F3 touches the live team-memory substrate, F2 provides a tested rollback axis (the git axis
covers versioned code; the substrate — team memory + inbox + index + markers — lives outside git).
OE ratified the scope (2026-06-16):

  * **scope (1)** — the WHOLE tree `~/.claude/klartext-team-memory/` byte-for-byte, NOT a `*.md`
    glob: the root holds a non-`.md` marker `compact-log-lastcheck` that a glob would silently drop
    (and any future non-`.md` file too). Whole-tree is the robust invariant.
  * **integrity (2)** — a restore is *tested-valid* iff (a) C4 index-integrity (reused from
    session_health, #133) ∧ (b) byte-identity over the whole tree ∧ (c) inbox completeness per slug
    (incl. `.read/`). C4 alone is necessary, not sufficient.
  * **target (3)** — `~/klartext-substrate-backups/<UTC>/`, fail-loud if the base is not writable.

OE's pinning request: a restore test must include a non-`.md` marker (the `compact-log-lastcheck`
case) so the whole-tree property cannot later be re-optimized back to `*.md`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import substrate_backup as sb  # noqa: E402
import substrate_restore as sr  # noqa: E402

_MARKER = "compact-log-lastcheck"  # the non-.md file OE flagged — pins the whole-tree property


def _make_substrate(root: Path) -> Path:
    """Builds a realistic mini substrate: MEMORY.md + a card + the non-.md marker + an inbox."""
    mem = root / "klartext-team-memory"
    mem.mkdir(parents=True)
    (mem / "MEMORY.md").write_text("# Index\n\n- [Card](feedback_x.md) — hook\n")
    (mem / "feedback_x.md").write_text("the fact\n")
    (mem / _MARKER).write_text("1718539200\n")  # non-.md marker (whole-tree property)
    inbox = mem / "inbox" / "devops"
    (inbox / ".read").mkdir(parents=True)
    (inbox / "2026-06-16T10:00:00__from-oe__live.md").write_text("unread body\n")
    (inbox / ".read" / "2026-06-15T09:00:00__from-oe__old.md").write_text("archived body\n")
    return mem


# --- backup -------------------------------------------------------------------------------


def test_backup_copies_whole_tree_byte_for_byte_including_non_md_marker(tmp_path: Path) -> None:
    """Expects a whole-tree byte-for-byte backup — incl. the non-.md marker (OE pin)."""
    source = _make_substrate(tmp_path / "src")
    dest_base = tmp_path / "backups"

    backup = sb.backup_substrate(source, dest_base)

    assert (backup / "MEMORY.md").read_bytes() == (source / "MEMORY.md").read_bytes()
    assert (backup / _MARKER).read_bytes() == (source / _MARKER).read_bytes()
    assert (
        backup / "inbox" / "devops" / ".read" / "2026-06-15T09:00:00__from-oe__old.md"
    ).is_file()


def test_backup_creates_timestamped_subdirectory(tmp_path: Path) -> None:
    """Expects the backup to live under dest_base in a UTC-timestamped subdirectory."""
    source = _make_substrate(tmp_path / "src")
    dest_base = tmp_path / "backups"

    backup = sb.backup_substrate(source, dest_base, timestamp="2026-06-16T19-49-29Z")

    assert backup.parent == dest_base
    assert backup.name == "2026-06-16T19-49-29Z"


def test_backup_fails_loud_when_source_missing(tmp_path: Path) -> None:
    """Expects a missing source substrate to raise — never a silent empty backup."""
    import pytest

    with pytest.raises(FileNotFoundError):
        sb.backup_substrate(tmp_path / "does-not-exist", tmp_path / "backups")


# --- restore + verify ---------------------------------------------------------------------


def test_restore_roundtrip_verifies_clean(tmp_path: Path) -> None:
    """Expects backup → restore-to-sandbox → verify (a)∧(b)∧(c) to be clean for a faithful copy."""
    source = _make_substrate(tmp_path / "src")
    backup = sb.backup_substrate(source, tmp_path / "backups")
    sandbox = tmp_path / "sandbox"

    sr.restore_substrate(backup, sandbox)

    assert sr.verify_restore(source, sandbox) == []
    assert (sandbox / _MARKER).read_bytes() == (source / _MARKER).read_bytes()


def test_verify_flags_byte_difference(tmp_path: Path) -> None:
    """Expects (b) byte-identity to flag a restored file whose content drifted from the source."""
    source = _make_substrate(tmp_path / "src")
    restored = _make_substrate(tmp_path / "restored")
    (restored / "feedback_x.md").write_text("CORRUPTED\n")

    violations = sr.verify_restore(source, restored)

    assert any("feedback_x.md" in v for v in violations)


def test_verify_flags_missing_marker_file(tmp_path: Path) -> None:
    """Expects (b) to flag the non-.md marker missing from the restore (whole-tree regression)."""
    source = _make_substrate(tmp_path / "src")
    restored = _make_substrate(tmp_path / "restored")
    (restored / _MARKER).unlink()

    violations = sr.verify_restore(source, restored)

    assert any(_MARKER in v for v in violations)


def test_verify_flags_inbox_archive_incompleteness(tmp_path: Path) -> None:
    """Expects (c) per-slug inbox completeness to flag a missing .read/ archive message."""
    source = _make_substrate(tmp_path / "src")
    restored = _make_substrate(tmp_path / "restored")
    (restored / "inbox" / "devops" / ".read" / "2026-06-15T09:00:00__from-oe__old.md").unlink()

    violations = sr.verify_restore(source, restored)

    assert any("inbox" in v and "devops" in v for v in violations)


def test_verify_flags_c4_index_break(tmp_path: Path) -> None:
    """Expects (a) C4 to flag a restored MEMORY.md entry that points at a missing file."""
    source = _make_substrate(tmp_path / "src")
    restored = _make_substrate(tmp_path / "restored")
    (restored / "feedback_x.md").unlink()  # MEMORY.md now points at a missing file

    violations = sr.verify_restore(source, restored)

    assert any("C4" in v or "MEMORY.md" in v for v in violations)


def test_restore_fails_loud_when_backup_missing(tmp_path: Path) -> None:
    """Expects restoring a non-existent backup to raise — never a silent empty restore."""
    import pytest

    with pytest.raises(FileNotFoundError):
        sr.restore_substrate(tmp_path / "no-backup", tmp_path / "sandbox")
