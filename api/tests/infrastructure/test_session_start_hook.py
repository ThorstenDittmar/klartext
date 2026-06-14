"""Infrastructure tests: SessionStart identity hook (ADR-0011 G1).

ADR-0011 G1 requires a ``SessionStart`` hook that loads ``agents/<slug>/claude.md`` into the
session context on startup (and on ``/clear``, which the desktop app reports as
``source=startup``). Without it an app session boots **without** its Hoheitswissen — identity
drift — because the app has no ``start-agent.sh`` to load identity.

The desktop app cannot be scripted, so the *runtime* injection is verified by the manual Canary
in ``docs/superpowers/improvement/environment/claude-code-app.md``. This file gates the two
**scriptable** halves, which is where the mechanism silently drifts otherwise:

  1. the hook is wired in ``.claude/settings.json`` with a matcher that includes ``startup``;
  2. the loader script ``scripts/load_agent_identity.py`` injects the right file for an agent
     worktree, no-ops for non-agent directories, and wraps the preamble (not the whole file) in
     the ``EXTREMELY_IMPORTANT`` tag per OE's identity wording.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parents[3]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
SCRIPT = REPO_ROOT / "scripts" / "load_agent_identity.py"


def _load_settings() -> dict[str, Any]:
    """Loads .claude/settings.json from the repository root."""
    assert SETTINGS.exists(), (
        ".claude/settings.json is missing — the SessionStart hook cannot be configured"
    )
    return json.loads(SETTINGS.read_text())


def _session_start_entries() -> list[dict[str, Any]]:
    """Returns the SessionStart hook entries (empty list if none configured)."""
    return _load_settings().get("hooks", {}).get("SessionStart", [])


def test_session_start_hook_is_configured() -> None:
    """Expects a SessionStart hook in .claude/settings.json — the G1 enabler for app return."""
    hooks = _load_settings().get("hooks", {})
    assert "SessionStart" in hooks, (
        "No SessionStart hook in .claude/settings.json — app sessions boot without their "
        "agents/<slug>/claude.md (identity drift); ADR-0011 G1 blocks the return until this exists"
    )


def test_session_start_matcher_includes_startup() -> None:
    """Expects the matcher to include 'startup' — the app reports /clear as source=startup."""
    matchers = " ".join(entry.get("matcher", "") for entry in _session_start_entries())
    assert "startup" in matchers, (
        "SessionStart matcher must include 'startup': the app reports /clear as source=startup, "
        "so a startup matcher covers both session-open and /clear"
    )


def test_session_start_hook_invokes_loader_script() -> None:
    """Expects the SessionStart hook command to invoke scripts/load_agent_identity.py."""
    commands = " ".join(
        hook.get("command", "")
        for entry in _session_start_entries()
        for hook in entry.get("hooks", [])
    )
    assert "load_agent_identity.py" in commands, (
        "SessionStart hook does not invoke scripts/load_agent_identity.py"
    )


def test_postcompact_hook_still_present() -> None:
    """Expects the existing PostCompact hook to remain — no regression of the compact monitor."""
    assert "PostCompact" in _load_settings().get("hooks", {}), (
        "PostCompact hook disappeared — the compact monitor would have nothing to detect"
    )


def _run_loader(project_dir: Path) -> subprocess.CompletedProcess[str]:
    """Runs the loader script with CLAUDE_PROJECT_DIR set to project_dir."""
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)},
        capture_output=True,
        text=True,
    )


def test_loader_injects_hoheitswissen_for_agent_dir(tmp_path: Path) -> None:
    """Injects the full claude.md for a worktree whose basename matches an agents/<slug> dir.

    Expects SessionStart additionalContext with the preamble wrapped in EXTREMELY_IMPORTANT and
    naming the slug, plus the full file content.
    """
    slug = "devops"
    worktree = tmp_path / slug
    (worktree / "agents" / slug).mkdir(parents=True)
    content = "# DevOps Hoheitswissen\nUNIQUE-MARKER-9f3a2b\n"
    (worktree / "agents" / slug / "claude.md").write_text(content)

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "<EXTREMELY_IMPORTANT>" in ctx, "preamble is not wrapped in the EXTREMELY_IMPORTANT tag"
    assert slug in ctx, "preamble does not name the agent slug"
    assert "UNIQUE-MARKER-9f3a2b" in ctx, "full claude.md content was not injected"


def test_loader_no_ops_for_non_agent_dir(tmp_path: Path) -> None:
    """No-ops for a directory whose basename has no agents/<slug>/claude.md.

    For the main checkout or the apptest clone the loader emits nothing and exits 0 —
    no error, no injection.
    """
    worktree = tmp_path / "klartext"  # no agents/klartext/claude.md inside
    worktree.mkdir()

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    assert result.stdout.strip() == "", (
        f"expected no output for a non-agent dir, got: {result.stdout!r}"
    )


def _write_agent_md(tmp_path: Path, slug: str, content: str) -> Path:
    """Creates an agent worktree at tmp_path/slug with agents/slug/claude.md = content."""
    worktree = tmp_path / slug
    (worktree / "agents" / slug).mkdir(parents=True)
    (worktree / "agents" / slug / "claude.md").write_text(content, encoding="utf-8")
    return worktree


def test_session_start_matcher_includes_clear() -> None:
    """Expects the matcher to include 'clear' — re-injects identity after /clear.

    The matcher string is startup|clear|compact; if 'clear' silently drops, a /clear that the
    runtime reports as source=clear would boot without Hoheitswissen.
    """
    matchers = " ".join(entry.get("matcher", "") for entry in _session_start_entries())
    assert "clear" in matchers, (
        "SessionStart matcher must include 'clear': a /clear reported as source=clear must "
        "re-inject the agent's Hoheitswissen, otherwise identity drifts after a clear"
    )


def test_session_start_matcher_includes_compact() -> None:
    """Expects the matcher to include 'compact' — re-injects identity after a compaction.

    A compaction drops the original SessionStart context; without a compact matcher the agent
    loses its Hoheitswissen mid-session.
    """
    matchers = " ".join(entry.get("matcher", "") for entry in _session_start_entries())
    assert "compact" in matchers, (
        "SessionStart matcher must include 'compact': after a compaction the original identity "
        "context is gone, so the hook must re-inject it"
    )


def test_loader_falls_back_to_cwd_when_project_dir_unset(tmp_path: Path) -> None:
    """Derives the slug from the cwd when CLAUDE_PROJECT_DIR is unset.

    The hook command passes CLAUDE_PROJECT_DIR, but the loader documents a cwd fallback. If the
    var is missing (manual run, different launcher), the loader must still find the worktree.
    """
    slug = "devops"
    worktree = _write_agent_md(tmp_path, slug, "# DevOps\nCWD-MARKER-7b1c\n")
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}

    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        env=env,
        cwd=str(worktree),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "CWD-MARKER-7b1c" in ctx, (
        "loader did not fall back to cwd when CLAUDE_PROJECT_DIR was unset"
    )


def test_loader_injects_for_empty_claude_md(tmp_path: Path) -> None:
    """Injects the preamble even when claude.md is empty.

    An empty file is still a file (is_file() is True). The loader must emit valid JSON with the
    EXTREMELY_IMPORTANT preamble, not crash or silently no-op as if the directory were non-agent.
    """
    slug = "devops"
    worktree = _write_agent_md(tmp_path, slug, "")

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    assert result.stdout.strip() != "", "loader no-opped on an empty claude.md instead of injecting"
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "<EXTREMELY_IMPORTANT>" in ctx, "empty claude.md must still get the preamble"


def test_loader_output_is_valid_json(tmp_path: Path) -> None:
    """Emits valid JSON with the SessionStart hook contract a consumer can parse.

    The runtime parses stdout as JSON; if it is malformed or missing the required keys the
    additionalContext never reaches the session.
    """
    slug = "devops"
    worktree = _write_agent_md(tmp_path, slug, "# DevOps\nbody\n")

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    payload = json.loads(result.stdout)  # raises if not valid JSON
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart", (
        "hookEventName must be SessionStart for the runtime to route the context"
    )
    assert isinstance(payload["hookSpecificOutput"]["additionalContext"], str), (
        "additionalContext must be a string"
    )


def test_loader_preserves_json_special_characters(tmp_path: Path) -> None:
    """Round-trips claude.md content containing JSON-special characters intact.

    Quotes, backslashes and newlines in the Hoheitswissen must survive serialization and parse
    back byte-for-byte, otherwise injected identity content is silently corrupted.
    """
    slug = "devops"
    tricky = 'Quote " backslash \\ and newline\nand tab\there: end "marker-x9"'
    worktree = _write_agent_md(tmp_path, slug, tricky)

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert tricky in ctx, "JSON-special characters in claude.md did not survive the round-trip"


def test_loader_no_ops_when_claude_md_is_a_directory(tmp_path: Path) -> None:
    """No-ops when agents/<slug>/claude.md exists but is a directory, not a file.

    is_file() guards against this — a directory named claude.md must not crash read_text() but
    fall through to the graceful no-op.
    """
    slug = "devops"
    worktree = tmp_path / slug
    (worktree / "agents" / slug / "claude.md").mkdir(parents=True)

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    assert result.stdout.strip() == "", (
        f"expected no output when claude.md is a directory, got: {result.stdout!r}"
    )


def test_loader_no_ops_when_agents_dir_present_but_claude_md_missing(tmp_path: Path) -> None:
    """No-ops when agents/<slug>/ exists but contains no claude.md.

    A half-set-up agent directory (folder present, file not yet written) must not crash; it falls
    through to the graceful no-op rather than emitting a partial or erroring.
    """
    slug = "devops"
    worktree = tmp_path / slug
    (worktree / "agents" / slug).mkdir(parents=True)  # no claude.md inside

    result = _run_loader(worktree)

    assert result.returncode == 0, f"loader errored: {result.stderr}"
    assert result.stdout.strip() == "", (
        f"expected no output when claude.md is missing, got: {result.stdout!r}"
    )
