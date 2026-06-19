"""Infrastructure tests: the seed .pre-commit-config template (export plan §7.3).

The seed ships the GENERIC WoW pre-commit hooks — the ADR-0014 agent-provenance trailer and the
semgrep architectural-rule scan — plus a documented slot where an importer drops its stack-specific
linters (ruff/mypy/tach/eslint/… are klartext's product stack and do NOT ship). The agent-trailer
hook invokes the portable interpreter via the phase-2 shim (`bin/seed-python`), so the interpreter
is a one-line seed.toml change rather than a hardcoded venv path.
"""

from __future__ import annotations

from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).parents[3]
_TEMPLATE = _REPO_ROOT / "seed" / "templates" / "pre-commit-config.yaml.tmpl"


def _hook_ids(config: dict) -> set[str]:
    """Returns every hook id across all repos in a parsed pre-commit config."""
    ids: set[str] = set()
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            ids.add(hook["id"])
    return ids


def _hook_entry(config: dict, hook_id: str) -> str:
    """Returns the `entry` of the hook with the given id."""
    for repo in config["repos"]:
        for hook in repo["hooks"]:
            if hook["id"] == hook_id:
                return hook.get("entry", "")
    raise AssertionError(f"hook {hook_id} not found")


def test_precommit_template_exists() -> None:
    """Expects the pre-commit template to be a committed seed artefact."""
    assert _TEMPLATE.is_file(), f"missing pre-commit template: {_TEMPLATE}"


def test_precommit_template_is_valid_yaml() -> None:
    """Expects the template to parse as YAML (it ships as-is; no required placeholder)."""
    yaml.safe_load(_TEMPLATE.read_text())


def test_precommit_ships_agent_trailer_as_the_active_generic_hook() -> None:
    """Expects agent-trailer (fully generic, no project config) to be an active hook."""
    ids = _hook_ids(yaml.safe_load(_TEMPLATE.read_text()))
    assert "agent-trailer" in ids


def test_precommit_does_not_ship_semgrep_as_an_active_hook_but_recommends_it() -> None:
    """Expects semgrep NOT to be an active hook — its rules + file-filter are consumer-specific.

    SA §185 review: an active semgrep hook bakes a Python-stack assumption (types_or) and points at
    a non-shipping `.semgrep/rules/` dir. Per the Standards-Charter cut (mechanism generic, rules =
    consumer's own), semgrep moves into the documented slot as a recommendation, not an active hook.
    """
    text = _TEMPLATE.read_text()
    assert "semgrep" not in _hook_ids(yaml.safe_load(text)), "semgrep must not be an active hook"
    assert "semgrep" in text, "semgrep should still be recommended in the slot comment"


def test_precommit_does_not_ship_product_stack_linters() -> None:
    """Expects klartext's product-stack linters to be absent — they belong in the slot."""
    ids = _hook_ids(yaml.safe_load(_TEMPLATE.read_text()))
    assert {"ruff", "ruff-format", "mypy", "tach-check", "eslint", "tsc"} & ids == set()


def test_agent_trailer_hook_runs_via_the_interpreter_shim() -> None:
    """Expects the agent-trailer hook to invoke scripts/agent_trailer.py via the bin/ shim.

    Routing through the phase-2 shim (not a hardcoded venv path) is what makes the interpreter a
    one-line seed.toml change for an importer.
    """
    entry = _hook_entry(yaml.safe_load(_TEMPLATE.read_text()), "agent-trailer")
    assert "bin/seed-python" in entry
    assert "scripts/agent_trailer.py" in entry


def test_precommit_installs_commit_msg_stage() -> None:
    """Expects the commit-msg stage to be installed (the agent trailer runs there)."""
    config = yaml.safe_load(_TEMPLATE.read_text())
    assert "commit-msg" in config["default_install_hook_types"]
