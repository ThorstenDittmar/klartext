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
from pathlib import Path


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
