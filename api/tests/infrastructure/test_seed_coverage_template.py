"""Infrastructure tests: the seed check_test_coverage template (export plan §7.3 / QA verdict).

Per QA's method-seed verdict, only Coverage-Invariant 1 (source->test) ships as live CODE; the
router-health (inv. 2) and supabase-integration-marker (inv. 3) checks are documented patterns, not
config-driven live checks (a consumer on a foreign stack would inherit dead code + dead config). So
the seed template:
  * keeps ONLY check_test_files_exist() + main() wired to that single check;
  * STRIPS check_router_health_tests() and check_supabase_integration_markers();
  * sources its config (source_dirs, excluded_files, test_file_overrides, backend_dir, tests_dir)
    from seed.toml at RUNTIME — like scripts/classify_gate.py — so seed.toml is the single source.

The template carries one scalar placeholder ({{project_name}} in the docstring); the rest is
runtime config, so render() is a near-passthrough. These tests render + assemble it and run the
rendered checker against a synthetic repo to prove it reads config and does invariant 1 only.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]
_TEMPLATE = _REPO_ROOT / "seed" / "templates" / "check_test_coverage.py.tmpl"


def _load_render():
    """Loads seed/render.py as a module (standalone tool, not a package)."""
    spec = importlib.util.spec_from_file_location("seed_render", _REPO_ROOT / "seed" / "render.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_render = _load_render()

_DEMO_SEED = (
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
    'source_dirs       = ["models", "services"]\n'
    'excluded_files    = ["__init__.py"]\n'
    "test_file_overrides = []\n"
    'backend_dir       = "app"\n'
    'tests_dir         = "app/tests"\n'
)


def _render_demo() -> str:
    """Renders the coverage template with the demo seed.toml."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        seed = Path(d) / "seed.toml"
        seed.write_text(_DEMO_SEED)
        cfg = _render.load_seed_config(seed)
        return _render.render(_TEMPLATE.read_text(), cfg)


def test_coverage_template_exists() -> None:
    """Expects the check_test_coverage template to be a committed seed artefact."""
    assert _TEMPLATE.is_file(), f"missing template: {_TEMPLATE}"


def test_template_renders_clean_and_compiles() -> None:
    """Expects render (demo) to leave no klartext literal / placeholder and to byte-compile."""
    import py_compile
    import tempfile

    rendered = _render_demo()
    assert "klartext" not in rendered.lower(), "un-parametrized klartext literal"
    assert "{{" not in rendered and "}}" not in rendered, "unsubstituted placeholder"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as h:
        h.write(rendered)
        py_compile.compile(h.name, doraise=True)


def test_invariants_2_and_3_are_stripped() -> None:
    """Expects the seed template to drop the router-health / supabase-marker checks (QA verdict)."""
    src = _TEMPLATE.read_text()
    assert "check_router_health_tests" not in src, "inv.2 must be stripped"
    assert "check_supabase_integration_markers" not in src, "inv.3 must be stripped"
    assert "check_test_files_exist" in src, "inv.1 must be present"


def _run_rendered_checker(
    tmp_path: Path, *, with_missing_test: bool
) -> subprocess.CompletedProcess[str]:
    """Assembles a synthetic consumer repo from the rendered template + demo seed.toml and runs it.

    Layout matches the demo config: backend_dir=app, tests_dir=app/tests, source_dirs=[models, ...].
    """
    repo = tmp_path / "repo"
    (repo / "seed").mkdir(parents=True)
    (repo / "seed" / "seed.toml").write_text(_DEMO_SEED)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "check_test_coverage.py").write_text(_render_demo())
    (repo / "app" / "models").mkdir(parents=True)
    (repo / "app" / "tests").mkdir(parents=True)
    (repo / "app" / "models" / "user.py").write_text("# a source file\n")
    if not with_missing_test:
        (repo / "app" / "tests" / "test_user.py").write_text("# its test\n")
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "check_test_coverage.py")],
        capture_output=True,
        text=True,
    )


def test_rendered_checker_reports_a_missing_test(tmp_path: Path) -> None:
    """Expects the rendered checker to FAIL (exit 1) and name the source file with no test."""
    result = _run_rendered_checker(tmp_path, with_missing_test=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "user.py" in result.stdout


def test_rendered_checker_passes_when_test_present(tmp_path: Path) -> None:
    """Expects the rendered checker to PASS (exit 0) once the matching test file exists.

    Proves it reads source_dirs/backend_dir/tests_dir from seed.toml at runtime — the synthetic
    repo uses the demo layout (app/, app/tests/), not klartext's api/ layout.
    """
    result = _run_rendered_checker(tmp_path, with_missing_test=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout


def _run_with_seed(
    tmp_path: Path, *, seed_toml: str, files: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """Assembles a synthetic repo with a CUSTOM seed.toml + files, runs the rendered checker.

    `files` maps repo-relative paths to contents (parent dirs auto-created). The rendered template
    body is config-independent (only the docstring carries {{project_name}}), so the runtime config
    that drives behaviour is the repo's own seed.toml — exactly what we vary here.
    """
    repo = tmp_path / "repo"
    (repo / "seed").mkdir(parents=True)
    (repo / "seed" / "seed.toml").write_text(seed_toml)
    (repo / "scripts").mkdir()
    (repo / "scripts" / "check_test_coverage.py").write_text(_render_demo())
    for rel, content in files.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "check_test_coverage.py")],
        capture_output=True,
        text=True,
    )


def test_excluded_files_are_skipped(tmp_path: Path) -> None:
    """GREEN guard: a source file listed in excluded_files raises no missing-test failure.

    __init__.py is in the demo excluded_files; present as the ONLY source file (no test) it must
    still pass — proving the exclusion branch runs, not that the dir merely happens to be empty.
    """
    result = _run_with_seed(
        tmp_path,
        seed_toml=_DEMO_SEED,
        files={"app/models/__init__.py": "# excluded — no domain logic\n"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout


def test_test_file_overrides_resolves_non_default_name(tmp_path: Path) -> None:
    """GREEN guard: an override maps a source file to a non-default test name, satisfied by it.

    With override `widget.py=test_custom_widget.py`, the default `test_widget*.py` is absent but
    the overridden name IS present — the checker must PASS, proving the override branch (not the
    prefix fallback) resolved the match.
    """
    seed = _DEMO_SEED.replace(
        "test_file_overrides = []\n",
        'test_file_overrides = ["widget.py=test_custom_widget.py"]\n',
    )
    result = _run_with_seed(
        tmp_path,
        seed_toml=seed,
        files={
            "app/models/widget.py": "# source\n",
            "app/tests/test_custom_widget.py": "# the non-default test\n",
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout


def test_test_file_overrides_fails_when_overridden_name_absent(tmp_path: Path) -> None:
    """GREEN guard: an override that points at a missing test name FAILS naming that exact name.

    Proves the override branch does not silently accept a default-named test: only the configured
    override name counts, and its absence is reported (exit 1) with the override target in output.
    """
    seed = _DEMO_SEED.replace(
        "test_file_overrides = []\n",
        'test_file_overrides = ["widget.py=test_custom_widget.py"]\n',
    )
    result = _run_with_seed(
        tmp_path,
        seed_toml=seed,
        files={
            "app/models/widget.py": "# source\n",
            # default-named test exists, but the OVERRIDE name does not — must still fail
            "app/tests/test_widget.py": "# default name, ignored by the override\n",
        },
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "test_custom_widget.py" in result.stdout


def test_prefix_match_accepts_suffixed_test_name(tmp_path: Path) -> None:
    """GREEN guard: the default branch accepts test_<stem>*.py (a suffix beyond the bare stem).

    `user.py` is satisfied by `test_user_extra.py` — proving the glob is `test_<stem>*.py`, not an
    exact `test_<name>.py` match.
    """
    result = _run_with_seed(
        tmp_path,
        seed_toml=_DEMO_SEED,
        files={
            "app/models/user.py": "# source\n",
            "app/tests/test_user_extra.py": "# suffixed test name\n",
        },
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout


def test_missing_config_key_fails_loud(tmp_path: Path) -> None:
    """GREEN guard: a seed.toml missing a coverage key crashes (KeyError) — never silent-passes.

    Drops source_dirs from the seed. The checker reads config at runtime with config["source_dirs"];
    a missing key must raise (non-zero exit, KeyError in stderr), not skip all checks and report OK.
    """
    seed = _DEMO_SEED.replace('source_dirs       = ["models", "services"]\n', "")
    result = _run_with_seed(
        tmp_path,
        seed_toml=seed,
        files={"app/models/user.py": "# source, no test\n"},
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "KeyError" in result.stderr
    assert "source_dirs" in result.stderr
    assert "OK" not in result.stdout


def test_malformed_override_without_separator_fails_loud(tmp_path: Path) -> None:
    """GREEN guard: a test_file_overrides entry with no '=' raises, never silently passes.

    Without the separator guard, "widget.py" would partition to ("widget.py", "", "") and map the
    source to an empty test name — (tests_dir / "").exists() is True, silently marking it covered.
    The template fail-louds (ValueError) instead, consistent with the seed's fail-loud philosophy.
    """
    seed = _DEMO_SEED.replace(
        "test_file_overrides = []\n",
        'test_file_overrides = ["widget.py"]\n',  # missing '=test_x.py'
    )
    result = _run_with_seed(
        tmp_path,
        seed_toml=seed,
        files={"app/models/widget.py": "# source, no test\n"},
    )
    assert result.returncode != 0, result.stdout + result.stderr
    assert "ValueError" in result.stderr
    assert "OK" not in result.stdout
