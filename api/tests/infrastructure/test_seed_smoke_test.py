"""Infrastructure tests: the bootstrap smoke-test (seed/smoke_test.py, export plan §10).

The smoke-test stands up a throwaway project from the seed + a DEMO seed.toml and asserts the
rendered fabric is complete, runnable, and source-literal-clean. These tests (a) run it end-to-end
against the repo and expect a pass, and (b) prove its check helpers are NON-VACUOUS — each reports
a failure on a deliberately-broken bundle, so a real regression cannot slip past green.
"""

from __future__ import annotations

import importlib.util
import sys
import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]


def _load(name: str, relpath: str):
    """Loads a standalone seed tool module (not a package) via importlib."""
    spec = importlib.util.spec_from_file_location(name, _REPO_ROOT / relpath)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_assemble = _load("assemble", "seed/assemble.py")
_smoke = _load("smoke_test", "seed/smoke_test.py")


def test_bootstrap_smoke_test_passes_end_to_end() -> None:
    """Expects the real bootstrap smoke-test to pass (fresh project, source-literal-clean)."""
    failures = _smoke.run_smoke_test(_REPO_ROOT)
    assert failures == [], "bootstrap smoke-test failed:\n" + "\n".join(failures)


def test_rendered_target_surface_is_non_empty() -> None:
    """Expects the zero-literal surface (template + config_source targets) to be non-empty.

    Guards against a vacuous zero-literal check: if the surface were empty, the check would pass
    trivially while inspecting nothing.
    """
    manifest = _assemble.load_manifest(_REPO_ROOT / "seed" / "MANIFEST.toml")
    targets = _smoke._rendered_and_config_targets(manifest)
    assert len(targets) >= 8, f"expected the rendered/config surface to be sizeable, got {targets}"


def _manifest_of(*entries: tuple[str, str, str]) -> object:
    """Builds an assemble.Manifest from (path, disposition, target) triples."""
    return _assemble.Manifest(
        entries=[_assemble.Entry(path=p, disposition=d, target=t, note="") for p, d, t in entries]
    )


def test_zero_literal_check_flags_a_surviving_source_slug(tmp_path: Path) -> None:
    """Non-vacuous: a rendered target still carrying the source slug is reported as a failure."""
    bundle = tmp_path / "bundle"
    (bundle / "scripts").mkdir(parents=True)
    (bundle / "scripts" / "leaky.py").write_text("# this still mentions klartext\n")
    manifest = _manifest_of(("seed/templates/leaky.py.tmpl", "template", "scripts/leaky.py"))
    failures = _smoke._check_zero_source_literal(manifest, bundle, "klartext")
    assert failures and "leaky.py" in failures[0]


def test_zero_literal_check_passes_a_clean_target(tmp_path: Path) -> None:
    """A rendered target free of the source slug yields no failure (the green path)."""
    bundle = tmp_path / "bundle"
    (bundle / "scripts").mkdir(parents=True)
    (bundle / "scripts" / "clean.py").write_text("# fully parameterized, says acme\n")
    manifest = _manifest_of(("seed/templates/clean.py.tmpl", "template", "scripts/clean.py"))
    assert _smoke._check_zero_source_literal(manifest, bundle, "klartext") == []


def test_completeness_check_flags_a_missing_target(tmp_path: Path) -> None:
    """Non-vacuous: a manifest target absent from the bundle is reported as a failure."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = _manifest_of(("seed/templates/x.tmpl", "template", "scripts/x.py"))
    result = _assemble.AssembleResult(produced=[], deferred=[])
    failures = _smoke._check_completeness(manifest, result, bundle)
    assert failures and "scripts/x.py" in failures[0]


def test_completeness_check_flags_deferred_drift(tmp_path: Path) -> None:
    """Non-vacuous: an assembled deferred set that diverges from the manifest is reported."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = _manifest_of(("some/plist", "deferred", "some/plist"))
    # manifest declares 'some/plist' deferred, but assembly reported nothing deferred → drift
    result = _assemble.AssembleResult(produced=[], deferred=[])
    failures = _smoke._check_completeness(manifest, result, bundle)
    assert any("deferred set drift" in f for f in failures)


# _check_runnable_fabric — was previously unguarded; these prove it is non-vacuous


def _real_bundle(tmp_path: Path) -> Path:
    """Assembles a real bundle from the live tree + demo seed (what run_smoke_test inspects)."""
    consumer = tmp_path / "consumer"
    consumer.mkdir()
    _smoke._build_consumer_repo(_REPO_ROOT, consumer)
    manifest = _assemble.load_manifest(consumer / "seed" / "MANIFEST.toml")
    bundle = tmp_path / "bundle"
    _assemble.assemble(manifest, consumer, bundle)
    return bundle


def test_runnable_fabric_passes_on_the_real_bundle(tmp_path: Path) -> None:
    """Green path: the fabric check finds no failure on a genuinely-rendered bundle.

    Pairs with the negative cases below: a clean bundle must yield [] or the negatives are moot.
    """
    assert _smoke._check_runnable_fabric(_real_bundle(tmp_path)) == []


def test_runnable_fabric_flags_invalid_settings_json(tmp_path: Path) -> None:
    """Non-vacuous: a rendered settings.json that is not valid JSON is reported."""
    bundle = tmp_path / "bundle"
    (bundle / ".claude").mkdir(parents=True)
    (bundle / ".claude" / "settings.json").write_text("{ not valid json ,, }")
    failures = _smoke._check_runnable_fabric(bundle)
    assert any("settings.json is invalid JSON" in f for f in failures)


def test_runnable_fabric_flags_uncompilable_python(tmp_path: Path) -> None:
    """Non-vacuous: a rendered .py that does not byte-compile is reported."""
    bundle = tmp_path / "bundle"
    (bundle / "scripts").mkdir(parents=True)
    (bundle / "scripts" / "broken.py").write_text("def (:\n")
    failures = _smoke._check_runnable_fabric(bundle)
    assert any("broken.py does not compile" in f for f in failures)


def test_runnable_fabric_flags_invalid_bash(tmp_path: Path) -> None:
    """Non-vacuous: a rendered .sh that fails `bash -n` is reported."""
    bundle = tmp_path / "bundle"
    (bundle / "scripts").mkdir(parents=True)
    (bundle / "scripts" / "broken.sh").write_text("if then fi do done bad(((\n")
    failures = _smoke._check_runnable_fabric(bundle)
    assert any("broken.sh is invalid bash" in f for f in failures)


def test_runnable_fabric_flags_wrong_classify_gate_verdict(tmp_path: Path) -> None:
    """Non-vacuous: a classify_gate that exits 0 on a WoW path (should be rc=1) is reported.

    A gate that waves a WoW change through with no label is the regression this check exists for.
    """
    bundle = tmp_path / "bundle"
    (bundle / "scripts").mkdir(parents=True)
    (bundle / "scripts" / "classify_gate.py").write_text("import sys; sys.exit(0)\n")
    failures = _smoke._check_runnable_fabric(bundle)
    assert any("classify_gate did not give the expected verdict" in f for f in failures)


def test_runnable_fabric_flags_inbox_roundtrip_losing_the_body(tmp_path: Path) -> None:
    """Non-vacuous: an inbox.sh whose read does not return the sent body is reported.

    `send`/`read` both exit 0 here — only the body is dropped, so the check must inspect content,
    not just exit codes.
    """
    bundle = tmp_path / "bundle"
    (bundle / "scripts").mkdir(parents=True)
    (bundle / "scripts" / "inbox.sh").write_text(
        '#!/usr/bin/env bash\nif [ "$1" = read ]; then echo "nothing here"; fi\nexit 0\n'
    )
    failures = _smoke._check_runnable_fabric(bundle)
    assert any("roundtrip lost the message body" in f for f in failures)


def test_inbox_env_prefix_matches_the_demo_seed(tmp_path: Path) -> None:
    """Brittleness guard: the hardcoded inbox prefix must equal the demo seed's env_prefix.

    The fabric check sets `<prefix>INBOX_BASE` to point the rendered inbox.sh at a temp base. If the
    two drift, the override would silently miss (inbox.sh would fall back to $HOME/...) and the
    roundtrip could still pass while testing nothing. This keeps the two in lockstep.
    """
    demo = tomllib.loads(_smoke._DEMO_SEED)
    assert _smoke._inbox_env_prefix() == demo["env_prefix"]
