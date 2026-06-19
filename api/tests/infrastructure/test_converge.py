"""Infrastructure tests: `klartext converge` — guarded voluntary worktree convergence (ADR-0012).

The pure guard decision is unit-tested in `api/tests/test_cli.py`. This file gates the **real git
behaviour** against throwaway repos, because the guards are only real if the actual rebase respects
them:

  * a clean `agent/<slug>` home branch behind `origin/main` **is** rebased;
  * a feature branch is **never** rebased (it converges via its PR lifecycle);
  * a dirty home branch is **never** rebased and its WIP is preserved;
  * an up-to-date branch is a no-op;
  * an untracked `api/.venv` symlink does not count as WIP.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from wow_cli.converge import ConvergeAction, _converge_worktree

_REPO_ROOT = Path(__file__).parents[3]


def _git(*args: str, cwd: Path) -> None:
    """Runs a git command in cwd with a deterministic identity."""
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_behind_worktree(
    tmp_path: Path, *, branch: str = "agent/devops", behind: int = 1, dirty: bool = False
) -> Path:
    """Builds a `branch` checkout that is `behind` commits behind `origin/main`.

    Layout: a bare origin with `main`; a `work` checkout on `branch` (forked at the seed commit);
    `origin/main` is then advanced by `behind` commits via a separate clone. `work` does not fetch —
    `_converge_worktree` does that itself. With `dirty=True`, `work` carries an uncommitted change.
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True
    )
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)
    (work / "README.md").write_text("seed\n")
    # Track an api/ directory so the untracked api/.venv symlink shows up as `?? api/.venv`,
    # not a collapsed `?? api/` — mirrors the real repo where api/ is tracked.
    (work / "api").mkdir()
    (work / "api" / "keep.txt").write_text("keep\n")
    _git("add", "README.md", "api/keep.txt", cwd=work)
    _git("commit", "-m", "seed", cwd=work)
    _git("push", "origin", "main", cwd=work)
    _git("checkout", "-b", branch, cwd=work)
    _git("push", "origin", branch, cwd=work)

    if behind:
        pub = tmp_path / "pub"
        subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
        _git("checkout", "main", cwd=pub)
        for i in range(behind):
            (pub / f"f{i}.txt").write_text(f"{i}\n")
            _git("add", f"f{i}.txt", cwd=pub)
            _git("commit", "-m", f"advance {i}", cwd=pub)
        _git("push", "origin", "main", cwd=pub)

    if dirty:
        (work / "README.md").write_text("local WIP\n")
    return work


def test_converge_rebases_clean_home_branch_behind(tmp_path: Path) -> None:
    """Expects a clean home branch behind main to be rebased — it then carries main's new commit."""
    work = _make_behind_worktree(tmp_path, branch="agent/devops", behind=1)
    assert not (work / "f0.txt").exists()  # precondition: behind, does not have the advance yet

    result = _converge_worktree(work)

    assert result.action == ConvergeAction.SYNC
    assert (work / "f0.txt").exists(), "worktree was not rebased onto origin/main"


def test_converge_leaves_feature_branch_untouched(tmp_path: Path) -> None:
    """Expects a feature branch to be skipped and NOT rebased — it converges via its PR."""
    work = _make_behind_worktree(tmp_path, branch="feat/x", behind=1)

    result = _converge_worktree(work)

    assert result.action == ConvergeAction.SKIP_NOT_HOME_BRANCH
    assert not (work / "f0.txt").exists(), "feature branch was rebased — the guard failed"


def test_converge_skips_dirty_home_branch_and_preserves_wip(tmp_path: Path) -> None:
    """Expects a dirty home branch to be skipped, not rebased, and its WIP left intact."""
    work = _make_behind_worktree(tmp_path, branch="agent/devops", behind=1, dirty=True)

    result = _converge_worktree(work)

    assert result.action == ConvergeAction.SKIP_DIRTY
    assert not (work / "f0.txt").exists(), "dirty worktree was rebased — the guard failed"
    assert (work / "README.md").read_text() == "local WIP\n", "WIP was disturbed"


def test_converge_is_noop_when_already_current(tmp_path: Path) -> None:
    """Expects an up-to-date clean home branch to report ALREADY_CURRENT and do nothing."""
    work = _make_behind_worktree(tmp_path, branch="agent/devops", behind=0)

    result = _converge_worktree(work)

    assert result.action == ConvergeAction.ALREADY_CURRENT
    assert result.commits_behind == 0


def test_converge_ignores_untracked_venv_and_syncs(tmp_path: Path) -> None:
    """Expects an untracked `api/.venv` symlink to not count as WIP — a behind home branch syncs."""
    work = _make_behind_worktree(tmp_path, branch="agent/devops", behind=1)
    (work / "api" / ".venv").symlink_to(tmp_path)  # untracked symlink, like the real venv link

    result = _converge_worktree(work)

    assert result.action == ConvergeAction.SYNC
    assert (work / "f0.txt").exists()


def test_converge_command_rebases_via_subprocess(tmp_path: Path) -> None:
    """Expects the real `klartext converge` command (no --all) to rebase the cwd worktree.

    End-to-end smoke over the typer wiring: it must resolve the cwd worktree, apply the guards,
    rebase, and exit 0. Run as `python -m api.cli` with PYTHONPATH on this worktree, because the
    venv's editable install points at the main checkout, not this branch's code.
    """
    work = _make_behind_worktree(tmp_path, branch="agent/devops", behind=1)
    env = {**os.environ, "PYTHONPATH": str(_REPO_ROOT)}

    result = subprocess.run(
        [sys.executable, "-m", "api.cli", "converge"],
        cwd=str(work),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"converge command failed:\n{result.stdout}\n{result.stderr}"
    assert (work / "f0.txt").exists(), "command did not rebase the worktree"


# ---------------------------------------------------------------------------
# QA-added RED tests — failure modes the original suite does not cover.
# These characterise destructive/silent behaviour of _converge_worktree.
# ---------------------------------------------------------------------------


def _make_conflicting_worktree(tmp_path: Path, *, branch: str = "agent/devops") -> Path:
    """Builds a clean `branch` whose committed edit to `shared.txt` conflicts with origin/main.

    Both the agent branch and origin/main change the same line of `shared.txt`, so a rebase of
    `branch` onto `origin/main` necessarily hits a merge conflict.
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True
    )
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)
    (work / "api").mkdir()
    (work / "api" / "keep.txt").write_text("keep\n")
    (work / "shared.txt").write_text("base\n")
    _git("add", "api/keep.txt", "shared.txt", cwd=work)
    _git("commit", "-m", "seed", cwd=work)
    _git("push", "origin", "main", cwd=work)
    _git("checkout", "-b", branch, cwd=work)
    (work / "shared.txt").write_text("agent change\n")
    _git("add", "shared.txt", cwd=work)
    _git("commit", "-m", "agent edit", cwd=work)

    pub = tmp_path / "pub"
    subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
    _git("checkout", "main", cwd=pub)
    (pub / "shared.txt").write_text("main change\n")
    _git("add", "shared.txt", cwd=pub)
    _git("commit", "-m", "main edit", cwd=pub)
    _git("push", "origin", "main", cwd=pub)
    return work


def test_converge_conflict_does_not_leave_worktree_mid_rebase(tmp_path: Path) -> None:
    """Expects a rebase conflict to NOT leave the worktree in a half-rebased, conflicted state.

    A clean home branch whose commit conflicts with origin/main cannot be auto-rebased. Converge
    must not abandon the worktree mid-rebase (.git/rebase-merge present, conflict markers staged):
    that is exactly the destructive surprise ADR-0012's guards exist to prevent. Converge must
    either abort the rebase (restoring the pre-rebase HEAD) or surface a meaningful message while
    leaving the worktree in a clean, usable state.
    """
    work = _make_conflicting_worktree(tmp_path, branch="agent/devops")

    try:
        _converge_worktree(work)
    except Exception:
        pass  # how the failure surfaces is secondary; the worktree state is what matters

    assert not (work / ".git" / "rebase-merge").exists(), (
        "worktree left mid-rebase after a conflict — destructive, guards bypassed"
    )
    porcelain = subprocess.run(
        ["git", "-C", str(work), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "UU " not in porcelain, f"unresolved conflict markers left in worktree:\n{porcelain}"


def test_converge_offline_fetch_failure_is_not_silent_success(tmp_path: Path) -> None:
    """Expects an unreachable origin (offline) to NOT be reported as a clean ALREADY_CURRENT.

    `git fetch` runs without check=True and its result is discarded, so when the remote is
    unreachable the stale origin/main is used and behind-count comes back 0 → the user sees a green
    'already current' while actually offline and possibly behind. A failed fetch must surface, not
    masquerade as success.
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True
    )
    work = tmp_path / "work"
    subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)
    (work / "README.md").write_text("seed\n")
    _git("add", "README.md", cwd=work)
    _git("commit", "-m", "seed", cwd=work)
    _git("push", "origin", "main", cwd=work)
    _git("checkout", "-b", "agent/devops", cwd=work)
    # Simulate offline: point origin at a path that does not exist so fetch fails.
    _git("remote", "set-url", "origin", str(tmp_path / "gone.git"), cwd=work)

    try:
        result = _converge_worktree(work)
    except Exception:
        return  # raising on fetch failure is an acceptable, non-silent outcome

    assert result.action != ConvergeAction.ALREADY_CURRENT, (
        "offline fetch failure silently reported as 'already current' — false success"
    )


def test_converge_all_skips_feature_and_dirty_worktrees(tmp_path: Path) -> None:
    """Expects `--all` to converge only the clean home branch and skip feature/dirty worktrees.

    The original suite only exercises a single clean cwd worktree. This drives the --all loop over
    a mix: one clean home branch (must sync), one feature branch (must not rebase), one dirty home
    branch (must not rebase, WIP preserved). All three are wired as real worktrees of one repo.
    """
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True
    )
    main = tmp_path / "main"
    subprocess.run(["git", "clone", str(origin), str(main)], check=True, capture_output=True)
    (main / "api").mkdir()
    (main / "api" / "keep.txt").write_text("keep\n")
    _git("add", "api/keep.txt", cwd=main)
    _git("commit", "-m", "seed", cwd=main)
    _git("push", "origin", "main", cwd=main)

    # Advance origin/main by one commit so home branches are behind.
    pub = tmp_path / "pub"
    subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
    (pub / "f0.txt").write_text("0\n")
    _git("add", "f0.txt", cwd=pub)
    _git("commit", "-m", "advance", cwd=pub)
    _git("push", "origin", "main", cwd=pub)

    # Three worktrees off the main checkout.
    clean_home = tmp_path / "wt_clean"
    feature = tmp_path / "wt_feat"
    dirty_home = tmp_path / "wt_dirty"
    _git("worktree", "add", "-b", "agent/clean", str(clean_home), "HEAD", cwd=main)
    _git("worktree", "add", "-b", "feat/x", str(feature), "HEAD", cwd=main)
    _git("worktree", "add", "-b", "agent/dirty", str(dirty_home), "HEAD", cwd=main)
    (dirty_home / "wip.txt").write_text("local WIP\n")  # untracked WIP → dirty

    for wt in (clean_home, feature, dirty_home):
        _converge_worktree(wt)

    assert (clean_home / "f0.txt").exists(), "clean home branch was not synced by --all"
    assert not (feature / "f0.txt").exists(), "feature branch was rebased by --all — guard failed"
    assert not (dirty_home / "f0.txt").exists(), (
        "dirty worktree was rebased by --all — guard failed"
    )
    assert (dirty_home / "wip.txt").read_text() == "local WIP\n", "WIP disturbed by --all"


def test_converge_all_does_not_crash_on_bare_worktree_entry(tmp_path: Path) -> None:
    """Expects a bare main repo (a `bare` entry in `worktree list`) to not crash the --all loop.

    A repo whose main checkout is bare emits a `bare` entry in `git worktree list --porcelain`.
    `_parse_worktree_list` returns its path, and `_converge_worktree` then runs `git status` on it,
    which exits 128 on a bare repo → an uncaught CalledProcessError aborts the whole --all run
    (later worktrees never get converged). A bare entry must be skipped gracefully, not fatal.
    """
    bare = tmp_path / "main.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(bare)], check=True, capture_output=True
    )

    # Calling converge on the bare path is what --all does after parsing the bare entry.
    _converge_worktree(bare)  # must not raise
