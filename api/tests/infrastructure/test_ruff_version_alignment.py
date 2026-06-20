"""Infrastructure test: the ruff version is pinned identically for local hooks and CI.

A skew between the pre-commit ruff hook and the ruff CI installs lets a commit pass local
pre-commit but fail CI's `ruff format --check` / `ruff check` (observed: v0.11.12 vs 0.15.18
disagreed on quote style and N802). The fix pins both to the SAME exact version:

  * `.pre-commit-config.yaml`  → `rev: vX.Y.Z` on the ruff-pre-commit repo
  * `api/pyproject.toml` dev   → `ruff==X.Y.Z` (exact, so CI's `pip install -e .[dev]` gets it)

This test enforces that invariant (ADR-0006: a rule needs an automated check) so the two sources
can never silently drift apart again.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]
_PRE_COMMIT = _REPO_ROOT / ".pre-commit-config.yaml"
_PYPROJECT = _REPO_ROOT / "api" / "pyproject.toml"
_LINT_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "lint.yml"


def _pre_commit_ruff_version() -> str:
    """Returns the ruff version from the ruff-pre-commit hook's `rev` (without the leading v)."""
    text = _PRE_COMMIT.read_text()
    match = re.search(
        r"ruff-pre-commit\s*\n\s*(?:#.*\n\s*)*rev:\s*v?(?P<v>[0-9]+\.[0-9]+\.[0-9]+)",
        text,
    )
    assert match, "could not find the ruff-pre-commit rev in .pre-commit-config.yaml"
    return match.group("v")


def _pyproject_ruff_version() -> str:
    """Returns the exact ruff version pinned in api/pyproject.toml's dev extra."""
    text = _PYPROJECT.read_text()
    match = re.search(r'"ruff==(?P<v>[0-9]+\.[0-9]+\.[0-9]+)"', text)
    assert match, "ruff must be pinned exactly ('ruff==X.Y.Z') in api/pyproject.toml dev extra"
    return match.group("v")


def test_pre_commit_and_pyproject_ruff_versions_match() -> None:
    """Expects the pre-commit ruff rev and the pyproject ruff pin to be the identical version.

    Guards against the local-vs-CI ruff skew: if they differ, a commit can pass pre-commit yet
    fail CI's ruff format/lint. Bump BOTH together.
    """
    pre_commit = _pre_commit_ruff_version()
    pyproject = _pyproject_ruff_version()
    assert pre_commit == pyproject, (
        f"ruff version skew: .pre-commit-config.yaml pins v{pre_commit} but api/pyproject.toml "
        f"pins =={pyproject} — bump both to the same version (local==CI, no drift)."
    )


def test_pyproject_ruff_is_pinned_exactly() -> None:
    """Expects ruff pinned with EXACT '==' (not a floating range), so CI cannot drift."""
    text = _PYPROJECT.read_text()
    assert '"ruff==' in text, "ruff must be an exact '==' pin so CI does not pick a newer version"
    assert not re.search(r'"ruff>=', text), "ruff must not use a floating '>=' range (drift risk)"


def test_lint_workflow_does_not_pin_ruff_separately() -> None:
    """Expects lint.yml to get ruff from the pyproject dev extra, never a separate version pin.

    CI installs via `pip install -e '.[dev]'`, so api/pyproject.toml is the single CI source of
    truth for the ruff version. A separately pinned ruff in the workflow (e.g. a `pip install
    ruff==X` step) would bypass that pin and silently reintroduce the local-vs-CI skew this guard
    exists to prevent.
    """
    text = _LINT_WORKFLOW.read_text()
    assert "pip install -e '.[dev]'" in text, (
        "lint.yml must install ruff via the pyproject dev extra (pip install -e '.[dev]'), "
        "so api/pyproject.toml stays the single CI source of truth for the ruff version."
    )
    separate_pin = re.search(r"ruff\s*(==|>=|<=|~=|!=|<|>)\s*[0-9]", text)
    assert not separate_pin, (
        "lint.yml must not pin a ruff version separately — that bypasses the pyproject pin and "
        "reintroduces the local-vs-CI skew. Bump the version in api/pyproject.toml instead."
    )
