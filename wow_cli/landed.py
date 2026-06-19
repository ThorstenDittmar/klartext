"""`landed` — did a ref's work reach origin/main? (squash-aware: change-presence, not SHA).

Stack-neutral WoW command (git + stdlib + typer only). Under a squash-merge default a merged branch
commit gets a NEW sha on main, so `git branch --contains` wrongly reports it as unmerged; this checks
reachability AND change-presence (patch-id equivalence). Registered onto a host typer app via
`register`, so klartext keeps its single `klartext` entrypoint and the seed ships the same command.
"""

from __future__ import annotations

import subprocess
from enum import StrEnum
from pathlib import Path

import typer


class LandedStatus(StrEnum):
    """Whether a ref's work has reached origin/main, and by which evidence."""

    LANDED_BY_SHA = "landed_by_sha"  # reachable from main (merge-commit / fast-forward)
    LANDED_BY_CONTENT = (
        "landed_by_content"  # sha absent from main, but content fully present
    )
    NOT_LANDED = (
        "not_landed"  # neither reachable nor content-subsumed — genuinely unmerged
    )


def _landed_verdict(*, sha_contained: bool, changes_in_main: bool) -> LandedStatus:
    """Decides whether a ref's work is in origin/main, distinguishing SHA- from change-presence.

    The squash-merge trap: a squash-merged branch commit gets a NEW sha on main and is never
    reachable from it (`git branch --contains` reports it as unmerged), even though its changes are
    present. Reachability (`sha_contained`) is the stronger signal when present; otherwise
    change-equivalence (`changes_in_main` — every commit of the ref has an equivalent patch upstream)
    is the reliable evidence that the work landed under a squash. Only when neither holds is the work
    genuinely unmerged.
    """
    if sha_contained:
        return LandedStatus.LANDED_BY_SHA
    if changes_in_main:
        return LandedStatus.LANDED_BY_CONTENT
    return LandedStatus.NOT_LANDED


def _fetch_origin(path: Path) -> bool:
    """Fetches origin quietly; returns False when the fetch failed (e.g. offline)."""
    return (
        subprocess.run(
            ["git", "-C", str(path), "fetch", "origin", "--quiet"], capture_output=True
        ).returncode
        == 0
    )


def _ref_resolves(path: Path, ref: str) -> bool:
    """True when `ref` resolves to a commit object — guards against a typo'd or deleted ref."""
    return (
        subprocess.run(
            [
                "git",
                "-C",
                str(path),
                "rev-parse",
                "--verify",
                "--quiet",
                f"{ref}^{{commit}}",
            ],
            capture_output=True,
        ).returncode
        == 0
    )


def _ref_landed_status(path: Path, ref: str) -> LandedStatus:
    """Computes the landed verdict for `ref` against the local origin/main (caller fetches first).

    Reachability via `git merge-base --is-ancestor`. Change-presence via `git cherry`, which marks
    each of the ref's commits `-` when an equivalent patch (same patch-id) already exists upstream
    and `+` when it does not — so a squash-merge is detected by change-equivalence even after main
    has moved on, where a whole-tree diff would always show differences.
    """
    sha_contained = (
        subprocess.run(
            ["git", "-C", str(path), "merge-base", "--is-ancestor", ref, "origin/main"],
            capture_output=True,
        ).returncode
        == 0
    )
    cherry = subprocess.run(
        ["git", "-C", str(path), "cherry", "origin/main", ref],
        capture_output=True,
        text=True,
    )
    changes_in_main = cherry.returncode == 0 and not any(
        line.startswith("+") for line in cherry.stdout.splitlines()
    )
    return _landed_verdict(sha_contained=sha_contained, changes_in_main=changes_in_main)


def landed(
    ref: str = typer.Argument(
        ..., help="branch or commit to check against origin/main"
    ),
) -> None:
    """Report whether <ref>'s work has reached origin/main — by change-equivalence, not just SHA.

    Under a squash-merge default a merged branch commit gets a NEW SHA on main, so
    `git branch --contains` wrongly reports it as unmerged. This checks reachability AND
    change-presence (patch-id equivalence) and prints the verdict; it exits non-zero only when the
    work is genuinely not landed. Use it instead of SHA-containment to answer "did this land?".
    """
    cwd = Path.cwd()
    if not _fetch_origin(cwd):
        typer.secho(
            "⚠  could not fetch origin — answering against a possibly-stale origin/main.",
            fg=typer.colors.YELLOW,
            err=True,
        )
    if not _ref_resolves(cwd, ref):
        typer.secho(f"✗  no such ref: {ref}", fg=typer.colors.RED)
        raise typer.Exit(2)
    status = _ref_landed_status(cwd, ref)
    if status == LandedStatus.LANDED_BY_SHA:
        typer.secho(
            f"✓  {ref} landed — reachable from origin/main (SHA present).",
            fg=typer.colors.GREEN,
        )
    elif status == LandedStatus.LANDED_BY_CONTENT:
        typer.secho(
            f"✓  {ref} landed by content — SHA absent from main (squash), content fully present.",
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(
            f"✗  {ref} not landed — content differs from origin/main (genuinely unmerged).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


def register(app: typer.Typer) -> None:
    """Registers the `landed` command on a host typer app (klartext re-export / seed CLI)."""
    app.command()(landed)
