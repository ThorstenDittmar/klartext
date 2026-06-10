"""Infrastructure tests: compact monitor script existence and executability.

The launchd agent (com.klartext.compact-monitor) installed by setup.sh references
scripts/check-compact-log.sh by absolute path. If that script is absent from the
repository, the agent silently fails — every invocation logs "No such file or directory"
and no auto-compact alert is ever sent.

This test provides the mechanical gate that was missing during the H01 sprint:
a committed script that can drift back to "absent" after a branch switch must be
verified by CI, not by manual inspection.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[3] / "scripts" / "check-compact-log.sh"


def test_compact_monitor_script_exists() -> None:
    """Verifies check-compact-log.sh is present in the repository."""
    script = Path(__file__).parents[3] / "scripts" / "check-compact-log.sh"
    assert script.exists(), (
        "scripts/check-compact-log.sh is missing — the launchd compact-monitor agent "
        "will fail silently until it is restored"
    )


def test_compact_monitor_script_is_executable() -> None:
    """Verifies check-compact-log.sh is executable (required by launchd)."""
    script = Path(__file__).parents[3] / "scripts" / "check-compact-log.sh"
    assert os.access(script, os.X_OK), (
        "scripts/check-compact-log.sh is not executable — "
        "run: chmod +x scripts/check-compact-log.sh"
    )


def test_compact_monitor_plist_template_exists() -> None:
    """Verifies the launchd plist template is present (required by setup.sh)."""
    template = Path(__file__).parents[3] / "scripts" / "com.klartext.compact-monitor.plist.template"
    assert template.exists(), (
        "scripts/com.klartext.compact-monitor.plist.template is missing — "
        "setup.sh cannot install the compact monitor launchd agent"
    )


def test_monitor_does_not_crash_on_non_auto_new_line(tmp_path: Path) -> None:
    """A new line without `| auto |` must exit 0 and advance state, not crash.

    Regression: under `set -euo pipefail`, `grep "| auto |"` on a new line with no
    match returned exit 1, aborting the script before it updated the lastcheck state.
    A single manual compact then wedged the monitor — every hourly run re-scanned the
    same line, crashed again, and the state never advanced. Found by the 3rd monitor
    trial (2026-06-10). This path never calls osascript, so the test is CI-safe.
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    log = claude_dir / "compact-log.txt"
    log.write_text("2026-06-10T16:00:00 | manual | some-branch\n")

    result = subprocess.run(
        ["bash", str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"check-compact-log.sh crashed on a non-auto new line (exit {result.returncode}): "
        f"{result.stderr}"
    )
    state = (claude_dir / "compact-log-lastcheck").read_text().strip()
    assert state == "1", (
        f"State did not advance past the processed line (lastcheck={state!r}); "
        "the monitor would re-scan and re-crash on every run"
    )
    assert not (claude_dir / "compact-monitor-digest.txt").exists(), (
        "A manual compact must not produce a digest entry — only `| auto |` alerts"
    )
