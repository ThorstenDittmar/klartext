"""Infrastructure tests: the seed settings.json template (export plan §7.3 artefact templating).

The seed ships a generic `.claude/settings.json` template; an importer renders it from seed.toml.
Only `memory_dir` is parametrized — the hooks already use a portable interpreter + project dir;
project-specific tool permissions (e.g. klartext's venv-pathed semgrep allow) are not generic,
so they stay out of the seed template (the importer adds its own).

The fidelity dogfood: rendering the template with klartext's own seed.toml reproduces klartext's
LIVE `.claude/settings.json` exactly, minus that one project-specific permission — proving the
template is a faithful generalization, not a drifting copy.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]
_TEMPLATE = _REPO_ROOT / "seed" / "templates" / "claude-settings.json.tmpl"
_LIVE_SETTINGS = _REPO_ROOT / ".claude" / "settings.json"
_PROJECT_SPECIFIC_PERM = "Bash(api/.venv/bin/semgrep*)"


def _load_render():
    """Loads seed/render.py as a module (standalone tool, not a package)."""
    spec = importlib.util.spec_from_file_location("seed_render", _REPO_ROOT / "seed" / "render.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_render = _load_render()


def _render_klartext_settings() -> str:
    """Renders the settings template with klartext's own seed.toml."""
    config = _render.load_seed_config(_REPO_ROOT / "seed" / "seed.toml")
    return _render.render(_TEMPLATE.read_text(), config)


def test_settings_template_exists() -> None:
    """Expects the settings.json template to be a committed seed artefact."""
    assert _TEMPLATE.is_file(), f"missing settings template: {_TEMPLATE}"


def test_rendered_settings_is_valid_json_with_no_placeholder_left() -> None:
    """Expects the rendered settings to parse as JSON with every placeholder substituted."""
    rendered = _render_klartext_settings()
    assert "{{" not in rendered and "}}" not in rendered, rendered
    json.loads(rendered)  # raises if invalid


def test_rendered_settings_carries_klartext_memory_dir() -> None:
    """Expects memory_dir to be substituted into autoMemoryDirectory."""
    data = json.loads(_render_klartext_settings())
    assert data["autoMemoryDirectory"] == "~/.claude/klartext-team-memory"


def test_rendered_settings_reproduces_live_minus_project_specific_permission() -> None:
    """Expects the rendered settings to equal klartext's LIVE settings.json, minus the project perm.

    Faithful-generalization dogfood: every klartext literal in settings.json comes from seed.toml
    (memory_dir), so rendering with klartext's seed.toml reproduces the live file — except the one
    project-specific permission the generic template intentionally omits.
    """
    rendered = json.loads(_render_klartext_settings())
    live = json.loads(_LIVE_SETTINGS.read_text())
    live["permissions"]["allow"] = [
        perm for perm in live["permissions"]["allow"] if perm != _PROJECT_SPECIFIC_PERM
    ]
    assert rendered == live
