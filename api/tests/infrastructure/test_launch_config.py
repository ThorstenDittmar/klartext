"""Infrastructure test: the project-scoped Preview launch config (`.claude/launch.json`).

Claude Code Desktop reads `launch.json` **project-scoped** from the selected project root's
`.claude/` directory. klartext's config historically lived only in the user-global
`~/.claude/launch.json` with an **absolute** frontend path (`/Users/thormar/klartext/frontend`) —
machine-dependent and an isolation risk (it could leak into a sibling project's session as a
fallback). F1/#3a moves it into the repo at `.claude/launch.json` with **portable, relative** args
so it is committable and travels with the checkout.

This test pins portability: the config exists, drives the frontend on port 5173, and carries no
absolute machine path.
"""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LAUNCH_JSON = _REPO_ROOT / ".claude" / "launch.json"


def test_launch_json_exists() -> None:
    """Expects the project-scoped launch config to live in the repo at .claude/launch.json."""
    assert _LAUNCH_JSON.is_file(), "missing .claude/launch.json (project-scoped Preview config)"


def test_launch_json_defines_frontend_on_port_5173() -> None:
    """Expects a 'frontend' configuration that runs the Vite dev server on port 5173."""
    config = json.loads(_LAUNCH_JSON.read_text())
    frontend = next((c for c in config["configurations"] if c.get("name") == "frontend"), None)
    assert frontend is not None, "no 'frontend' configuration in launch.json"
    assert frontend["port"] == 5173


def test_launch_json_uses_a_relative_frontend_prefix() -> None:
    """Expects the frontend args to use the relative './frontend' prefix, not an absolute path."""
    config = json.loads(_LAUNCH_JSON.read_text())
    frontend = next(c for c in config["configurations"] if c.get("name") == "frontend")
    args = frontend["runtimeArgs"]
    assert "--prefix" in args, "expected an npm --prefix arg"
    prefix = args[args.index("--prefix") + 1]
    assert prefix == "frontend", f"expected relative prefix 'frontend', got {prefix!r}"


def test_launch_json_has_no_absolute_machine_path() -> None:
    """Expects no absolute machine path anywhere in the config — it must be portable/committable."""
    raw = _LAUNCH_JSON.read_text()
    assert "/Users/" not in raw, "launch.json carries an absolute machine path — not portable"
    assert "/home/" not in raw, "launch.json carries an absolute machine path — not portable"
