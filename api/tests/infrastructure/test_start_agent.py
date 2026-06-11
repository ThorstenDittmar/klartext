"""Infrastructure tests: the per-agent worktree launcher (scripts/start-agent.sh).

Stage 2 gives each agent a long-lived git worktree on its own branch. The launcher
provisions that worktree idempotently and starts the session in it. If provisioning
breaks, an agent cannot start (or worse, an existing worktree's WIP is disturbed),
so the contract is gated by CI. The launch step (`exec claude`) is skipped via
KLARTEXT_NO_LAUNCH so the test is CI-safe.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[3] / "scripts" / "start-agent.sh"


def _git(*args: str, cwd: Path) -> None:
    """Runs a git command in cwd with a deterministic identity."""
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_repo(tmp_path: Path) -> Path:
    """Creates a main checkout with an `origin` remote that has a main branch."""
    origin = tmp_path / "origin.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(origin)], check=True, capture_output=True
    )
    main = tmp_path / "main"
    subprocess.run(["git", "clone", str(origin), str(main)], check=True, capture_output=True)
    (main / "README.md").write_text("seed\n")
    _git("add", "README.md", cwd=main)
    _git("commit", "-m", "seed", cwd=main)
    _git("push", "origin", "main", cwd=main)
    _git("fetch", "origin", cwd=main)
    return main


def _run(
    slug: str, repo_root: Path, wt_base: Path, inbox_base: Path
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "KLARTEXT_REPO_ROOT": str(repo_root),
        "KLARTEXT_WORKTREE_BASE": str(wt_base),
        "KLARTEXT_INBOX_BASE": str(inbox_base),
        "KLARTEXT_NO_LAUNCH": "1",
    }
    return subprocess.run(["bash", str(SCRIPT), slug], capture_output=True, text=True, env=env)


def test_start_agent_script_exists_and_is_executable() -> None:
    """Verifies scripts/start-agent.sh is present and executable."""
    assert SCRIPT.exists(), "scripts/start-agent.sh is missing"
    assert os.access(SCRIPT, os.X_OK), "scripts/start-agent.sh is not executable"


def test_provisions_worktree_on_agent_branch(tmp_path: Path) -> None:
    """First launch creates a worktree on branch agent/<slug> from origin/main."""
    main = _make_repo(tmp_path)
    wt_base = tmp_path / "worktrees"

    result = _run("devops", main, wt_base, tmp_path / "inbox")

    assert result.returncode == 0, result.stderr
    worktree = wt_base / "devops"
    assert worktree.is_dir(), f"worktree not created: {result.stdout}\n{result.stderr}"
    assert "branch=agent/devops" in result.stdout, result.stdout
    assert (worktree / "README.md").exists(), "worktree was not checked out"


def test_reuses_existing_worktree_without_reset(tmp_path: Path) -> None:
    """A second launch reuses the worktree and never resets uncommitted WIP."""
    main = _make_repo(tmp_path)
    wt_base = tmp_path / "worktrees"
    _run("devops", main, wt_base, tmp_path / "inbox")

    # Simulate uncommitted WIP in the worktree.
    wip = wt_base / "devops" / "wip.txt"
    wip.write_text("in progress\n")

    result = _run("devops", main, wt_base, tmp_path / "inbox")

    assert result.returncode == 0, result.stderr
    assert "reusing existing worktree" in result.stdout, result.stdout
    assert wip.exists() and wip.read_text() == "in progress\n", "WIP was disturbed on relaunch"
