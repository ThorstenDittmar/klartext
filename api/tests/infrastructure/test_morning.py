"""Infrastructure tests: the morning startup script (scripts/morning.sh).

morning.sh reads agents/team.yaml and opens a terminal tab for each agent
with status=terminal and active=true. In KLARTEXT_MORNING_DRY_RUN mode, it
prints what it would do instead of opening actual terminals — that mode is
used here so the tests are CI-safe.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[3] / "scripts" / "morning.sh"

_TEAM_YAML_TEMPLATE = """\
agents:
  - slug: devops
    display: "DevOps"
    status: terminal
    active: true
  - slug: hannibal
    display: "Hannibal"
    status: app
    active: true
  - slug: retired
    display: "Retired"
    status: terminal
    active: false
"""

_TEAM_YAML_ALL_APP = """\
agents:
  - slug: hannibal
    display: "Hannibal"
    status: app
    active: true
  - slug: oe
    display: "OE"
    status: app
    active: true
"""


def _write_team_yaml(repo_root: Path, content: str) -> None:
    """Writes agents/team.yaml with the given content under repo_root."""
    agents_dir = repo_root / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / "team.yaml").write_text(content)


def _run(repo_root: Path) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "KLARTEXT_REPO_ROOT": str(repo_root),
        "KLARTEXT_MORNING_DRY_RUN": "1",
    }
    return subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, env=env)


def test_morning_script_exists_and_is_executable() -> None:
    """Verifies scripts/morning.sh is present and executable."""
    assert SCRIPT.exists(), "scripts/morning.sh is missing"
    assert os.access(SCRIPT, os.X_OK), "scripts/morning.sh is not executable"


def test_morning_starts_only_terminal_active_agents(tmp_path: Path) -> None:
    """Expects morning.sh to select agents with status=terminal and active=true only."""
    _write_team_yaml(tmp_path, _TEAM_YAML_TEMPLATE)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "devops" in result.stdout, f"devops (terminal+active) missing:\n{result.stdout}"
    assert "hannibal" not in result.stdout, f"hannibal (app) should not appear:\n{result.stdout}"
    assert "retired" not in result.stdout, f"retired (inactive) should not appear:\n{result.stdout}"


def test_morning_exits_cleanly_when_no_terminal_agents(tmp_path: Path) -> None:
    """Expects morning.sh to print a message and exit 0 when no terminal agents exist."""
    _write_team_yaml(tmp_path, _TEAM_YAML_ALL_APP)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "No terminal agents" in result.stdout, (
        f"Expected 'No terminal agents' notice:\n{result.stdout}"
    )


def test_morning_fails_when_team_yaml_is_missing(tmp_path: Path) -> None:
    """Expects morning.sh to exit non-zero when team.yaml does not exist."""
    result = _run(tmp_path)

    assert result.returncode != 0, (
        f"Expected non-zero exit when team.yaml is missing, got 0."
        f"\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


_TEAM_YAML_TWO_TERMINAL = """\
agents:
  - slug: devops
    display: "DevOps"
    status: terminal
    active: true
  - slug: oe
    display: "OE"
    status: terminal
    active: true
"""

_TEAM_YAML_NO_AGENTS_KEY = """\
version: 1
settings:
  foo: bar
"""

_TEAM_YAML_MALFORMED = "this: is: [broken yaml\n"


def _run_with_stagger(repo_root: Path, stagger: str = "0") -> subprocess.CompletedProcess[str]:
    """Runs morning.sh in dry-run mode with a configurable stagger value."""
    env = {
        **os.environ,
        "KLARTEXT_REPO_ROOT": str(repo_root),
        "KLARTEXT_MORNING_DRY_RUN": "1",
        "KLARTEXT_MORNING_STAGGER": stagger,
    }
    return subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, env=env)


def test_morning_dry_run_prints_open_tab_command(tmp_path: Path) -> None:
    """Expects dry-run mode to print the exact tab-open command for each agent."""
    _write_team_yaml(tmp_path, _TEAM_YAML_TEMPLATE)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert (
        "[dry-run] would open a tab in the current window: bash agents/devops/start.sh"
        in result.stdout
    ), f"Expected dry-run line for devops agent missing from output:\n{result.stdout}"


def test_morning_stagger_notice_printed_between_agents_not_before_first(tmp_path: Path) -> None:
    """Expects stagger notice between agents but not before the first agent launch."""
    _write_team_yaml(tmp_path, _TEAM_YAML_TWO_TERMINAL)

    result = _run_with_stagger(tmp_path, stagger="0")

    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()

    # The stagger notice must appear somewhere in output (two agents → one gap).
    is_stagger = lambda ln: "Waiting" in ln and "contention" in ln  # noqa: E731
    stagger_lines = [ln for ln in lines if is_stagger(ln)]
    assert len(stagger_lines) == 1, (
        f"Expected exactly 1 stagger notice for 2 agents, got {len(stagger_lines)}"
        f":\n{result.stdout}"
    )

    # The stagger notice must come AFTER the first agent line, not before it.
    first_agent_idx = next(i for i, ln in enumerate(lines) if "devops" in ln)
    stagger_idx = next(i for i, ln in enumerate(lines) if is_stagger(ln))
    assert stagger_idx > first_agent_idx, (
        f"Stagger notice appeared before first agent "
        f"(line {stagger_idx} vs first-agent line {first_agent_idx}):\n{result.stdout}"
    )


def test_morning_exits_cleanly_when_team_yaml_has_no_agents_key(tmp_path: Path) -> None:
    """Expects morning.sh to exit 0 with a notice when team.yaml contains no 'agents' key."""
    _write_team_yaml(tmp_path, _TEAM_YAML_NO_AGENTS_KEY)

    result = _run(tmp_path)

    assert result.returncode == 0, (
        f"Expected exit 0 for team.yaml without 'agents' key:"
        f"\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "No terminal agents" in result.stdout, (
        f"Expected 'No terminal agents' notice for team.yaml without 'agents' key:\n{result.stdout}"
    )


def test_morning_fails_when_team_yaml_is_malformed(tmp_path: Path) -> None:
    """Expects morning.sh to exit non-zero when team.yaml is not valid YAML.

    A parse failure must not silently produce 'No terminal agents' and exit 0 —
    that would mask a broken config and leave agents un-started with no visible error.
    """
    _write_team_yaml(tmp_path, _TEAM_YAML_MALFORMED)

    result = _run(tmp_path)

    assert result.returncode != 0, (
        f"Expected non-zero exit for malformed team.yaml, got 0.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
