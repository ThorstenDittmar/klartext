"""`converge` — guarded voluntary worktree convergence (ADR-0012).

Stack-neutral WoW command (git + stdlib + typer only). Rebases a clean `agent/<slug>` home branch
onto origin/main; feature branches and dirty worktrees are reported and left untouched; never
destructive (a rebase conflict is aborted and the pre-rebase HEAD restored). Registered onto a host
typer app via `register`, so klartext keeps its single entrypoint and the seed ships the same command.

REVIEW (parametrization): `_is_worktree_clean` ignores an untracked `api/.venv` symlink — a klartext
layout literal. Behaviour-preserving here; a later increment parametrizes it from seed.toml (the same
literal-→{{…}} REVIEW strand as the template scripts).
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import typer


class ConvergeAction(StrEnum):
    """Outcome of evaluating whether/how a worktree should converge to origin/main."""

    SYNC = "sync"
    ALREADY_CURRENT = "already_current"
    SKIP_DIRTY = "skip_dirty"
    SKIP_NOT_HOME_BRANCH = "skip_not_home_branch"
    SKIP_CONFLICT = "skip_conflict"
    SKIP_FETCH_FAILED = "skip_fetch_failed"
    SKIP_UNAVAILABLE = "skip_unavailable"


_HOME_BRANCH_RE = re.compile(r"^agent/[^/]+$")


def _is_home_branch(branch: str) -> bool:
    """True for an `agent/<slug>` home branch — the only branch converge rebases (ADR-0012 §B)."""
    return bool(_HOME_BRANCH_RE.match(branch))


def _is_worktree_clean(porcelain: str) -> bool:
    """True if `git status --porcelain` shows no WIP, ignoring the untracked `api/.venv` symlink.

    Every worktree carries an untracked `api/.venv` symlink to the shared venv; it is never WIP.
    Any other entry — modified, staged, or untracked — counts as dirty and blocks convergence.
    """
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        if line[3:].strip() in ("api/.venv", "api/.venv/"):
            continue
        return False
    return True


def _converge_decision(
    branch: str, is_clean: bool, commits_behind: int
) -> ConvergeAction:
    """Pure guard decision for `converge` (ADR-0012: guarded voluntary convergence).

    Guards in priority order: a non-home branch is never touched (feature branches converge via
    their PR lifecycle); a dirty worktree is never disturbed (consent over coercion); an up-to-date
    branch is a no-op; only a clean home branch that is behind main is rebased.
    """
    if not _is_home_branch(branch):
        return ConvergeAction.SKIP_NOT_HOME_BRANCH
    if not is_clean:
        return ConvergeAction.SKIP_DIRTY
    if commits_behind == 0:
        return ConvergeAction.ALREADY_CURRENT
    return ConvergeAction.SYNC


@dataclass(frozen=True)
class ConvergeResult:
    """Outcome of converging one worktree: the action taken, its branch, and how far behind."""

    action: ConvergeAction
    branch: str
    commits_behind: int


def _git_out(path: Path, *args: str) -> str:
    """Runs a read-only git command in `path` and returns stdout (raises on non-zero exit)."""
    return subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, check=True
    ).stdout


def _converge_worktree(path: Path) -> ConvergeResult:
    """Converges one worktree to `origin/main` under the ADR-0012 guards — never destructively.

    Applies the pure guard decision (only a clean `agent/<slug>` home branch behind main is rebased)
    and layers the failure modes that must never surprise an agent:
      * a path that is not a usable worktree (bare repo / git error) is skipped, not fatal;
      * a failed `git fetch` (offline) is reported, never masqueraded as "already current";
      * a rebase conflict is **aborted** (restoring the pre-rebase HEAD) and reported — the worktree
        is never left half-rebased with conflict markers.
    """
    # Read branch + cleanliness; a bare repo or any git error here means "not a usable worktree".
    try:
        branch = _git_out(path, "rev-parse", "--abbrev-ref", "HEAD").strip()
        porcelain = _git_out(path, "status", "--porcelain")
    except subprocess.CalledProcessError:
        return ConvergeResult(
            ConvergeAction.SKIP_UNAVAILABLE, branch="", commits_behind=0
        )
    is_clean = _is_worktree_clean(porcelain)

    # Skip decisions that don't depend on the remote — no need to touch the network for these.
    if not _is_home_branch(branch) or not is_clean:
        return ConvergeResult(_converge_decision(branch, is_clean, 0), branch, 0)

    # A failed fetch must surface, not pass off a stale ref as success.
    fetch = subprocess.run(
        ["git", "-C", str(path), "fetch", "origin", "--quiet"],
        capture_output=True,
        text=True,
    )
    if fetch.returncode != 0:
        return ConvergeResult(ConvergeAction.SKIP_FETCH_FAILED, branch, 0)

    behind = int(
        _git_out(path, "rev-list", "--count", "HEAD..origin/main").strip() or "0"
    )
    action = _converge_decision(branch, is_clean, behind)
    if action == ConvergeAction.SYNC:
        rebase = subprocess.run(
            ["git", "-C", str(path), "rebase", "origin/main"],
            capture_output=True,
            text=True,
        )
        if rebase.returncode != 0:
            # Restore the pre-rebase HEAD — never leave the worktree mid-rebase.
            subprocess.run(
                ["git", "-C", str(path), "rebase", "--abort"], capture_output=True
            )
            return ConvergeResult(ConvergeAction.SKIP_CONFLICT, branch, behind)
    return ConvergeResult(action=action, branch=branch, commits_behind=behind)


def _parse_worktree_list(porcelain: str) -> list[Path]:
    """Extracts worktree paths from `git worktree list --porcelain` output."""
    prefix = "worktree "
    return [
        Path(line[len(prefix) :])
        for line in porcelain.splitlines()
        if line.startswith(prefix)
    ]


def _list_worktrees() -> list[Path]:
    """Returns every git worktree of the current repository (resolved from the cwd)."""
    return _parse_worktree_list(_git_out(Path.cwd(), "worktree", "list", "--porcelain"))


def _print_converge_result(path: Path, result: ConvergeResult) -> None:
    """Prints a one-line, colour-coded summary of a worktree's convergence outcome."""
    name = path.name
    if result.action == ConvergeAction.SYNC:
        typer.secho(
            f"✓  {name}: synced ({result.commits_behind} behind → up to date)",
            fg=typer.colors.GREEN,
        )
    elif result.action == ConvergeAction.ALREADY_CURRENT:
        typer.secho(f"✓  {name}: already current", fg=typer.colors.GREEN)
    elif result.action == ConvergeAction.SKIP_DIRTY:
        typer.secho(
            f"⊘  {name}: skipped — uncommitted changes (rebase manually when ready)",
            fg=typer.colors.YELLOW,
        )
    elif result.action == ConvergeAction.SKIP_NOT_HOME_BRANCH:
        typer.secho(
            f"⊘  {name}: skipped — on {result.branch} (a feature branch converges via its PR)",
            fg=typer.colors.YELLOW,
        )
    elif result.action == ConvergeAction.SKIP_CONFLICT:
        typer.secho(
            f"✗  {name}: rebase conflict — aborted, worktree restored; resolve manually",
            fg=typer.colors.RED,
        )
    elif result.action == ConvergeAction.SKIP_FETCH_FAILED:
        typer.secho(
            f"✗  {name}: could not fetch origin (offline?) — not converged",
            fg=typer.colors.RED,
        )
    else:  # SKIP_UNAVAILABLE
        typer.secho(
            f"⊘  {name}: skipped — not a usable worktree", fg=typer.colors.YELLOW
        )


def converge(
    all_worktrees: bool = typer.Option(
        False,
        "--all",
        help="Converge every worktree of the repo, not just the current one",
    ),
) -> None:
    """Converge worktree(s) to origin/main under the ADR-0012 guards (voluntary convergence).

    Only a clean `agent/<slug>` home branch that is behind main is rebased; feature branches and
    dirty worktrees are reported and left untouched. Idempotent — safe to re-run.
    """
    targets = _list_worktrees() if all_worktrees else [Path.cwd()]
    for path in targets:
        _print_converge_result(path, _converge_worktree(path))


def register(app: typer.Typer) -> None:
    """Registers the `converge` command on a host typer app (klartext re-export / seed CLI)."""
    app.command()(converge)
