"""Infrastructure tests: the config-driven classify-gate pattern source (export phase 3.2).

The shipped seed gate sources its trigger patterns from seed.toml instead of a hardcoded list:
`trigger_patterns_from_config` builds TRIGGER_PATTERNS from `wow_trigger_paths` (SA's generic-WoW
classification) plus the parametrized `cli_entrypoint` (the product CLI path).

Critically, a CONSISTENCY DOGFOOD pins that this config-derived list matches klartext's LIVE
`scripts/classify_gate.py` TRIGGER_PATTERNS. Both now read seed.toml (B-voll done — the live gate
no longer hardcodes the list), so seed.toml is the single source of truth; this test guards against
the two derivation implementations drifting.
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

    Both the seed renderer and the live gate now derive their patterns from seed.toml (B-voll done);
    this guards against the two derivation implementations drifting from one another.
    """
    config = _render.load_seed_config(_REPO_ROOT / "seed" / "seed.toml")
    derived = sorted(_render.trigger_patterns_from_config(config))
    live = sorted(_live_gate.TRIGGER_PATTERNS)
    assert derived == live, (
        "seed.toml-derived trigger patterns drifted from the live classify_gate list — "
        f"derived={derived} live={live}"
    )
