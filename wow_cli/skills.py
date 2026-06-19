"""Stack-neutral skill-distribution logic for the WoW CLI (method-seed phase 4).

Mirrors a repo's skills into an install dir, idempotently and prune-safely: the repo is the single
source of truth, each source skill (flat `<name>.md` or `<name>/` directory) installs as
`<target>/<name>/` with a `.repo-managed` marker, re-running is a no-op when content matches,
managed dirs whose source disappeared are pruned, and unmarked foreign/plugin skills are untouched.

Source/target paths are parameters — no project-specific literal lives here. klartext's
`klartext skills sync` command wires its own paths and re-uses this logic (git + stdlib only).
"""

from __future__ import annotations

import shutil
from enum import StrEnum
from pathlib import Path

_REPO_MANAGED_MARKER = ".repo-managed"


class SkillsSyncAction(StrEnum):
    """Outcome of mirroring one skill from the repo into the install directory."""

    INSTALLED = "installed"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    PRUNED = "pruned"


def _collect_skill_files(source: Path) -> dict[str, bytes]:
    """Returns the desired install file set for one source skill, keyed by relative path.

    A flat `<name>.md` source becomes a single `SKILL.md`; a `<name>/` directory is mirrored
    file-for-file (multi-file skills like qa-review keep their companion docs). The
    `.repo-managed` marker is never part of the comparison set — it is install metadata.
    """
    if source.is_file():
        return {"SKILL.md": source.read_bytes()}
    files: dict[str, bytes] = {}
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        rel = path.relative_to(source).as_posix()
        if rel == _REPO_MANAGED_MARKER:
            continue
        files[rel] = path.read_bytes()
    return files


def _read_managed_files(skill_dir: Path) -> dict[str, bytes]:
    """Returns a target skill dir's installed files by relative path (excludes the marker)."""
    files: dict[str, bytes] = {}
    for path in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(skill_dir).as_posix()
        if rel == _REPO_MANAGED_MARKER:
            continue
        files[rel] = path.read_bytes()
    return files


def _source_skills(source_dir: Path) -> dict[str, Path]:
    """Maps skill name → source path. Skills are flat `<name>.md` files or `<name>/` directories."""
    skills: dict[str, Path] = {}
    if not source_dir.exists():
        return skills
    for entry in sorted(source_dir.iterdir()):
        if entry.is_dir():
            skills[entry.name] = entry
        elif entry.suffix == ".md":
            skills[entry.stem] = entry
    return skills


def _sync_skills(source_dir: Path, target_dir: Path) -> dict[str, SkillsSyncAction]:
    """Mirrors repo skills into the install dir, idempotently and prune-safely.

    The repo is the single source of truth. Each source skill (flat `<name>.md` or `<name>/`
    directory) is installed as `<target>/<name>/` with a `.repo-managed` marker. Re-running is a
    no-op (UNCHANGED) when content matches; changed content is overwritten (UPDATED). Managed
    target dirs whose source has disappeared are pruned (handles renames like pre-compact→anchor);
    unmarked foreign/plugin skills are never touched.
    """
    result: dict[str, SkillsSyncAction] = {}
    sources = _source_skills(source_dir)

    for name, source in sources.items():
        desired = _collect_skill_files(source)
        skill_dir = target_dir / name
        if not skill_dir.exists():
            action = SkillsSyncAction.INSTALLED
        elif _read_managed_files(skill_dir) != desired:
            action = SkillsSyncAction.UPDATED
        else:
            action = SkillsSyncAction.UNCHANGED

        if action in (SkillsSyncAction.INSTALLED, SkillsSyncAction.UPDATED):
            if skill_dir.exists():
                shutil.rmtree(skill_dir)
            for rel, content in desired.items():
                dest = skill_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
        # Always ensure the marker exists, even on an UNCHANGED re-sync of a hand-copied dir.
        marker = skill_dir / _REPO_MANAGED_MARKER
        if not marker.exists():
            marker.write_text("")
        result[name] = action

    # Prune managed dirs whose source is gone; leave unmarked foreign skills untouched.
    # Guard: never prune when the source yielded *no* skills. A missing or empty source dir
    # (a path typo, a wrong cwd, a broken checkout) must not be read as "every skill deleted"
    # and wipe the whole install — pruning only ever follows a real source.
    if sources and target_dir.exists():
        for entry in sorted(target_dir.iterdir()):
            if (
                entry.is_dir()
                and entry.name not in sources
                and (entry / _REPO_MANAGED_MARKER).exists()
            ):
                shutil.rmtree(entry)
                result[entry.name] = SkillsSyncAction.PRUNED

    return result
