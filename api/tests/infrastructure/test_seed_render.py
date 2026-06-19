"""Infrastructure tests: the method-seed config source + renderer (seed/render.py).

Phase 1 of the method-seed export (method-seed-export-plan.md §4/§7): `seed.toml` is the single
config source that replaces a fragile global find-replace of klartext literals, and `render`
substitutes its values into templated artefacts. These tests gate the keystone mechanism every
later phase consumes:

  * `load_seed_config` exposes every required §4 key and rejects an incomplete seed.toml;
  * `render` substitutes `{{key}}` placeholders and FAILS LOUD on an unknown placeholder
    (a silently-unsubstituted placeholder shipped to an importer is exactly the bug to avoid);
  * the committed `seed/seed.toml` is itself valid (carries every required key).

seed/render.py is a standalone tool (not a package), so it is loaded via importlib — the same
pattern as test_classify_gate.py.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parents[3]
_MODULE = _REPO_ROOT / "seed" / "render.py"


def _load():
    """Loads seed/render.py as a module (it is a standalone tool, not a package)."""
    spec = importlib.util.spec_from_file_location("seed_render", _MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_render = _load()


def _complete_seed_toml(tmp_path: Path) -> Path:
    """Writes a temp seed.toml carrying every required key, returns its path."""
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name      = "demo"\n'
        'env_prefix        = "DEMO_"\n'
        'memory_dir        = "demo-team-memory"\n'
        'product_domain    = "demo.example"\n'
        'repo_slug         = "acme/demo"\n'
        'worktree_base     = "$HOME/demo-worktrees"\n'
        'identity_preamble = "the demo multi-agent system"\n'
        'interpreter       = ".venv/bin/python3"\n'
        'cli_entrypoint    = "app/cli.py"\n'
        'wow_cli_command   = "demo"\n'
        'wow_trigger_paths = ["CLAUDE.md", "scripts/**"]\n'
    )
    return path


def test_load_seed_config_exposes_every_required_key(tmp_path: Path) -> None:
    """Expects a complete seed.toml to load and expose each required §4 key by name."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert config["project_name"] == "demo"
    assert config["env_prefix"] == "DEMO_"
    assert config["repo_slug"] == "acme/demo"
    assert config["interpreter"] == ".venv/bin/python3"


def test_load_seed_config_rejects_missing_required_key(tmp_path: Path) -> None:
    """Expects a seed.toml missing a required key to raise, naming the missing key."""
    path = tmp_path / "seed.toml"
    path.write_text('project_name = "demo"\n')  # everything else missing
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.load_seed_config(path)
    assert "memory_dir" in str(exc.value)


def test_render_substitutes_placeholders(tmp_path: Path) -> None:
    """Expects `{{key}}` placeholders to be replaced by the matching seed.toml value."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    rendered = _render.render("~/.claude/{{memory_dir}} for {{project_name}}", config)
    assert rendered == "~/.claude/demo-team-memory for demo"


def test_render_tolerates_inner_whitespace(tmp_path: Path) -> None:
    """Expects `{{ key }}` with surrounding whitespace to substitute the same as `{{key}}`."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert _render.render("{{ project_name }}", config) == "demo"


def test_render_raises_on_unknown_placeholder(tmp_path: Path) -> None:
    """Expects an unknown placeholder to FAIL LOUD, not ship as an unsubstituted literal.

    A `{{nope}}` left verbatim in a rendered settings.json / workflow is a silent bug the importer
    inherits — the renderer must refuse it.
    """
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.render("value: {{nope}}", config)
    assert "nope" in str(exc.value)


def test_committed_seed_toml_is_valid() -> None:
    """Expects the committed seed/seed.toml to carry every required key (klartext's example)."""
    config = _render.load_seed_config(_REPO_ROOT / "seed" / "seed.toml")
    assert config["project_name"] == "klartext"
    for key in _render.REQUIRED_KEYS:
        assert config[key], f"committed seed.toml has an empty value for {key}"


# --- phase 3 increment 1: list-valued keys (path lists) + the parametrized CLI entrypoint --------


def test_load_seed_config_preserves_list_values(tmp_path: Path) -> None:
    """Expects a list-valued key (wow_trigger_paths) to load as a list, not a stringified blob."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert config.get_list("wow_trigger_paths") == ["CLAUDE.md", "scripts/**"]


def test_load_seed_config_accepts_empty_list_value(tmp_path: Path) -> None:
    """Pins: an EMPTY list is present-and-valid, not missing — `get_list` returns `[]`.

    The presence check is `key not in data`, so `wow_trigger_paths = []` satisfies REQUIRED_LISTS
    and loads as `[]`. Characterization of current behavior: emptiness is the consumer's concern,
    not the loader's — the loader does not reject an empty trigger list.
    """
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "m"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'wow_cli_command = "x"\n'
        'interpreter = "p"\ncli_entrypoint = "app/cli.py"\nwow_trigger_paths = []\n'
    )
    config = _render.load_seed_config(path)
    assert config.get_list("wow_trigger_paths") == []


def test_load_seed_config_coerces_non_string_list_items_to_str(tmp_path: Path) -> None:
    """Pins: list items are `str()`-coerced, so a numeric TOML list yields string items.

    `wow_trigger_paths = [1, 2]` loads as `["1", "2"]` — the loader normalizes every item to str
    (downstream consumers render these as path literals). Characterization of current behavior.
    """
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "m"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'wow_cli_command = "x"\n'
        'interpreter = "p"\ncli_entrypoint = "app/cli.py"\nwow_trigger_paths = [1, 2]\n'
    )
    config = _render.load_seed_config(path)
    assert config.get_list("wow_trigger_paths") == ["1", "2"]


def test_get_list_on_missing_key_raises(tmp_path: Path) -> None:
    """Expects `get_list` on an absent key to fail loud — distinct from scalar-holds-list.

    The error path differs from `test_list_access_to_scalar_key_raises`: here the key is absent
    (KeyError branch → "unknown seed config list key"), not present-but-scalar.
    """
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    with pytest.raises(_render.SeedConfigError) as exc:
        config.get_list("does_not_exist")
    assert "does_not_exist" in str(exc.value)


def test_load_seed_config_rejects_toml_table_value(tmp_path: Path) -> None:
    """Expects a TOML `[section]` table to be rejected, not silently flattened to a dict-repr str.

    DevOps decision: seed.toml is a flat config (scalars + path lists). A nested table is an
    unexpected shape — flattening it to `"{'key': 'v'}"` would render garbage into a downstream
    artefact. Fail loud (consistent with the unknown-placeholder / malformed-TOML handling), naming
    the offending key.
    """
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "m"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'wow_cli_command = "x"\n'
        'interpreter = "p"\ncli_entrypoint = "app/cli.py"\nwow_trigger_paths = ["x"]\n'
        '[section]\nkey = "v"\n'
    )
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.load_seed_config(path)
    assert "section" in str(exc.value)


def test_load_seed_config_requires_cli_entrypoint(tmp_path: Path) -> None:
    """Expects a seed.toml without cli_entrypoint to be rejected (SA: parametrize, not hardcode)."""
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "m"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'wow_cli_command = "x"\n'
        'interpreter = "p"\nwow_trigger_paths = ["CLAUDE.md"]\n'  # cli_entrypoint absent
    )
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.load_seed_config(path)
    assert "cli_entrypoint" in str(exc.value)


def test_load_seed_config_requires_wow_trigger_paths(tmp_path: Path) -> None:
    """Expects a seed.toml without the wow_trigger_paths list to be rejected."""
    path = tmp_path / "seed.toml"
    path.write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "m"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'wow_cli_command = "x"\n'
        'interpreter = "p"\ncli_entrypoint = "app/cli.py"\n'  # wow_trigger_paths absent
    )
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.load_seed_config(path)
    assert "wow_trigger_paths" in str(exc.value)


def test_scalar_access_to_list_key_raises(tmp_path: Path) -> None:
    """Expects `config[list_key]` to fail loud — a list is not a scalar substitution."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    with pytest.raises(_render.SeedConfigError):
        _ = config["wow_trigger_paths"]


def test_list_access_to_scalar_key_raises(tmp_path: Path) -> None:
    """Expects `config.get_list(scalar_key)` to fail loud rather than silently wrap a scalar."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    with pytest.raises(_render.SeedConfigError):
        config.get_list("project_name")


def test_committed_seed_toml_has_cli_entrypoint_and_generic_trigger_paths() -> None:
    """Expects klartext's seed.toml to carry the parametrized CLI path + SA's generic trigger list.

    SA §9: api/cli.py is product-stack → parametrized as cli_entrypoint, NOT a trigger-list literal.
    The generic WoW surfaces (incl. .github/workflows/**, now live via #183) ship in the list.
    """
    config = _render.load_seed_config(_REPO_ROOT / "seed" / "seed.toml")
    assert config["cli_entrypoint"] == "api/cli.py"
    paths = config.get_list("wow_trigger_paths")
    assert ".github/workflows/**" in paths
    assert "api/cli.py" not in paths  # product path is parametrized separately, not a list literal


def test_render_returns_template_without_placeholders_unchanged(tmp_path: Path) -> None:
    """Expects a template with no `{{...}}` placeholder to pass through verbatim."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert _render.render("plain text, no placeholders", config) == "plain text, no placeholders"


def test_render_empty_template_returns_empty_string(tmp_path: Path) -> None:
    """Expects an empty template to render to the empty string (no crash on zero matches)."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert _render.render("", config) == ""


def test_render_substitutes_repeated_placeholder(tmp_path: Path) -> None:
    """Expects the same placeholder used twice to be substituted at both sites."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert _render.render("{{project_name}} {{project_name}}", config) == "demo demo"


def test_render_substitutes_adjacent_placeholders(tmp_path: Path) -> None:
    """Expects two placeholders with no separator to both substitute (no greedy over-match)."""
    config = _render.load_seed_config(_complete_seed_toml(tmp_path))
    assert _render.render("{{project_name}}{{env_prefix}}", config) == "demoDEMO_"


def test_render_is_single_pass_does_not_re_substitute_value(tmp_path: Path) -> None:
    """Pins single-pass substitution: a value containing `{{...}}` is NOT re-rendered.

    `worktree_base` carries a literal `$HOME/...`; here we use a config whose value is itself a
    placeholder-looking string to prove `render` does one regex pass and leaves the value verbatim
    (no recursion / no infinite re-expansion). Characterization of current, correct behavior.
    """
    config = _render.SeedConfig({"a": "{{b}}", "b": "DEEP"})
    assert _render.render("{{a}}", config) == "{{b}}"


def test_load_seed_config_names_all_missing_keys(tmp_path: Path) -> None:
    """Expects a seed.toml missing several keys to name more than one in the error message."""
    path = tmp_path / "seed.toml"
    path.write_text('project_name = "demo"\n')  # all other required keys absent
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.load_seed_config(path)
    message = str(exc.value)
    assert "env_prefix" in message
    assert "interpreter" in message


def test_load_seed_config_wraps_malformed_toml_with_path_context(tmp_path: Path) -> None:
    """Expects malformed TOML to raise SeedConfigError naming the file, not a bare decode error.

    DevOps decision: this tool is importer-facing — a raw tomllib.TOMLDecodeError with no "which
    seed.toml" context is poor DX and inconsistent with the contextual missing-key error. The
    loader wraps the decode failure as SeedConfigError mentioning the path.
    """
    path = tmp_path / "seed.toml"
    path.write_text("project_name = \nbroken")
    with pytest.raises(_render.SeedConfigError) as exc:
        _render.load_seed_config(path)
    assert "seed.toml" in str(exc.value)
