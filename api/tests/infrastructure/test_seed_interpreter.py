"""Infrastructure tests: the portable interpreter shim template (export plan §7 phase 2).

The venv coupling that blocks importability lives in `.pre-commit-config.yaml` + the CLI call
(`api/.venv/bin/python …`). Phase 2 removes the hardcoded layout by shipping a shim TEMPLATE
rendered from `seed.toml`'s `interpreter` value: WoW hooks invoke a stable `bin/` path, and
changing the interpreter is a one-line seed.toml edit instead of re-editing every hook.

These tests gate that the committed shim template renders, via the phase-1 renderer, into a valid
shim that execs the configured interpreter and forwards its arguments — with no placeholder left.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]
_MODULE = _REPO_ROOT / "seed" / "render.py"
_SHIM_TEMPLATE = _REPO_ROOT / "seed" / "templates" / "bin-seed-python.tmpl"


def _load():
    """Loads seed/render.py as a module (standalone tool, not a package)."""
    spec = importlib.util.spec_from_file_location("seed_render", _MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_render = _load()


def _demo_config():
    """A SeedConfig with a recognisable interpreter value for shim assertions."""
    return _render.SeedConfig(
        {"interpreter": "/opt/acme/.venv/bin/python3", "project_name": "demo"}
    )


def test_committed_shim_template_exists() -> None:
    """Expects the interpreter shim template to be a committed seed artefact."""
    assert _SHIM_TEMPLATE.is_file(), f"missing shim template: {_SHIM_TEMPLATE}"


def test_rendered_shim_execs_configured_interpreter_and_forwards_args() -> None:
    """Expects the rendered shim to exec the seed.toml interpreter and forward its arguments."""
    rendered = _render.render(_SHIM_TEMPLATE.read_text(), _demo_config())
    assert 'exec /opt/acme/.venv/bin/python3 "$@"' in rendered


def test_rendered_shim_has_a_shebang() -> None:
    """Expects the rendered shim to start with a shell shebang so it is directly executable."""
    rendered = _render.render(_SHIM_TEMPLATE.read_text(), _demo_config())
    assert rendered.startswith("#!"), rendered.splitlines()[:1]


def test_rendered_shim_leaves_no_placeholder() -> None:
    """Expects no `{{…}}` placeholder to remain in the rendered shim (fully substituted)."""
    rendered = _render.render(_SHIM_TEMPLATE.read_text(), _demo_config())
    assert "{{" not in rendered and "}}" not in rendered, rendered
