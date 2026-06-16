"""Infrastructure tests: F2 substrate backup + restore (out-of-band rollback for the refactoring).

Before F3 touches the live substrate, F2 provides the rollback axis git cannot. OE+User ratified the
full Frozen-Plan §6.3 scope (2026-06-16) — a FOUR-group backup under `$KLARTEXT_BACKUP_ROOT/<UTC>/`
(env-var, fail-loud) plus a manifest:

  * **G1 team-memory/** — whole tree byte-for-byte (copytree, NOT a `*.md` glob; a non-`.md` marker
    `compact-log-lastcheck` would be dropped). Integrity: (a) C4 ∧ (b) byte-identity ∧ (c) inbox.
  * **G2 claude-user-state/** — `settings.json` + `skills/` + `~/.claude.json`; excludes caches/
    projects. Integrity: (b) byte-identity.
  * **G3 secrets/** — every worktree's `.env`/`api/.env` (SENSITIVE): files 600, dir 700, content
    NEVER in logs/violations (path only); manifest stores SHA256 + a confidential flag, not bytes.
  * **G4 wip/<worktree>/** — tracked WIP via `git stash create` → `git bundle`; untracked as a LIST.
    Integrity: the bundle is valid and records the stash commit.

`manifest.json`: SHA256 per tree, worktree HEADs + stash SHAs, timestamp, confidential flag.
Tested-valid = sandbox-restore with every group's integrity green + manifest SHA256 matching.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import substrate_backup as sb  # noqa: E402
import substrate_restore as sr  # noqa: E402

_MARKER = "compact-log-lastcheck"  # the non-.md file OE flagged — pins the whole-tree property


def _git(*args: str, cwd: Path) -> str:
    """Runs a git command in cwd with a deterministic identity, returns stdout."""
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _make_home(root: Path) -> Path:
    """Builds a fake ~/.claude home: team-memory (G1) + user-state (G2) + caches to exclude."""
    home = root / "home"
    claude = home / ".claude"
    mem = claude / "klartext-team-memory"
    (mem / "inbox" / "devops" / ".read").mkdir(parents=True)
    (mem / "MEMORY.md").write_text("# Index\n\n- [Card](feedback_x.md) — hook\n")
    (mem / "feedback_x.md").write_text("the fact\n")
    (mem / _MARKER).write_text("1718539200\n")
    (mem / "inbox" / "devops" / "live.md").write_text("unread\n")
    (mem / "inbox" / "devops" / ".read" / "old.md").write_text("archived\n")
    # G2 user-state
    (claude / "settings.json").write_text('{"autoMemoryDirectory": "x"}\n')
    (claude / "skills" / "anchor").mkdir(parents=True)
    (claude / "skills" / "anchor" / "SKILL.md").write_text("anchor skill\n")
    (home / ".claude.json").write_text('{"mcpServers": {}}\n')
    # excluded caches
    (claude / "plugins" / "cache").mkdir(parents=True)
    (claude / "plugins" / "cache" / "junk").write_text("reinstallable\n")
    (claude / "projects").mkdir()
    (claude / "projects" / "transcript.jsonl").write_text("big\n")
    return home


def _make_worktree(root: Path, name: str, *, env: bool = True, wip: bool = False) -> Path:
    """Builds a git worktree (its own repo) optionally carrying an api/.env and tracked WIP."""
    wt = root / name
    (wt / "api").mkdir(parents=True)
    _git("init", "-q", cwd=wt)
    (wt / "README.md").write_text("base\n")
    _git("add", "-A", cwd=wt)
    _git("commit", "-q", "-m", "base", cwd=wt)
    if env:
        (wt / "api" / ".env").write_text("ANTHROPIC_API_KEY=sk-secret-do-not-log\n")
    if wip:
        (wt / "README.md").write_text("base\nWIP change\n")  # tracked, uncommitted
        (wt / "scratch.txt").write_text("untracked\n")  # untracked
    return wt


# --- backup: structure + groups -----------------------------------------------------------


def test_backup_fails_loud_when_backup_root_unset(tmp_path: Path) -> None:
    """Expects a missing $KLARTEXT_BACKUP_ROOT to raise — never a silent default location."""
    import pytest

    home = _make_home(tmp_path)
    with pytest.raises(ValueError):
        sb.backup_substrate(home=home, worktrees=[], backup_root=None)


def test_backup_creates_four_groups_and_manifest(tmp_path: Path) -> None:
    """Expects the four group dirs (team-memory/ user-state/ secrets/ wip/) + manifest.json."""
    home = _make_home(tmp_path)
    wt = _make_worktree(tmp_path, "wt-a", wip=True)

    backup = sb.backup_substrate(home=home, worktrees=[wt], backup_root=tmp_path / "bk")

    for group in ("team-memory", "claude-user-state", "secrets", "wip"):
        assert (backup / group).is_dir(), f"missing group {group}"
    assert (backup / "manifest.json").is_file()


def test_g1_team_memory_whole_tree_includes_non_md_marker(tmp_path: Path) -> None:
    """Expects G1 to mirror the whole team-memory tree incl. the non-.md marker (OE pin)."""
    home = _make_home(tmp_path)
    backup = sb.backup_substrate(home=home, worktrees=[], backup_root=tmp_path / "bk")
    tm = backup / "team-memory"
    src = home / ".claude" / "klartext-team-memory"
    assert (tm / _MARKER).read_bytes() == (src / _MARKER).read_bytes()
    assert (tm / "inbox" / "devops" / ".read" / "old.md").is_file()


def test_g2_user_state_copies_settings_skills_and_claude_json_excluding_caches(
    tmp_path: Path,
) -> None:
    """Expects G2 to capture settings.json + skills/ + .claude.json; excludes caches/projects."""
    home = _make_home(tmp_path)
    backup = sb.backup_substrate(home=home, worktrees=[], backup_root=tmp_path / "bk")
    us = backup / "claude-user-state"
    assert (us / "settings.json").read_bytes() == (home / ".claude" / "settings.json").read_bytes()
    assert (us / "skills" / "anchor" / "SKILL.md").is_file()
    assert (us / ".claude.json").is_file()
    assert not (us / "plugins").exists(), "plugins/cache must be excluded"
    assert not (us / "projects").exists(), "projects/ must be excluded"


def test_g3_secrets_copied_with_restrictive_modes(tmp_path: Path) -> None:
    """Expects G3 to copy each worktree .env with file mode 600 and the secrets dir mode 700."""
    home = _make_home(tmp_path)
    wt = _make_worktree(tmp_path, "wt-a")
    backup = sb.backup_substrate(home=home, worktrees=[wt], backup_root=tmp_path / "bk")
    secrets = backup / "secrets"
    env_copies = list(secrets.rglob(".env"))
    assert env_copies, "expected the worktree api/.env to be backed up"
    assert stat.S_IMODE(secrets.stat().st_mode) == 0o700
    for copy in env_copies:
        assert stat.S_IMODE(copy.stat().st_mode) == 0o600


def test_manifest_records_sha_heads_and_flags_secrets_confidential_without_content(
    tmp_path: Path,
) -> None:
    """Expects the manifest to carry per-tree SHA256, worktree HEADs, and a confidential flag.

    Crucially it must NOT store secret *content* — the .env value appears nowhere in the manifest.
    """
    import json

    home = _make_home(tmp_path)
    wt = _make_worktree(tmp_path, "wt-a", wip=True)
    backup = sb.backup_substrate(home=home, worktrees=[wt], backup_root=tmp_path / "bk")
    manifest = json.loads((backup / "manifest.json").read_text())
    assert "sha256" in manifest and manifest["sha256"]
    assert manifest["worktree_heads"], "expected worktree HEADs recorded"
    assert manifest["secrets_confidential"] is True
    assert "sk-secret-do-not-log" not in (backup / "manifest.json").read_text()


# --- restore + verify ---------------------------------------------------------------------


def test_restore_roundtrip_verifies_clean(tmp_path: Path) -> None:
    """Expects backup → restore-to-sandbox → verify of all four groups + manifest to be clean."""
    home = _make_home(tmp_path)
    wt = _make_worktree(tmp_path, "wt-a", wip=True)
    backup = sb.backup_substrate(home=home, worktrees=[wt], backup_root=tmp_path / "bk")
    sandbox = tmp_path / "sandbox"

    sr.restore_substrate(backup, sandbox)

    assert sr.verify_restore(backup, sandbox) == []


def test_verify_flags_g1_byte_difference(tmp_path: Path) -> None:
    """Expects (b) byte-identity to flag a G1 file that drifted in the restore."""
    home = _make_home(tmp_path)
    backup = sb.backup_substrate(home=home, worktrees=[], backup_root=tmp_path / "bk")
    sandbox = tmp_path / "sandbox"
    sr.restore_substrate(backup, sandbox)
    (sandbox / "team-memory" / _MARKER).write_text("TAMPERED\n")

    violations = sr.verify_restore(backup, sandbox)

    assert any(_MARKER in v for v in violations)


def test_verify_secret_violation_names_path_not_content(tmp_path: Path) -> None:
    """Expects a G3 secret mismatch to report the path only — never the secret bytes."""
    home = _make_home(tmp_path)
    wt = _make_worktree(tmp_path, "wt-a")
    backup = sb.backup_substrate(home=home, worktrees=[wt], backup_root=tmp_path / "bk")
    sandbox = tmp_path / "sandbox"
    sr.restore_substrate(backup, sandbox)
    tampered = next((sandbox / "secrets").rglob(".env"))
    tampered.write_text("ANTHROPIC_API_KEY=sk-different-secret\n")

    violations = sr.verify_restore(backup, sandbox)

    assert violations, "expected a secrets violation"
    joined = "\n".join(violations)
    assert ".env" in joined
    assert "sk-different-secret" not in joined and "sk-secret-do-not-log" not in joined


def test_verify_flags_manifest_sha_mismatch(tmp_path: Path) -> None:
    """Expects manifest verification to flag a restored tree whose SHA256 no longer matches."""
    home = _make_home(tmp_path)
    backup = sb.backup_substrate(home=home, worktrees=[], backup_root=tmp_path / "bk")
    sandbox = tmp_path / "sandbox"
    sr.restore_substrate(backup, sandbox)
    (sandbox / "claude-user-state" / "settings.json").write_text('{"tampered": true}\n')

    violations = sr.verify_restore(backup, sandbox)

    assert violations


def test_verify_flags_g4_wip_bundle_recoverable(tmp_path: Path) -> None:
    """Expects G4 to bundle tracked WIP into a verifiable bundle holding the stash commit."""
    home = _make_home(tmp_path)
    wt = _make_worktree(tmp_path, "wt-a", wip=True)
    backup = sb.backup_substrate(home=home, worktrees=[wt], backup_root=tmp_path / "bk")

    bundles = list((backup / "wip").rglob("*.bundle"))
    assert bundles, "expected a WIP bundle for the dirty worktree"
    # `git bundle verify` returns 0 only for a valid bundle (_git check=True → raises otherwise);
    # assert the recorded ref by name (locale-independent — verify's prose text is localized).
    out = _git("bundle", "verify", str(bundles[0]), cwd=wt)
    assert "refs/klartext-wip-backup" in out


def test_restore_fails_loud_when_backup_missing(tmp_path: Path) -> None:
    """Expects restoring a non-existent backup to raise — never a silent empty restore."""
    import pytest

    with pytest.raises(FileNotFoundError):
        sr.restore_substrate(tmp_path / "no-backup", tmp_path / "sandbox")


def test_backup_root_from_env_when_not_passed(tmp_path: Path) -> None:
    """Expects backup_substrate to read $KLARTEXT_BACKUP_ROOT when no explicit root is given."""
    home = _make_home(tmp_path)
    os.environ["KLARTEXT_BACKUP_ROOT"] = str(tmp_path / "envbk")
    try:
        backup = sb.backup_substrate(home=home, worktrees=[])
        assert (tmp_path / "envbk") in backup.parents
    finally:
        del os.environ["KLARTEXT_BACKUP_ROOT"]
