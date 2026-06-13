"""Infrastructure tests: team auto-memory via committed project settings.

Empirically verified 2026-06-13 (lab ``~/memlab``, desktop app v1.12603.x, claude 2.1.177):

  * ``autoMemoryDirectory`` set in the **committed** ``.claude/settings.json`` IS honored by the
    desktop app (after the folder's trust dialog is accepted) and **overrides** the user-global
    ``~/.claude/settings.json`` (precedence: project > user). The ``~/`` prefix expands correctly.
  * The auto-memory **default** is keyed by the sanitized *cwd*, not the git repo, so git worktrees
    do **not** share it. A shared team blackboard therefore needs an *explicit*
    ``autoMemoryDirectory`` — and the committed ``.claude/settings.json`` is the single source that
    is byte-identical in every worktree, so all agents resolve to the same directory.

This migration moves the pin OUT of the user-global ``~/.claude/settings.json`` — which redirected
*every* machine session (klartext or not) onto the team memory, the "time bomb" — and INTO the
committed project file. ``setup.sh`` must stop writing the user-global keys and instead clean any
stale ones so existing machines stop leaking.

The desktop runtime cannot be scripted; the *runtime* honoring was verified empirically (the lab
above) and is re-checked after app updates by the Canary in
``docs/superpowers/improvement/environment/claude-code-app.md``. This file gates the two scriptable
halves: the committed settings carry the pin, and setup.sh no longer pins it user-global.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parents[3]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
SETUP_SH = REPO_ROOT / "setup.sh"

TEAM_MEMORY_DIR = "~/.claude/klartext-team-memory"

# The setup.sh cleanup is an embedded heredoc Python snippet. The marker is the exact
# line setup.sh uses to launch it. We extract the snippet and run it the same way setup.sh
# does (python3 <script> <settings_path>) so the test exercises the REAL cleanup logic,
# not a paraphrase of it.
_CLEANUP_MARKER = "python3 - \"$USER_SETTINGS\" <<'PY'"
_HEREDOC_END = "\nPY"


def _load_settings() -> dict[str, Any]:
    """Loads the committed .claude/settings.json from the repository root."""
    assert SETTINGS.exists(), ".claude/settings.json is missing — the team memory pin has no home"
    return json.loads(SETTINGS.read_text())


def _extract_cleanup_snippet() -> str:
    """Extracts the embedded user-global cleanup Python snippet from setup.sh.

    Returns the body between the ``python3 - "$USER_SETTINGS" <<'PY'`` marker and its
    closing ``PY``. Asserts the marker exists so a refactor that renames/moves the block
    fails loudly here instead of silently testing nothing.
    """
    text = SETUP_SH.read_text()
    assert _CLEANUP_MARKER in text, (
        "setup.sh no longer launches the user-global cleanup via "
        f"{_CLEANUP_MARKER!r}; the behavioral cleanup tests can no longer locate the snippet. "
        "If the cleanup moved, update _CLEANUP_MARKER to match."
    )
    start = text.index(_CLEANUP_MARKER)
    body_start = text.index("\n", start) + 1
    body_end = text.index(_HEREDOC_END, body_start)
    return text[body_start:body_end]


def _run_cleanup(settings_path: Path) -> subprocess.CompletedProcess[str]:
    """Runs the extracted cleanup snippet against settings_path exactly as setup.sh does."""
    snippet = _extract_cleanup_snippet()
    return subprocess.run(
        [sys.executable, "-", str(settings_path)],
        input=snippet,
        capture_output=True,
        text=True,
    )


def test_committed_settings_pins_team_memory_directory() -> None:
    """Expects autoMemoryDirectory to point at the shared team blackboard in committed settings.

    This is the pin that makes every worktree resolve to one shared memory directory. Without it
    each worktree falls to its own per-cwd default and the team blackboard shatters.
    """
    settings = _load_settings()
    assert settings.get("autoMemoryDirectory") == TEAM_MEMORY_DIR, (
        "committed .claude/settings.json must pin autoMemoryDirectory to "
        f"{TEAM_MEMORY_DIR!r} so all worktrees share one team memory directory; "
        f"found {settings.get('autoMemoryDirectory')!r}"
    )


def test_committed_settings_enables_auto_memory() -> None:
    """Expects autoMemoryEnabled true in committed settings — the pin is inert when disabled."""
    assert _load_settings().get("autoMemoryEnabled") is True, (
        "committed .claude/settings.json must set autoMemoryEnabled: true, otherwise the pinned "
        "directory is never read or written"
    )


def test_setup_does_not_pin_user_global_auto_memory() -> None:
    """Expects setup.sh to no longer WRITE the autoMemory keys into the user-global settings.

    The old block assigned ``data["autoMemoryDirectory"] = …`` into ~/.claude/settings.json — the
    time bomb that redirected every machine session. The migration removes that write; if it
    silently returns the regression goes unnoticed until an unrelated project leaks into the memory.
    """
    text = SETUP_SH.read_text()
    assert 'data["autoMemoryDirectory"]' not in text, (
        "setup.sh still writes autoMemoryDirectory into the user-global settings.json — that is "
        "the time bomb this migration removes; the pin now lives in committed .claude/settings.json"
    )
    assert 'data["autoMemoryEnabled"]' not in text, (
        "setup.sh still writes autoMemoryEnabled into the user-global settings.json — remove the "
        "user-global pin; the committed .claude/settings.json carries it now"
    )


# ---------------------------------------------------------------------------
# Behavioral tests: run the ACTUAL setup.sh cleanup snippet, not a source grep.
#
# The grep-based tests above pass even if the cleanup logic is wrong: they only prove
# certain substrings exist. These tests execute the embedded snippet against temp files
# and assert the real production behavior — keys removed, OTHER keys preserved, idempotent,
# and graceful on a missing/malformed file. THIS is the failure mode that breaks machines.
# ---------------------------------------------------------------------------


def test_cleanup_removes_stale_user_global_keys(tmp_path: Path) -> None:
    """Running the setup.sh cleanup deletes both autoMemory keys from a user-global file.

    This is the time-bomb removal: an existing machine has the keys; a re-run must strip them.
    The grep test cannot prove the keys are actually popped — this one runs the code and checks.
    """
    settings = tmp_path / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "autoMemoryEnabled": True,
                "autoMemoryDirectory": "/old/team/memory",
                "theme": "dark",
            }
        )
    )

    result = _run_cleanup(settings)

    assert result.returncode == 0, f"cleanup snippet crashed: {result.stderr}"
    data = json.loads(settings.read_text())
    assert "autoMemoryEnabled" not in data, (
        "cleanup left autoMemoryEnabled in the user-global settings — the time bomb is not defused"
    )
    assert "autoMemoryDirectory" not in data, (
        "cleanup left autoMemoryDirectory in the user-global settings — time bomb not defused"
    )


def test_cleanup_preserves_other_user_global_keys(tmp_path: Path) -> None:
    """The cleanup must NOT clobber unrelated user-global keys (theme, plugins, model, …).

    setup.sh's comment promises 'without clobbering other values'. If a future edit rewrote
    the file from scratch instead of popping, the user would silently lose their settings.
    The grep test cannot catch that; this one does.
    """
    settings = tmp_path / "settings.json"
    settings.write_text(
        json.dumps(
            {
                "autoMemoryEnabled": True,
                "autoMemoryDirectory": "/old/team/memory",
                "theme": "dark",
                "model": "opus",
                "plugins": {"foo": True},
            }
        )
    )

    result = _run_cleanup(settings)

    assert result.returncode == 0, f"cleanup snippet crashed: {result.stderr}"
    data = json.loads(settings.read_text())
    assert data == {"theme": "dark", "model": "opus", "plugins": {"foo": True}}, (
        "cleanup clobbered unrelated user-global keys; it must only pop the two autoMemory keys "
        f"and leave everything else intact. Got: {data!r}"
    )


def test_cleanup_is_noop_when_keys_absent(tmp_path: Path) -> None:
    """When no autoMemory keys exist, the cleanup must leave the file untouched (idempotent).

    The snippet only rewrites the file when it actually removed something. A re-run on an
    already-clean machine must not churn the file or strip other keys.
    """
    settings = tmp_path / "settings.json"
    original = json.dumps({"theme": "light", "model": "sonnet"}, indent=2) + "\n"
    settings.write_text(original)

    result = _run_cleanup(settings)

    assert result.returncode == 0, f"cleanup snippet crashed: {result.stderr}"
    assert settings.read_text() == original, (
        "cleanup modified an already-clean user-global file; it must be a no-op when no "
        "autoMemory keys are present"
    )


def test_cleanup_handles_malformed_settings_gracefully(tmp_path: Path) -> None:
    """A malformed user-global settings.json must not abort setup.sh.

    setup.sh runs unconditionally on every machine. If a user has a hand-edited / broken
    settings.json, the cleanup must exit cleanly (exit 0) rather than crash the whole setup run.
    """
    settings = tmp_path / "settings.json"
    settings.write_text("{ this is not valid json ")

    result = _run_cleanup(settings)

    assert result.returncode == 0, (
        "cleanup snippet crashed on a malformed user-global settings.json; setup.sh must survive "
        f"a broken file rather than abort. stderr: {result.stderr}"
    )


def test_committed_settings_directory_is_user_relative_or_absolute(tmp_path: Path) -> None:
    """The committed autoMemoryDirectory must be an absolute or ~/-relative path, never empty.

    The desktop app only honors a fully-resolvable path. An empty string or a bare relative path
    would resolve differently per worktree (or not at all), silently shattering the shared store —
    the exact failure this migration exists to prevent.
    """
    directory = _load_settings().get("autoMemoryDirectory")
    assert isinstance(directory, str) and directory.strip(), (
        f"autoMemoryDirectory must be a non-empty path string; found {directory!r}"
    )
    assert directory.startswith("~/") or directory.startswith("/"), (
        "autoMemoryDirectory must be absolute or ~/-relative so it resolves to the same place "
        f"in every worktree; a bare relative path resolves per-cwd. Got {directory!r}"
    )
