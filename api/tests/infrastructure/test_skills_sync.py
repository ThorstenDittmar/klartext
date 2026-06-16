"""Infrastructure tests: skill distribution (`klartext skills sync`).

Two things are gated here:

  * the **F0 prerequisite contract** — `tdd` and `systematic-debugging` must exist in the repo as
    tracked work products. They used to live only in `~/.claude/skills/` (un-versioned); F0.1 cannot
    path-classify a skill that is not a tracked artifact. Both are the two skills with the heaviest
    superpowers dependency, so their absence from the repo is the gap this asserts is closed.
  * the **real sync wiring** — the pure mirror logic is unit-tested in `api/tests/test_cli.py`; here
    the command's source/target constants and an end-to-end sync of the *actual* repo skills dir are
    gated, so the wiring (not just the algorithm) is verified.
"""

from __future__ import annotations

from pathlib import Path

from api.cli import (
    _SKILLS_SOURCE,
    _SKILLS_TARGET,
    SkillsSyncAction,
    _sync_skills,
)

_REPO_ROOT = Path(__file__).parents[3]
_SKILLS_DIR = _REPO_ROOT / "docs" / "method" / "enactment" / "skills"

# The skills that F0 must be able to classify — previously un-versioned (user-global only).
_F0_REQUIRED_SKILLS = ("tdd", "systematic-debugging")


def test_tdd_and_systematic_debugging_are_tracked_in_repo() -> None:
    """Expects both F0-required skills to exist in the repo as non-empty SKILL.md work products."""
    for name in _F0_REQUIRED_SKILLS:
        skill = _SKILLS_DIR / name / "SKILL.md"
        assert skill.is_file(), f"{name} is not a tracked work product (F0 cannot classify it)"
        assert skill.read_text().strip(), f"{name}/SKILL.md is empty"


def test_skills_sync_source_points_at_repo_skills_dir() -> None:
    """Expects the sync command to read from the repo's docs/method/enactment/skills/ directory."""
    assert _SKILLS_SOURCE == _SKILLS_DIR


def test_skills_sync_target_is_user_global_claude_skills() -> None:
    """Expects the sync command to install into ~/.claude/skills/ (the install location)."""
    assert _SKILLS_TARGET == Path.home() / ".claude" / "skills"


def test_real_repo_skills_sync_installs_f0_required_skills(tmp_path: Path) -> None:
    """Expects syncing the real repo skills dir to install both F0-required skills with SKILL.md.

    Runs the actual mirror against the live source into a throwaway target — proving the repo
    layout (flat `.md` and `<name>/` directories) syncs end-to-end, not just the unit fixtures.
    """
    target = tmp_path / "skills"

    result = _sync_skills(_SKILLS_SOURCE, target)

    for name in _F0_REQUIRED_SKILLS:
        assert result[name] in (SkillsSyncAction.INSTALLED, SkillsSyncAction.UPDATED)
        installed = target / name / "SKILL.md"
        assert installed.is_file()
        assert installed.read_text() == (_SKILLS_DIR / name / "SKILL.md").read_text()
        assert (target / name / ".repo-managed").exists()


def test_real_repo_skills_sync_is_idempotent(tmp_path: Path) -> None:
    """Expects a second sync of the real repo skills to report every skill UNCHANGED."""
    target = tmp_path / "skills"
    _sync_skills(_SKILLS_SOURCE, target)

    result = _sync_skills(_SKILLS_SOURCE, target)

    assert result, "expected at least one skill to be synced"
    assert all(action == SkillsSyncAction.UNCHANGED for action in result.values())
