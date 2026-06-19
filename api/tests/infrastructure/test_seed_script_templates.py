"""Infrastructure tests: the seed script templates (export plan §7.3 artefact templating).

The seed ships the WoW machinery scripts as templates; an importer renders them from seed.toml.
These six carry only SCALAR klartext literals (project_name, env_prefix, memory_dir, worktree_base,
identity_preamble, wow_cli_command), so `{{key}}` substitution suffices (check_test_coverage.py,
which needs list/map config, is a separate increment).

The completeness gate, rendered against a DEMO seed.toml (NOT klartext's own — klartext's
project_name IS "klartext", which would mask un-parametrized literals):
  * no "klartext" literal survives — every endeavour-specific string came from seed.toml;
  * no "{{...}}" placeholder is left unsubstituted (a silent bug the importer would inherit);
  * the rendered artefact is syntactically valid (bash -n for .sh, py_compile for .py).

EN-first (plan §6 decision 1): the seed templates render user-facing strings in English, so they
intentionally differ from klartext's live DE strings — hence a demo-render completeness gate rather
than a live-reproduction dogfood.
"""

from __future__ import annotations

import ast
import importlib.util
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[3]
_TEMPLATES_DIR = _REPO_ROOT / "seed" / "templates"

# template filename → rendered target basename (for syntax-check dispatch by extension)
_SCRIPT_TEMPLATES: dict[str, str] = {
    "inbox.sh.tmpl": "inbox.sh",
    "start-agent.sh.tmpl": "start-agent.sh",
    "check-compact-log.sh.tmpl": "check-compact-log.sh",
    "load_agent_identity.py.tmpl": "load_agent_identity.py",
    "session_health.py.tmpl": "session_health.py",
    "substrate_backup.py.tmpl": "substrate_backup.py",
}


def _load_render():
    """Loads seed/render.py as a module (standalone tool, not a package)."""
    spec = importlib.util.spec_from_file_location("seed_render", _REPO_ROOT / "seed" / "render.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_render = _load_render()

# A complete demo seed.toml whose values share NO substring with "klartext", so a surviving
# "klartext" in a rendered template can only be an un-parametrized literal.
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
)


def _render_with_demo(template_name: str, tmp_path: Path) -> str:
    """Renders a seed template with the demo seed.toml."""
    seed = tmp_path / "seed.toml"
    seed.write_text(_DEMO_SEED)
    config = _render.load_seed_config(seed)
    return _render.render((_TEMPLATES_DIR / template_name).read_text(), config)


def test_all_six_script_templates_exist() -> None:
    """Expects every WoW-machinery script template to be a committed seed artefact."""
    for name in _SCRIPT_TEMPLATES:
        assert (_TEMPLATES_DIR / name).is_file(), f"missing script template: {name}"


def test_no_klartext_literal_survives_rendering(tmp_path: Path) -> None:
    """Expects rendering with a non-klartext seed.toml to leave no 'klartext' literal behind."""
    for name in _SCRIPT_TEMPLATES:
        rendered = _render_with_demo(name, tmp_path)
        assert "klartext" not in rendered.lower(), f"un-parametrized klartext literal in {name}"


def test_no_placeholder_left_unsubstituted(tmp_path: Path) -> None:
    """Expects no '{{...}}' placeholder to survive — a leftover one is a silent bug."""
    for name in _SCRIPT_TEMPLATES:
        rendered = _render_with_demo(name, tmp_path)
        assert "{{" not in rendered and "}}" not in rendered, f"unsubstituted placeholder in {name}"


def test_rendered_shell_templates_are_valid_bash(tmp_path: Path) -> None:
    """Expects each rendered .sh template to pass `bash -n` (syntax-valid after substitution)."""
    for name, target in _SCRIPT_TEMPLATES.items():
        if not target.endswith(".sh"):
            continue
        rendered = _render_with_demo(name, tmp_path)
        result = subprocess.run(
            ["bash", "-n", "/dev/stdin"], input=rendered, text=True, capture_output=True
        )
        assert result.returncode == 0, f"{name} renders invalid bash: {result.stderr}"


def test_rendered_python_templates_compile(tmp_path: Path) -> None:
    """Expects each rendered .py template to byte-compile (syntax-valid after substitution)."""
    for name, target in _SCRIPT_TEMPLATES.items():
        if not target.endswith(".py"):
            continue
        rendered = _render_with_demo(name, tmp_path)
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
            handle.write(rendered)
            path = handle.name
        py_compile.compile(path, doraise=True)


def test_wow_cli_command_is_substituted_in_converge_callers(tmp_path: Path) -> None:
    """Expects the converge-calling templates to render the consumer's wow_cli_command.

    inbox.sh and session_health.py both reference the WoW converge invocation; after rendering with
    the demo config they must say 'demo converge', proving Wrinkle A's key reached both call sites.
    """
    for name in ("inbox.sh.tmpl", "session_health.py.tmpl"):
        rendered = _render_with_demo(name, tmp_path)
        assert "demo converge" in rendered, f"wow_cli_command not substituted into {name}"


def test_load_agent_identity_format_slug_works(tmp_path: Path) -> None:
    """Expects the rendered _PREAMBLE to carry exactly one valid `{slug}` field for `.format()`.

    `{{identity_preamble}}` is render-time (double-brace); `{slug}` is runtime (single-brace, kept
    for `.format(slug=...)`). py_compile only proves syntax — it would NOT catch a stray single `{`
    or `}` in the preamble that makes `.format()` raise KeyError/ValueError at hook time. This
    exec()s the rendered module and calls `.format(slug=...)`, the path the SessionStart hook runs.
    """
    rendered = _render_with_demo("load_agent_identity.py.tmpl", tmp_path)
    namespace: dict[str, object] = {}
    # Neutralise the __main__ guard so exec does not run sys.exit / git / file IO.
    exec(rendered.replace("if __name__", "if False and __name__"), namespace)
    preamble = namespace["_PREAMBLE"]
    assert isinstance(preamble, str)
    formatted = preamble.format(slug="ux")  # raises if a stray brace broke the format string
    assert "ux" in formatted, "the rendered {slug} field did not substitute"


class _LogicCanonicaliser(ast.NodeTransformer):
    """Normalises an AST to its logic skeleton: drops docstrings, flattens str constants to 'S'.

    The seed templates diverge from the live scripts ONLY in docstrings (war-story strip) and
    user-facing string literals (EN translation). Erasing both leaves the executable structure —
    every statement, call, condition, def — so an equal dump proves the parametrisation changed
    strings/comments only, never logic (a dropped `if`, a flipped operator, a removed function).
    """

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:  # noqa: N802
        """Collapses every string constant to a single sentinel so EN translation is invisible."""
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(value="S"), node)
        return node

    def _strip_docstring(self, node: ast.AST) -> ast.AST:
        self.generic_visit(node)
        body = getattr(node, "body", None)
        if not body:
            return node
        first = body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            node.body = body[1:]  # type: ignore[attr-defined]
        return node

    # ast.NodeVisitor dispatches on these exact CamelCase names — N815 cannot apply here.
    visit_Module = _strip_docstring  # type: ignore[assignment]  # noqa: N815
    visit_FunctionDef = _strip_docstring  # type: ignore[assignment]  # noqa: N815
    visit_AsyncFunctionDef = _strip_docstring  # type: ignore[assignment]  # noqa: N815
    visit_ClassDef = _strip_docstring  # type: ignore[assignment]  # noqa: N815


def _logic_skeleton(source: str) -> str:
    """Returns the docstring-stripped, string-erased AST dump of Python source."""
    tree = _LogicCanonicaliser().visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    return ast.dump(tree)


def _render_with_klartext(template_name: str) -> str:
    """Renders a seed template with klartext's OWN seed.toml (the worked example in the repo)."""
    config = _render.load_seed_config(_REPO_ROOT / "seed" / "seed.toml")
    return _render.render((_TEMPLATES_DIR / template_name).read_text(), config)


_PYTHON_TEMPLATE_TO_LIVE: dict[str, str] = {
    "load_agent_identity.py.tmpl": "load_agent_identity.py",
    "session_health.py.tmpl": "session_health.py",
    "substrate_backup.py.tmpl": "substrate_backup.py",
}


def test_python_templates_preserve_live_script_logic() -> None:
    """Expects each .py template, rendered with klartext's seed, to match the live script's logic.

    A textual dogfood is impossible here (EN translation + war-story strip make render != live),
    but the LOGIC must be untouched. This compares logic skeletons (docstrings dropped, string
    literals erased): a green run means the only divergence is strings/comments — an accidental
    structural change (deleted statement, altered condition) would break it. Fidelity guard.
    """
    for template, live in _PYTHON_TEMPLATE_TO_LIVE.items():
        rendered = _render_with_klartext(template)
        live_source = (_REPO_ROOT / "scripts" / live).read_text()
        assert _logic_skeleton(rendered) == _logic_skeleton(live_source), (
            f"{template} diverges from scripts/{live} in LOGIC, not just strings/docstrings"
        )
