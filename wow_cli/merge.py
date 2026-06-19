"""`merge` — verified PR-merge wrapper (DELETE-404 retro action item).

Stack-neutral WoW command (gh + git + stdlib + typer only). Merges a PR the verified way:
poll checks green → GitHub-API merge (not `gh pr merge`, which fails when main is checked out in a
worktree) → delete the branch → verify against the mainline. rebase is intentionally unavailable
(it rewrites SHAs and breaks stacks). The repo slug is resolved from the cwd via `gh`, so nothing is
hardcoded. Registered onto a host typer app via `register` (klartext re-export / seed CLI).
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

import typer

_ALLOWED_MERGE_METHODS = ("squash", "merge")


def _validate_merge_method(method: str) -> str:
    """Returns the method if allowed. Rejects rebase — it rewrites SHAs and breaks stacks."""
    normalized = method.lower()
    if normalized in _ALLOWED_MERGE_METHODS:
        return normalized
    if normalized == "rebase":
        raise typer.BadParameter(
            "rebase rewrites commit SHAs and breaks stacked PRs — use 'squash' or 'merge'"
        )
    raise typer.BadParameter(
        f"unknown merge method '{method}' — use 'squash' or 'merge'"
    )


def _evaluate_checks(checks: list[dict[str, Any]]) -> str:
    """Collapses a list of gh check buckets into one verdict: pass | fail | pending.

    fail/cancel anywhere → fail. Then only explicitly satisfied buckets count as done:
    a bucket that is neither 'pass' nor 'skipping' (including 'pending', an unknown
    value, or a missing bucket) blocks as 'pending'. This is deliberately conservative —
    a gatekeeper must never let an unrecognized status slip through to a merge. An empty
    check list is non-blocking (pass).
    """
    buckets = [c.get("bucket") for c in checks]
    if any(b in ("fail", "cancel") for b in buckets):
        return "fail"
    if any(b not in ("pass", "skipping") for b in buckets):
        return "pending"
    return "pass"


def _evaluate_preconditions(pr: dict[str, Any]) -> tuple[bool, str]:
    """Decides whether a PR's state permits merging. Returns (ok, reason).

    Hard-fails only on a non-OPEN state or a conflicting/dirty merge state. Transient
    states (UNKNOWN/UNSTABLE/BEHIND) proceed — CI status is the check-poll step's job.
    """
    state = pr.get("state")
    if state != "OPEN":
        return False, f"PR is {state}, not OPEN"
    if pr.get("mergeable") == "CONFLICTING" or pr.get("mergeStateStatus") == "DIRTY":
        return False, "PR has merge conflicts (resolve them before merging)"
    return True, ""


def _gh_json(args: list[str]) -> Any:
    """Runs a gh command expected to emit JSON on success and returns the parsed result."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        typer.secho(
            f"✗  gh {' '.join(args)} failed:\n{result.stderr}", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    return json.loads(result.stdout)


def _fetch_check_buckets(pr: int) -> list[dict[str, Any]]:
    """Returns the check buckets for a PR.

    `gh pr checks` exits non-zero while checks are pending or failing, so the exit
    code is ignored — the JSON output is the source of truth. No checks configured →
    empty stdout → treated as no checks (non-blocking).
    """
    result = subprocess.run(
        ["gh", "pr", "checks", str(pr), "--json", "name,bucket"],
        capture_output=True,
        text=True,
    )
    out = result.stdout.strip()
    if not out:
        return []
    buckets: list[dict[str, Any]] = json.loads(out)
    return buckets


def _repo_slug() -> str:
    """Returns the owner/repo slug for the current repository via gh."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.secho(
            f"✗  could not resolve repository:\n{result.stderr}", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    return result.stdout.strip()


def merge(
    pr: int = typer.Argument(..., help="PR number to merge"),
    method: str = typer.Option(
        "squash", "--method", "-m", help="squash (default) or merge"
    ),
    keep_branch: bool = typer.Option(
        False, "--keep-branch", help="Do not delete the branch after merge"
    ),
    timeout: int = typer.Option(
        900, "--timeout", help="Max seconds to wait for checks"
    ),
) -> None:
    """Merge a PR the verified way: checks green → API-merge → delete branch → verify.

    Uses the GitHub API to merge — not `gh pr merge`, which fails when main is checked
    out in a worktree. rebase is intentionally unavailable (it rewrites SHAs and breaks
    stacks). Squash is the default; use --method merge for SHA-preserving stacks.
    """
    method = _validate_merge_method(method)

    # 1. Preconditions — refuse closed/conflicting PRs before doing anything.
    pr_info = _gh_json(
        [
            "pr",
            "view",
            str(pr),
            "--json",
            "state,mergeable,mergeStateStatus,headRefName",
        ]
    )
    ok, reason = _evaluate_preconditions(pr_info)
    if not ok:
        typer.secho(f"✗  Cannot merge PR #{pr}: {reason}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # 2. Poll required checks — never merge a red PR; abort on failure or timeout.
    typer.echo(f"Waiting for checks on PR #{pr} (timeout {timeout}s)…")
    deadline = time.monotonic() + timeout
    while True:
        verdict = _evaluate_checks(_fetch_check_buckets(pr))
        if verdict == "pass":
            typer.secho("✓  All checks passed.", fg=typer.colors.GREEN)
            break
        if verdict == "fail":
            typer.secho(
                f"✗  A check failed on PR #{pr} — not merging.", fg=typer.colors.RED
            )
            raise typer.Exit(1)
        if time.monotonic() >= deadline:
            typer.secho(
                f"✗  Timed out after {timeout}s waiting for checks.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        time.sleep(15)

    # 3. Merge via the GitHub API (not `gh pr merge` — worktree-safe).
    repo = _repo_slug()
    typer.echo(f"Merging PR #{pr} into main via {method}…")
    merge_path = f"repos/{repo}/pulls/{pr}/merge"
    result = subprocess.run(
        ["gh", "api", merge_path, "-X", "PUT", "-f", f"merge_method={method}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.secho(f"✗  Merge failed:\n{result.stderr}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"✓  PR #{pr} merged ({method}).", fg=typer.colors.GREEN)

    # 4. Delete the branch (short-lived by Merge Protocol rule 6) unless asked to keep it.
    head = pr_info.get("headRefName")
    if keep_branch:
        typer.echo(f"Keeping branch {head} (--keep-branch).")
    elif head:
        del_result = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/refs/heads/{head}", "-X", "DELETE"],
            capture_output=True,
            text=True,
        )
        if del_result.returncode == 0:
            typer.secho(f"✓  Branch {head} deleted.", fg=typer.colors.GREEN)
        else:
            typer.secho(
                f"⚠  Branch {head} not deleted: {del_result.stderr.strip()}",
                fg=typer.colors.YELLOW,
            )

    # 5. Verify against artifacts — show main after the merge (Merge Protocol rule 4).
    cwd = Path.cwd()
    subprocess.run(["git", "-C", str(cwd), "fetch", "origin", "--quiet"])
    typer.echo("\nmain after merge:")
    subprocess.run(["git", "-C", str(cwd), "log", "--oneline", "-5", "origin/main"])


def register(app: typer.Typer) -> None:
    """Registers the `merge` command on a host typer app (klartext re-export / seed CLI)."""
    app.command()(merge)
