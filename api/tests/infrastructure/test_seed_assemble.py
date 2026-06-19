"""Infrastructure tests: the method-seed bundle assembly (Model B, reconciled to the #187 manifest).

seed/ stores only the .tmpl files + this assembly mechanism + the MANIFEST. `assemble` produces a
self-contained bundle on demand from `seed/MANIFEST.toml`, routing by disposition:

  * as_is / config_source → copy `path` verbatim from the live repo to `target`
  * template              → render `path` from seed.toml to `target`
  * declared / exclude    → never shipped (prerequisite / product boundary) — not copied
  * deferred              → in-scope but not yet shippable — skipped + reported as a known gap
  * generated             → produced by assembly logic; none exist yet → fail loud if encountered

The seam dogfood loads the real `seed/MANIFEST.toml` and asserts every disposition is recognised —
SA's #188 contract: the loader reads the authoritative manifest, never diverging silently.
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
    """Builds a fake source repo: a seed.toml, a template, an as-is file."""
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


def _entry(_assemble_mod, **kw):
    """Builds an Entry with sensible defaults (target defaults to path; note empty)."""
    return _assemble_mod.Entry(
        path=kw["path"],
        disposition=kw["disposition"],
        target=kw.get("target", kw["path"]),
        note=kw.get("note", ""),
    )


def test_assemble_renders_templates_and_copies_as_is_and_config_source(tmp_path: Path) -> None:
    """Expects template→render, as_is→copy, config_source→copy verbatim."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(
        entries=[
            _entry(
                _assemble,
                path="seed/templates/greeting.txt.tmpl",
                disposition="template",
                target="greeting.txt",
            ),
            _entry(_assemble, path="src/asis.txt", disposition="as_is"),
            _entry(_assemble, path="seed/seed.toml", disposition="config_source"),
        ]
    )

    result = _assemble.assemble(manifest, repo, out)

    assert (out / "greeting.txt").read_text() == "hello demo\n"
    assert (out / "src" / "asis.txt").read_text() == "verbatim content\n"
    assert (out / "seed" / "seed.toml").exists()  # config_source ships verbatim to be filled
    assert set(result.produced) == {"greeting.txt", "src/asis.txt", "seed/seed.toml"}


def test_assemble_skips_declared_exclude_and_reports_deferred_as_gap(tmp_path: Path) -> None:
    """Expects declared/exclude to be skipped silently and deferred reported as a known gap."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(
        entries=[
            _entry(_assemble, path="superpowers", disposition="declared"),
            _entry(_assemble, path="api/domain.py", disposition="exclude"),
            _entry(_assemble, path="scripts/classify_gate.py", disposition="deferred"),
        ]
    )

    result = _assemble.assemble(manifest, repo, out)

    assert result.produced == []
    assert result.deferred == ["scripts/classify_gate.py"]
    assert not any(out.rglob("*"))  # nothing copied


def test_assemble_fails_loud_on_missing_source(tmp_path: Path) -> None:
    """Expects a missing as_is/template source to raise — never a silently partial bundle."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(
        entries=[_entry(_assemble, path="src/nope.txt", disposition="as_is")]
    )
    with pytest.raises(_assemble.AssemblyError) as exc:
        _assemble.assemble(manifest, repo, out)
    assert "nope.txt" in str(exc.value)


def test_assemble_fails_loud_on_generated_disposition(tmp_path: Path) -> None:
    """Expects 'generated' (assembly-from-logic, none implemented) to fail loud if encountered."""
    repo = _fake_repo(tmp_path)
    out = tmp_path / "bundle"
    manifest = _assemble.Manifest(
        entries=[_entry(_assemble, path="index", disposition="generated")]
    )
    with pytest.raises(_assemble.AssemblyError) as exc:
        _assemble.assemble(manifest, repo, out)
    assert "generated" in str(exc.value).lower()


def test_load_manifest_rejects_unknown_disposition(tmp_path: Path) -> None:
    """Expects an unknown disposition value to fail loud at load (the seam guard)."""
    path = tmp_path / "manifest.toml"
    path.write_text('[[entry]]\npath = "x"\ndisposition = "frobnicate"\n')
    with pytest.raises(_assemble.AssemblyError) as exc:
        _assemble.load_manifest(path)
    assert "frobnicate" in str(exc.value)


def test_load_manifest_rejects_empty_manifest(tmp_path: Path) -> None:
    """Expects a manifest with no [[entry]] to fail loud (schema mismatch / empty)."""
    path = tmp_path / "manifest.toml"
    path.write_text('title = "not a manifest"\n')
    with pytest.raises(_assemble.AssemblyError):
        _assemble.load_manifest(path)


def test_load_manifest_target_defaults_to_path(tmp_path: Path) -> None:
    """Expects an entry without an explicit target to default target to path."""
    path = tmp_path / "manifest.toml"
    path.write_text('[[entry]]\npath = "seed/render.py"\ndisposition = "as_is"\n')
    manifest = _assemble.load_manifest(path)
    assert manifest.entries[0].target == "seed/render.py"


def test_load_manifest_reads_the_real_seed_manifest_with_known_dispositions() -> None:
    """Seam dogfood: the real seed/MANIFEST.toml loads and every disposition is recognised.

    This is SA's #188 contract realised: the loader reads the authoritative #187 manifest directly,
    so the two cannot silently diverge. Every entry routes through a known disposition.
    """
    manifest = _assemble.load_manifest(_REPO_ROOT / "seed" / "MANIFEST.toml")
    assert len(manifest.entries) >= 20
    for entry in manifest.entries:
        assert entry.disposition in _assemble.KNOWN_DISPOSITIONS, entry
