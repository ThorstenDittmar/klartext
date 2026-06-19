"""Infrastructure tests: the method-seed bundle assembly (Model B, OE bundling decision 2026-06-19).

seed/ stores only the .tmpl files + this assembly mechanism (+ later OE's MANIFEST). `assemble`
produces a self-contained bundle on demand: render each template from seed.toml, copy each as-is
file verbatim from the live repo. No as-is file is stored in seed/ — single source of truth = live;
bundle is the self-contained artefact. The manifest format here is a simple interim one (OE defines
the authoritative format); the assembly mechanism is built against it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parents[3]
_SEED_DIR = _REPO_ROOT / "seed"


def _load_assemble():
    """Loads seed/assemble.py, with seed/ on sys.path so its internal `import render` resolves."""
    if str(_SEED_DIR) not in sys.path:
        sys.path.insert(0, str(_SEED_DIR))
    spec = importlib.util.spec_from_file_location("seed_assemble", _SEED_DIR / "assemble.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_assemble = _load_assemble()


def _fake_repo(tmp_path: Path) -> Path:
    """Builds a fake source repo: a seed.toml, a template, and an as-is file."""
    repo = tmp_path / "repo"
    (repo / "seed" / "templates").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "seed" / "seed.toml").write_text(
        'project_name = "demo"\nenv_prefix = "D_"\nmemory_dir = "demo-mem"\nproduct_domain = "d"\n'
        'repo_slug = "a/d"\nworktree_base = "$HOME/w"\nidentity_preamble = "x"\n'
        'interpreter = "p"\ncli_entrypoint = "app/cli.py"\nwow_trigger_paths = ["CLAUDE.md"]\n'
    )
    (repo / "seed" / "templates" / "greeting.txt.tmpl").write_text("hello {{project_name}}\n")
    (repo / "src" / "asis.txt").write_text("verbatim content\n")
    return repo


def test_assemble_renders_templates_and_copies_as_is(tmp_path: Path) -> None:
    """Expects assemble to render a template from seed.toml and copy an as-is file verbatim."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(
        templates=[("seed/templates/greeting.txt.tmpl", "greeting.txt")],
        as_is=[("src/asis.txt", "src/asis.txt")],
    )

    _assemble.assemble(manifest, repo, out)

    assert (out / "greeting.txt").read_text() == "hello demo\n"
    assert (out / "src" / "asis.txt").read_text() == "verbatim content\n"


def test_assemble_fails_loud_on_missing_as_is_source(tmp_path: Path) -> None:
    """Expects a missing as-is source to raise, not silently skip — the bundle must be complete."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(templates=[], as_is=[("src/nope.txt", "src/nope.txt")])
    with pytest.raises(_assemble.AssemblyError) as exc:
        _assemble.assemble(manifest, repo, out)
    assert "nope.txt" in str(exc.value)


def test_assemble_fails_loud_on_missing_template_source(tmp_path: Path) -> None:
    """Expects a missing template source to raise rather than produce an incomplete bundle."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(templates=[("seed/templates/gone.tmpl", "gone")], as_is=[])
    with pytest.raises(_assemble.AssemblyError) as exc:
        _assemble.assemble(manifest, repo, out)
    assert "gone" in str(exc.value)


def test_load_manifest_parses_template_and_as_is_entries(tmp_path: Path) -> None:
    """Expects the interim TOML manifest to parse into template + as-is (src, dest) pairs."""
    path = tmp_path / "manifest.toml"
    path.write_text(
        "[[template]]\n"
        'src = "seed/templates/claude-settings.json.tmpl"\n'
        'dest = ".claude/settings.json"\n\n'
        "[[as_is]]\n"
        'src = ".github/workflows/agent-provenance.yml"\n'
        'dest = ".github/workflows/agent-provenance.yml"\n'
    )
    manifest = _assemble.load_manifest(path)
    assert manifest.templates == [
        ("seed/templates/claude-settings.json.tmpl", ".claude/settings.json")
    ]
    assert manifest.as_is == [
        (".github/workflows/agent-provenance.yml", ".github/workflows/agent-provenance.yml")
    ]
