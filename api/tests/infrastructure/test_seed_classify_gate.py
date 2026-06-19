"""Infrastructure tests: the config-driven classify-gate pattern source (export phase 3.2).

The shipped seed gate (B-Seed-only) sources its trigger patterns from seed.toml instead of a
hardcoded list: `trigger_patterns_from_config` builds TRIGGER_PATTERNS from `wow_trigger_paths`
(SA's generic-WoW classification) plus the parametrized `cli_entrypoint` (the product CLI path).

Critically, a CONSISTENCY DOGFOOD pins that this config-derived list matches klartext's LIVE
hardcoded `scripts/classify_gate.py` TRIGGER_PATTERNS. B-Seed-only leaves the live gate hardcoded
for now, so the two sources must stay in sync until the live gate is unified (B-voll, tracked in
team memory) — this test is the guard that catches drift between them.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]


def _load(name: str, relpath: str):
    """Loads a standalone module (not a package) via importlib."""
    spec = importlib.util.spec_from_file_location(name, _REPO_ROOT / relpath)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_render = _load("seed_render", "seed/render.py")
_live_gate = _load("live_classify_gate", "scripts/classify_gate.py")


def test_trigger_patterns_from_config_combines_paths_and_cli(tmp_path: Path) -> None:
    """Expects the gate patterns = wow_trigger_paths + the parametrized cli_entrypoint."""
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "m"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'interpreter = "p"\ncli_entrypoint = "app/cli.py"\n'
        'wow_trigger_paths = ["CLAUDE.md", "scripts/**"]\n'
    )
    config = _render.load_seed_config(path)
    patterns = _render.trigger_patterns_from_config(config)
    assert patterns == ["CLAUDE.md", "scripts/**", "app/cli.py"]


def test_config_patterns_match_live_gate_trigger_patterns() -> None:
    """Pins consistency: klartext's seed.toml-derived patterns == the LIVE classify_gate list.

    B-Seed-only keeps the live gate hardcoded; this guards against the two sources drifting until
    the live gate is unified to read from seed.toml (B-voll, deferred).
    """
    config = _render.load_seed_config(_REPO_ROOT / "seed" / "seed.toml")
    derived = sorted(_render.trigger_patterns_from_config(config))
    live = sorted(_live_gate.TRIGGER_PATTERNS)
    assert derived == live, (
        "seed.toml-derived trigger patterns drifted from the live classify_gate list — "
        f"derived={derived} live={live}"
    )
