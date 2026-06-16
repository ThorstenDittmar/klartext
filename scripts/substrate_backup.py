#!/usr/bin/env python3
"""F2 substrate backup — out-of-band rollback for the method/product refactoring (Frozen Plan §6.3).

The git axis covers versioned code; the **substrate** lives outside version control and is touched by
F3. This captures it before the rebuild. OE+User ratified the full four-group §6.3 scope (2026-06-16),
laid down under `$KLARTEXT_BACKUP_ROOT/<UTC>/` (env-var, fail-loud if unset/unwritable; root mode 700):

  * **G1 team-memory/** — whole tree `~/.claude/klartext-team-memory/` byte-for-byte (copytree, never a
    `*.md` glob: a non-`.md` marker `compact-log-lastcheck` would be dropped, and the rule must not drift).
  * **G2 claude-user-state/** — `~/.claude/settings.json` + `~/.claude/skills/` + `~/.claude.json`
    (plugin/MCP config). Excludes `plugins/cache/`, `projects/`, history — reinstallable / not substrate.
  * **G3 secrets/** — every worktree's `.env` / `api/.env` (SENSITIVE): file mode 600, dir mode 700,
    content NEVER logged; the manifest stores a SHA256 + a confidential flag, never the bytes.
  * **G4 wip/<worktree>/** — tracked WIP via `git stash create` → `git bundle` (the worktree is not
    touched); untracked files captured as a LIST only.

`manifest.json` records per-tree SHA256, worktree HEADs + stash SHAs, the untracked lists, the timestamp,
and a confidential flag for secrets. Restore + verification live in `substrate_restore.py`. The backup
holds cleartext creds outside git → it MUST be deleted after a successful F3 (see the F3 close-out).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_TEMP_WIP_REF = (
    "refs/klartext-wip-backup"  # transient ref to bundle a stash commit; removed after
)


def _team_memory_dir(home: Path) -> Path:
    """Returns the live substrate root (the pinned shared team memory) under `home`."""
    return home / ".claude" / "klartext-team-memory"


def tree_sha256(root: Path) -> str:
    """Returns a stable SHA256 over a directory tree (sorted relpaths + bytes). '' for a missing tree."""
    if not root.exists():
        return ""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _resolve_backup_root(backup_root: Path | None) -> Path:
    """Resolves the backup root from the arg or $KLARTEXT_BACKUP_ROOT. Fail-loud if neither is set."""
    if backup_root is not None:
        return backup_root
    env = os.environ.get("KLARTEXT_BACKUP_ROOT")
    if not env:
        raise ValueError(
            "KLARTEXT_BACKUP_ROOT is unset and no backup_root was given — refusing a default location"
        )
    return Path(env)


def _git(*args: str, cwd: Path) -> str:
    """Runs a git command in cwd and returns stdout (raises on non-zero exit)."""
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True
    ).stdout


def _backup_team_memory(home: Path, dest: Path) -> None:
    """G1: mirror the whole team-memory tree byte-for-byte (copytree — never an extension filter)."""
    source = _team_memory_dir(home)
    if not source.is_dir():
        raise FileNotFoundError(f"substrate team-memory not found: {source}")
    shutil.copytree(source, dest)


def _backup_user_state(home: Path, dest: Path) -> None:
    """G2: copy settings.json + skills/ + .claude.json; exclude caches/projects/history."""
    dest.mkdir(parents=True)
    claude = home / ".claude"
    if (claude / "settings.json").is_file():
        shutil.copy2(claude / "settings.json", dest / "settings.json")
    if (claude / "skills").is_dir():
        shutil.copytree(claude / "skills", dest / "skills")
    if (home / ".claude.json").is_file():
        shutil.copy2(home / ".claude.json", dest / ".claude.json")


def _backup_secrets(worktrees: list[Path], dest: Path) -> list[dict[str, str]]:
    """G3: copy each worktree's .env / api/.env with file mode 600, dir mode 700. No content is logged.

    Returns confidential manifest entries (worktree, path, sha256) — never the bytes.
    """
    dest.mkdir(parents=True)
    os.chmod(dest, 0o700)
    entries: list[dict[str, str]] = []
    for worktree in worktrees:
        for rel in (".env", "api/.env"):
            source = worktree / rel
            if not source.is_file():
                continue
            target = dest / worktree.name / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            os.chmod(target, 0o600)
            entries.append(
                {
                    "worktree": worktree.name,
                    "path": f"{worktree.name}/{rel}",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
            )
    return entries


def _backup_wip(worktrees: list[Path], dest: Path) -> list[dict[str, object]]:
    """G4: bundle each worktree's tracked WIP (git stash create) without touching it; list untracked.

    Returns manifest entries {worktree, head, stash, untracked}. A clean worktree yields no stash/bundle.
    """
    dest.mkdir(parents=True)
    entries: list[dict[str, object]] = []
    for worktree in worktrees:
        if not (worktree / ".git").exists():
            continue
        head = _git("rev-parse", "HEAD", cwd=worktree).strip()
        stash = _git("stash", "create", cwd=worktree).strip()
        untracked = [
            line
            for line in _git(
                "ls-files", "--others", "--exclude-standard", cwd=worktree
            ).splitlines()
        ]
        entry: dict[str, object] = {
            "worktree": worktree.name,
            "head": head,
            "untracked": untracked,
        }
        if stash:
            wt_dir = dest / worktree.name
            wt_dir.mkdir(parents=True)
            # A transient ref names the stash commit so the bundle is fetchable; removed right after,
            # leaving the worktree (and its repo refs) unchanged.
            _git("update-ref", _TEMP_WIP_REF, stash, cwd=worktree)
            try:
                _git(
                    "bundle",
                    "create",
                    str(wt_dir / "wip.bundle"),
                    _TEMP_WIP_REF,
                    cwd=worktree,
                )
            finally:
                _git("update-ref", "-d", _TEMP_WIP_REF, cwd=worktree)
            entry["stash"] = stash
        entries.append(entry)
    return entries


def backup_substrate(
    *,
    home: Path,
    worktrees: list[Path],
    backup_root: Path | None = None,
    timestamp: str | None = None,
) -> Path:
    """Backs up the four substrate groups + a manifest under backup_root/<UTC>/; returns the path.

    Fail-loud: raises if the backup root is unresolved/unwritable or the team-memory source is missing.
    The backup directory is created mode 700 (it holds the secrets group).
    """
    root = _resolve_backup_root(backup_root)
    stamp = timestamp or datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")
    backup = root / stamp
    backup.mkdir(
        parents=True
    )  # unwritable base raises here (fail-loud), never a silent fallback
    os.chmod(backup, 0o700)

    _backup_team_memory(home, backup / "team-memory")
    _backup_user_state(home, backup / "claude-user-state")
    secrets = _backup_secrets(worktrees, backup / "secrets")
    wip = _backup_wip(worktrees, backup / "wip")

    manifest = {
        "timestamp": stamp,
        "sha256": {
            "team-memory": tree_sha256(backup / "team-memory"),
            "claude-user-state": tree_sha256(backup / "claude-user-state"),
        },
        "secrets": secrets,
        "secrets_confidential": True,
        "worktree_heads": {e["worktree"]: e["head"] for e in wip},
        "wip": wip,
    }
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return backup


def _list_worktrees(repo: Path) -> list[Path]:
    """Returns every git worktree path of the repository at `repo`."""
    out = _git("worktree", "list", "--porcelain", cwd=repo)
    return [
        Path(line[len("worktree ") :])
        for line in out.splitlines()
        if line.startswith("worktree ")
    ]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: backs up the live four-group substrate, prints the path, returns 0/1."""
    home = Path.home()
    if not _team_memory_dir(home).is_dir():
        print(f"✗  substrate not found: {_team_memory_dir(home)}", file=sys.stderr)
        return 1
    try:
        backup = backup_substrate(home=home, worktrees=_list_worktrees(Path.cwd()))
    except ValueError as exc:
        print(f"✗  {exc}", file=sys.stderr)
        return 1
    print(f"✓  substrate backed up → {backup}  (delete after a successful F3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
