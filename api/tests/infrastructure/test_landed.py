"""Infrastructure tests: `klartext landed <ref>` — did a ref's work reach origin/main?

The pure verdict is unit-tested in `api/tests/test_cli.py`. This file gates the **real git
behaviour** against throwaway repos, with the squash-merge trap as the central case:

  * a ref reachable from origin/main (real merge-commit / fast-forward) → landed by SHA;
  * a ref whose commit was **squash-merged** (new SHA on main, content present) → landed by
    content — the case `git branch --contains` gets wrong, the exact false conclusion this guards;
  * a ref whose content is NOT in main → not landed (non-zero exit).

Run as `python -m api.cli landed <ref>` with PYTHONPATH on this worktree, because the venv's
editable install points at the main checkout, not this branch's code (same stance as test_converge).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]


def _git(*args: str, cwd: Path) -> str:
    """Runs a git command in cwd with a deterministic identity, returning stdout."""
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _landed(ref: str, *, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Invokes the real `klartext landed <ref>` command in cwd."""
    return subprocess.run(
        [sys.executable, "-m", "api.cli", "landed", ref],
        cwd=str(cwd),
        env={**os.environ, "PYTHONPATH": str(_REPO_ROOT)},
        capture_output=True,
        text=True,
    )


def _seed_repo(tmp_path: Path) -> tuple[Path, Path]:
    """Creates a bare origin with `main` seeded and a `work` clone on a feature branch.

    Returns (origin, work). `work` is on `feat/x`, forked from the seed commit on main.
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
    _git("checkout", "-b", "feat/x", cwd=work)
    return origin, work


def test_landed_reports_landed_by_content_for_squash_merged_branch(tmp_path: Path) -> None:
    """Expects a squash-merged branch to be reported as landed-by-content, exit 0.

    The branch commit changes a.txt; origin/main then gets the SAME content as a NEW commit (a
    squash). The branch SHA is never reachable from main, but its content is fully present —
    `landed` must see this and NOT report it as unmerged.
    """
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("feature change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "feature work", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()

    # Simulate the squash merge: same content lands on origin/main as a different commit.
    pub = tmp_path / "pub"
    subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
    (pub / "a.txt").write_text("feature change\n")
    _git("add", "a.txt", cwd=pub)
    _git("commit", "-m", "feature work (squash) (#42)", cwd=pub)
    _git("push", "origin", "main", cwd=pub)

    result = _landed(branch_sha, cwd=work)

    assert result.returncode == 0, f"squash-merged work reported as not landed:\n{result.stderr}"
    assert "content" in result.stdout.lower(), result.stdout


def test_landed_reports_landed_by_content_when_main_moved_on_after_squash(tmp_path: Path) -> None:
    """Expects landed-by-content even when main has UNRELATED commits after the squash.

    The real-world case the full-tree diff gets wrong: a branch commit's changes are squash-merged,
    then main moves on with other work. A whole-tree `git diff <ref> origin/main` is then never
    empty, yet the ref's *changes* are present. The verdict must rest on change-equivalence
    (patch-id), not tree-equality — this is exactly the f0fc0b6 situation that misled the agent.
    """
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("feature change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "feature work", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()

    pub = tmp_path / "pub"
    subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
    (pub / "a.txt").write_text("feature change\n")  # the squash: same change, new SHA
    _git("add", "a.txt", cwd=pub)
    _git("commit", "-m", "feature work (squash) (#42)", cwd=pub)
    (pub / "b.txt").write_text("unrelated later work\n")  # main moves on after the squash
    _git("add", "b.txt", cwd=pub)
    _git("commit", "-m", "later unrelated work", cwd=pub)
    _git("push", "origin", "main", cwd=pub)

    result = _landed(branch_sha, cwd=work)

    assert result.returncode == 0, f"squash work reported not landed:\n{result.stdout}"
    assert "content" in result.stdout.lower(), result.stdout


def test_landed_reports_landed_by_sha_for_reachable_commit(tmp_path: Path) -> None:
    """Expects a commit reachable from origin/main (real merge / ff) to be landed-by-sha, exit 0."""
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("feature change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "feature work", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()
    # Fast-forward main to the branch commit (sha-preserving merge) and push.
    _git("push", "origin", f"{branch_sha}:main", cwd=work)

    result = _landed(branch_sha, cwd=work)

    assert result.returncode == 0, f"reachable commit reported as not landed:\n{result.stderr}"
    assert "sha" in result.stdout.lower(), result.stdout


def test_landed_reports_not_landed_for_unmerged_work(tmp_path: Path) -> None:
    """Expects a branch whose content is absent from origin/main to be not-landed, non-zero exit."""
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("feature change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "feature work", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()

    result = _landed(branch_sha, cwd=work)

    assert result.returncode != 0, f"genuinely unmerged work reported as landed:\n{result.stdout}"
    assert "not landed" in result.stdout.lower(), result.stdout


def test_landed_reports_not_landed_when_only_some_commits_squashed(tmp_path: Path) -> None:
    """Expects a multi-commit branch with only ONE commit landed to be NOT landed (safety).

    The dangerous false positive: a branch has two commits, the first is squash-merged onto main,
    the second is still unmerged. `git cherry` then prints `-` for the landed commit but `+` for
    the unmerged one. Partial landing must NEVER be reported as landed — the second commit's work
    would silently be considered safe to drop. Non-zero exit, "not landed".
    """
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("first change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "first commit", cwd=work)
    (work / "b.txt").write_text("second change\n")
    _git("add", "b.txt", cwd=work)
    _git("commit", "-m", "second commit (still unmerged)", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()

    # Squash-merge ONLY the first commit's content onto origin/main.
    pub = tmp_path / "pub"
    subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
    (pub / "a.txt").write_text("first change\n")
    _git("add", "a.txt", cwd=pub)
    _git("commit", "-m", "first change (squash) (#7)", cwd=pub)
    _git("push", "origin", "main", cwd=pub)

    result = _landed(branch_sha, cwd=work)

    assert result.returncode != 0, f"partially-landed branch reported as landed:\n{result.stdout}"
    assert "not landed" in result.stdout.lower(), result.stdout


def test_landed_reports_landed_by_content_when_all_commits_squashed(tmp_path: Path) -> None:
    """Expects a multi-commit branch whose EVERY commit's patch is upstream to be landed-by-content.

    Counterpart to the partial case: when all of the branch's commits have an equivalent patch on
    origin/main (each `git cherry` line is `-`, none `+`), even though the squash gave them new
    SHAs, the work is fully present and must be reported landed. Exit 0, "content".
    """
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("first change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "first commit", cwd=work)
    (work / "b.txt").write_text("second change\n")
    _git("add", "b.txt", cwd=work)
    _git("commit", "-m", "second commit", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()

    # Replay BOTH commits' content onto origin/main as new (squash-style) commits.
    pub = tmp_path / "pub"
    subprocess.run(["git", "clone", str(origin), str(pub)], check=True, capture_output=True)
    (pub / "a.txt").write_text("first change\n")
    _git("add", "a.txt", cwd=pub)
    _git("commit", "-m", "first change (squash) (#7)", cwd=pub)
    (pub / "b.txt").write_text("second change\n")
    _git("add", "b.txt", cwd=pub)
    _git("commit", "-m", "second change (squash) (#8)", cwd=pub)
    _git("push", "origin", "main", cwd=pub)

    result = _landed(branch_sha, cwd=work)

    assert result.returncode == 0, f"fully-landed branch reported not landed:\n{result.stdout}"
    assert "content" in result.stdout.lower(), result.stdout


def test_landed_reports_landed_by_sha_for_ancestor_commit_with_no_own_work(tmp_path: Path) -> None:
    """Expects the seed commit (an ancestor of origin/main with no own commits) to be landed-by-sha.

    A ref that is already an ancestor of origin/main — e.g. the seed commit the feature branch
    forked from — is trivially reachable. `git cherry` is empty (no own commits to compare). The
    verdict must be LANDED_BY_SHA via reachability, exit 0, "sha".
    """
    origin, work = _seed_repo(tmp_path)
    # feat/x currently sits exactly on the seed commit, which is origin/main's tip.
    seed_sha = _git("rev-parse", "HEAD", cwd=work).strip()

    result = _landed(seed_sha, cwd=work)

    assert result.returncode == 0, f"ancestor commit reported as not landed:\n{result.stderr}"
    assert "sha" in result.stdout.lower(), result.stdout


def test_landed_errors_on_nonexistent_ref(tmp_path: Path) -> None:
    """Expects a bad/nonexistent ref to error with 'no such ref', NOT a confident 'not landed'.

    DevOps decision (QA-flagged footgun): a typo'd or deleted ref must not look identical to
    genuinely unmerged work. An unresolvable ref is a distinct failure — `landed` reports 'no such
    ref' and exits 2, so a typo can never be mistaken for a real not-landed verdict.
    """
    origin, work = _seed_repo(tmp_path)

    result = _landed("does-not-exist-deadbeef", cwd=work)

    assert result.returncode == 2, result.stdout
    assert "no such ref" in result.stdout.lower(), result.stdout
    assert "not landed" not in result.stdout.lower(), result.stdout


def test_landed_warns_when_fetch_fails_offline(tmp_path: Path) -> None:
    """Expects a failed origin fetch (offline) to warn the answer may be stale, not stay silent.

    `landed`'s whole purpose is the a-jour discipline; answering against a stale origin/main without
    a word is the silent-staleness trap. With origin unreachable but the ref resolvable locally, the
    command still produces a verdict but must surface a freshness warning (same stance as converge's
    SKIP_FETCH_FAILED).
    """
    origin, work = _seed_repo(tmp_path)
    (work / "a.txt").write_text("feature change\n")
    _git("add", "a.txt", cwd=work)
    _git("commit", "-m", "feature work", cwd=work)
    branch_sha = _git("rev-parse", "HEAD", cwd=work).strip()
    # Simulate offline: point origin at a path that does not exist so fetch fails.
    _git("remote", "set-url", "origin", str(tmp_path / "gone.git"), cwd=work)

    result = _landed(branch_sha, cwd=work)

    combined = (result.stdout + result.stderr).lower()
    assert "fetch" in combined or "stale" in combined, f"no freshness warning:\n{combined}"
