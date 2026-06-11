"""Infrastructure tests: compact-log hook present in .claude/settings.json.

The compact monitor is a two-stage pipeline:
  1. A PostCompact hook in .claude/settings.json appends a line to .claude/compact-log.txt
     every time a compact fires (distinguishing `auto` from `manual`).
  2. The launchd agent (scripts/check-compact-log.sh) reads that log and alerts on new
     `| auto |` entries.

`test_compact_monitor.py` gates stage 2 (the script). This file gates stage 1 (the hook).
Both halves drifted independently during H01: the script lived only on a working-tree branch
for a while, and the hook lived only on `salvage/h01-working-tree` — so a real auto-compact
went undetected because compact-log.txt was never written. A hook that can silently disappear
from `main` must be verified by CI, not by manual inspection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_settings() -> dict[str, Any]:
    """Loads .claude/settings.json from the repository root."""
    settings_path = Path(__file__).parents[3] / ".claude" / "settings.json"
    assert settings_path.exists(), (
        ".claude/settings.json is missing — the compact-log hook cannot be configured"
    )
    return json.loads(settings_path.read_text())


def test_postcompact_hook_is_configured() -> None:
    """Verifies a PostCompact hook is present in .claude/settings.json."""
    settings = _load_settings()
    hooks = settings.get("hooks", {})
    assert "PostCompact" in hooks, (
        "No PostCompact hook in .claude/settings.json — auto-compacts will not be logged "
        "and the compact monitor has nothing to detect"
    )


def test_postcompact_hook_writes_compact_log() -> None:
    """Verifies the PostCompact hook appends to the central compact-log (the monitor's input)."""
    settings = _load_settings()
    post_compact = settings["hooks"]["PostCompact"]
    commands = [
        hook["command"]
        for matcher in post_compact
        for hook in matcher.get("hooks", [])
        if hook.get("type") == "command"
    ]
    assert any("klartext-team-memory/compact-log.txt" in command for command in commands), (
        "The PostCompact hook does not write to the central "
        "klartext-team-memory/compact-log.txt — the launchd monitor reads exactly that file"
    )


def test_postcompact_hook_distinguishes_auto_from_manual() -> None:
    """Verifies the PostCompact hook records both auto and manual compacts distinctly."""
    settings = _load_settings()
    post_compact = settings["hooks"]["PostCompact"]
    matchers = {matcher.get("matcher") for matcher in post_compact}
    assert {"auto", "manual"} <= matchers, (
        "The PostCompact hook must distinguish auto from manual compacts — "
        "the monitor only alerts on `| auto |` entries, so the matcher is what makes "
        "proactive (manual) vs. system-triggered (auto) compacts distinguishable in the log"
    )


def test_postcompact_hook_writes_to_central_pinned_log() -> None:
    """Verifies the hook writes to the central pinned log, not a per-repo/worktree path.

    Once agents run in per-agent git worktrees (Stage 2), a log under the session's
    own project dir would be invisible to the single launchd monitor instance. The
    hook therefore writes to the absolute pinned path
    ($HOME/.claude/klartext-team-memory/compact-log.txt), shared across all worktrees.
    The branch field still derives from $CLAUDE_PROJECT_DIR (`git -C`), so each entry
    records which agent/worktree compacted. A bare relative log path would be wrong.
    """
    settings = _load_settings()
    post_compact = settings["hooks"]["PostCompact"]
    commands = [
        hook["command"]
        for matcher in post_compact
        for hook in matcher.get("hooks", [])
        if hook.get("type") == "command"
    ]
    for command in commands:
        assert "$HOME/.claude/klartext-team-memory/compact-log.txt" in command, (
            "The PostCompact hook must write to the central pinned log "
            '"$HOME/.claude/klartext-team-memory/compact-log.txt" so one monitor '
            "catches every per-agent worktree"
        )
        assert 'git -C "$CLAUDE_PROJECT_DIR"' in command, (
            "The branch field must derive from $CLAUDE_PROJECT_DIR (git -C) so each "
            "log entry records which agent/worktree compacted"
        )
        assert ">> .claude/compact-log.txt" not in command, (
            "The PostCompact hook still uses a bare relative log path"
        )
