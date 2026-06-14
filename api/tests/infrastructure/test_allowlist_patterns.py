"""Infrastructure test: allowlist patterns match real tool invocations (ADR-0011 G4).

The pre-commit semgrep hook invokes semgrep via its venv path (`api/.venv/bin/semgrep`), not a
bare `semgrep` on PATH. The base allowlist entry `Bash(semgrep*)` does not match that path, so an
agent running the genuine invocation gets a permission prompt (`Projekt (lokal)` deny-by-default).

This test ties the allowlist pattern to the pre-commit `entry`, so the two cannot drift apart
silently: if the entry path changes or the allowlist loses the venv pattern, the test fails.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]  # PyYAML ships no stubs; types-PyYAML not a project dep

REPO_ROOT = Path(__file__).parents[3]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
PRECOMMIT = REPO_ROOT / ".pre-commit-config.yaml"


def _allowlist() -> list[str]:
    """Returns the Bash/permission allow list from .claude/settings.json."""
    settings: dict[str, Any] = json.loads(SETTINGS.read_text())
    return settings["permissions"]["allow"]


def _semgrep_entry() -> str:
    """Returns the pre-commit semgrep hook's entry path — the real invocation form."""
    config: dict[str, Any] = yaml.safe_load(PRECOMMIT.read_text())
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            if hook.get("id") == "semgrep":
                return hook["entry"]
    raise AssertionError("no semgrep hook with an 'entry' found in .pre-commit-config.yaml")


def test_semgrep_venv_path_is_allowlisted() -> None:
    """Expects the allowlist to permit the pre-commit semgrep entry path without a prompt.

    The pre-commit hook runs `<entry> ...` (a venv path); `Bash(semgrep*)` does not match it, so
    the genuine invocation would prompt. A `Bash(<entry>*)` pattern must be present.
    """
    entry = _semgrep_entry()  # e.g. api/.venv/bin/semgrep
    expected = f"Bash({entry}*)"
    allow = _allowlist()
    assert expected in allow, (
        f"allowlist is missing {expected!r} — the real semgrep invocation ({entry} ...) would "
        f"prompt; Bash(semgrep*) does not match the venv path. Current allow list: {allow}"
    )


def test_base_semgrep_pattern_still_present() -> None:
    """Expects the bare `Bash(semgrep*)` pattern to remain in the allowlist (no regression).

    The venv-path fix adds `Bash(api/.venv/bin/semgrep*)` alongside — not instead of — the base
    pattern, which still covers a manual `semgrep ...` run on PATH. Guards against a future edit
    dropping the base entry while adding the venv one.
    """
    allow = _allowlist()
    assert "Bash(semgrep*)" in allow, (
        f"base pattern 'Bash(semgrep*)' missing — a manual `semgrep ...` on PATH would prompt. "
        f"Current allow list: {allow}"
    )
