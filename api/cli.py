"""klartext CLI — infrastructure commands for local development.

Usage (after pip install -e .):
  klartext start              Start the API server (dev mode with auto-reload)
  klartext frontend           Start the Vite frontend dev server
  klartext dev                Start the full dev stack (Supabase + API + Frontend)
  klartext demo               Clean environment: reset DB, seed data, start all services
  klartext test               Run the unit test suite
  klartext test --all         Run unit tests + integration tests
  klartext health             Call the /health endpoint and print results
  klartext testdata           Seed the database with a consistent test dataset
  klartext flush              Delete all data rows without restarting anything
  klartext db start           Start the local Supabase instance
  klartext db reset           Reset the local Supabase database (re-applies migrations)
  klartext db status          Show the status of the local Supabase instance
  klartext skills sync        Install repo skills into ~/.claude/skills/ (repo is the SoT)
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx
import typer

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="klartext",
    help="Infrastructure commands for the klartext.jetzt API.",
    no_args_is_help=True,
)

db_app = typer.Typer(help="Database commands (Supabase).")
app.add_typer(db_app, name="db")

skills_app = typer.Typer(help="Skill distribution (repo → ~/.claude/skills/).")
app.add_typer(skills_app, name="skills")

_PROJECT_ROOT = Path(__file__).parent.parent
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"
_SKILLS_SOURCE = _PROJECT_ROOT / "docs" / "superpowers" / "skills"
_SKILLS_TARGET = Path.home() / ".claude" / "skills"
_REPO_MANAGED_MARKER = ".repo-managed"


# ---------------------------------------------------------------------------
# Private helpers — shared building blocks used by multiple commands
# ---------------------------------------------------------------------------


def _supabase_start() -> None:
    """Starts the local Supabase instance."""
    typer.echo("Starting Supabase…")
    subprocess.run(["supabase", "start"], cwd=str(_PROJECT_ROOT), check=True)


def _supabase_project_id() -> str:
    """Reads the project_id from supabase/config.toml."""
    config_path = _PROJECT_ROOT / "supabase" / "config.toml"
    match = re.search(r'project_id\s*=\s*"([^"]+)"', config_path.read_text())
    return match.group(1) if match else "klartext"


def _record_migrations(db_container: str, migrations_dir: Path) -> None:
    """Creates the supabase_migrations tracking schema and marks all migrations as applied.

    Without this table, supabase start tries to re-apply all migrations on the
    next run and fails because the tables already exist.
    """
    migration_files = sorted(migrations_dir.glob("*.sql"))
    values = ", ".join(f"('{f.stem[:14]}', '{f.stem[15:]}')" for f in migration_files)
    sql = f"""
CREATE SCHEMA IF NOT EXISTS supabase_migrations;
CREATE TABLE IF NOT EXISTS supabase_migrations.schema_migrations (
    version text NOT NULL,
    statements text[],
    name text
);
INSERT INTO supabase_migrations.schema_migrations (version, name) VALUES {values}
ON CONFLICT DO NOTHING;
""".encode()
    subprocess.run(
        ["docker", "exec", "-i", db_container, "psql", "-U", "postgres", "-d", "postgres"],
        input=sql,
        check=True,
    )


def _db_reset() -> None:
    """Resets the local Supabase database and re-applies all migrations.

    The Supabase CLI migration runner has a known issue on macOS where it
    incorrectly reports 'relation users already exists' due to auth.users
    being present in the search_path. This command works around it by
    applying migrations directly via the postgres container, then registering
    them in the tracking table so the CLI does not re-apply them on next start.
    """
    project_id = _supabase_project_id()
    db_container = f"supabase_db_{project_id}"
    migrations_dir = _PROJECT_ROOT / "supabase" / "migrations"

    # Stop and remove old data — ignore errors if nothing is running
    typer.echo("Stopping Supabase and removing old data…")
    subprocess.run(["supabase", "stop", "--no-backup"], cwd=str(_PROJECT_ROOT))

    # supabase start initialises the DB container but fails at the migration step.
    # The DB container stays running after the failure — that is expected and required.
    typer.echo("Initialising fresh database (migration errors here are expected)…")
    subprocess.run(["supabase", "start"], cwd=str(_PROJECT_ROOT))

    # Wait for the DB container to be healthy before applying migrations
    typer.echo("Waiting for database container…")
    for _ in range(30):
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", db_container],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() == "healthy":
            break
        time.sleep(1)
    else:
        typer.secho("✗  Database container did not become healthy.", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Apply all migrations directly via psql inside the container
    typer.echo("Applying migrations…")
    for migration_file in sorted(migrations_dir.glob("*.sql")):
        typer.echo(f"  → {migration_file.name}")
        subprocess.run(
            ["docker", "exec", "-i", db_container, "psql", "-U", "postgres", "-d", "postgres"],
            input=migration_file.read_bytes(),
            check=True,
        )

    # Register all migrations so supabase start won't try to re-apply them
    _record_migrations(db_container, migrations_dir)

    # Full stop (backs up DB to Docker volume) then start (restores + starts all services)
    typer.echo("Starting full Supabase stack…")
    subprocess.run(["supabase", "stop"], cwd=str(_PROJECT_ROOT), check=True)
    subprocess.run(["supabase", "start"], cwd=str(_PROJECT_ROOT), check=True)
    typer.secho("✓  Database reset complete.", fg=typer.colors.GREEN)


def _api_process(
    host: str = "127.0.0.1", port: int = 8000, reload: bool = True
) -> subprocess.Popen[bytes]:
    """Starts the FastAPI server as a background process and returns the handle."""
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        cmd.append("--reload")
    typer.echo(f"Starting klartext API on http://{host}:{port}")
    return subprocess.Popen(cmd)


def _frontend_process() -> subprocess.Popen[bytes]:
    """Starts the Vite dev server as a background process and returns the handle."""
    typer.echo("Starting frontend (Vite) on http://127.0.0.1:5173")
    return subprocess.Popen(["npm", "run", "dev"], cwd=str(_FRONTEND_DIR))


def _wait_for_api(url: str, timeout: int = 30) -> bool:
    """Polls /health until the API is ready or the timeout (seconds) is reached."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if httpx.get(f"{url}/health", timeout=2).status_code == 200:
                return True
        except httpx.ConnectError:
            pass
        time.sleep(1)
    return False


async def _seed(url: str) -> None:
    """Seeds the database with the predefined test dataset via the running API."""
    from api.seeddata import FIXTURE_PATH, SEED_ACTORS, SEED_CAUSAL_MODEL, SEED_CLAIMS

    async with httpx.AsyncClient(base_url=url, timeout=30) as client:
        # 1. Import narrative
        typer.echo("  → Importing Klartext narrative…")
        response = await client.post("/narratives/import", json={"path": str(FIXTURE_PATH)})
        if response.status_code != 201:
            typer.secho(
                f"  ✗  Import failed: {response.status_code} {response.text}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

        narrative = response.json()
        narrative_id = narrative["id"]
        scenes = narrative["scenes"]
        typer.secho(
            f"  ✓  Narrative created: {narrative['title']} "
            f"({len(scenes)} scenes, id={narrative_id})",
            fg=typer.colors.GREEN,
        )

        # 2. Extract claims for seeded scenes
        for seed in SEED_CLAIMS:
            if seed.scene_index >= len(scenes):
                break
            scene = scenes[seed.scene_index]
            scene_id = scene["id"]
            extract_response = await client.post(
                f"/narratives/{narrative_id}/scenes/{scene_id}/extract-claims"
            )
            if extract_response.status_code == 201:
                count = len(extract_response.json().get("claims", []))
                typer.secho(
                    f"  ✓  Scene '{scene['title']}': {count} claims extracted",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"  ⚠  Scene '{scene['title']}': extraction failed "
                    f"({extract_response.status_code})",
                    fg=typer.colors.YELLOW,
                )

        # 3. Create causal model
        typer.echo("  → Creating causal model…")
        model_response = await client.post(
            "/causal-models",
            json={"title": SEED_CAUSAL_MODEL.title},
        )
        if model_response.status_code != 201:
            typer.secho(
                f"  ✗  Causal model creation failed: "
                f"{model_response.status_code} {model_response.text}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

        model = model_response.json()
        model_id = model["id"]
        typer.secho(
            f"  ✓  Causal model created: {model['title']} (id={model_id})",
            fg=typer.colors.GREEN,
        )

        # 4. Add axioms to causal model
        for axiom in SEED_CAUSAL_MODEL.axioms:
            axiom_response = await client.post(
                f"/causal-models/{model_id}/axioms",
                json={"label": axiom.label, "description": axiom.description},
            )
            if axiom_response.status_code == 201:
                typer.secho(
                    f"  ✓  Axiom added: {axiom.label}",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"  ⚠  Axiom '{axiom.label}' failed ({axiom_response.status_code})",
                    fg=typer.colors.YELLOW,
                )

        # 5. Add actors to narrative
        typer.echo("  → Adding actors to narrative…")
        for actor in SEED_ACTORS:
            actor_response = await client.post(
                f"/narratives/{narrative_id}/actors",
                json={"label": actor.label, "actor_type": actor.actor_type, "notes": actor.notes},
            )
            if actor_response.status_code == 201:
                typer.secho(
                    f"  ✓  Actor added: {actor.label} ({actor.actor_type})",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"  ⚠  Actor '{actor.label}' failed ({actor_response.status_code})",
                    fg=typer.colors.YELLOW,
                )

        # 6. Link narrative to causal model
        typer.echo("  → Linking narrative to causal model…")
        link_response = await client.put(
            f"/narratives/{narrative_id}/causal-model",
            json={"causal_model_id": model_id},
        )
        if link_response.status_code == 200:
            typer.secho(
                f"  ✓  Narrative linked to causal model (id={model_id})",
                fg=typer.colors.GREEN,
            )
        else:
            typer.secho(
                f"  ⚠  Linking failed ({link_response.status_code})",
                fg=typer.colors.YELLOW,
            )


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def start(
    host: str = typer.Option("127.0.0.1", help="Bind address"),
    port: int = typer.Option(8000, help="Port"),
    reload: bool = typer.Option(True, help="Enable auto-reload (dev mode)"),
) -> None:
    """Start the FastAPI development server."""
    _api_process(host, port, reload).wait()


@app.command()
def frontend() -> None:
    """Start the Vite frontend dev server."""
    _frontend_process().wait()


@app.command()
def dev() -> None:
    """Start the full development stack: Supabase + API + Frontend.

    Does not reset the database or re-seed data.
    Use 'klartext demo' for a clean environment with fresh test data.
    """
    _supabase_start()
    api_proc = _api_process()
    frontend_proc = _frontend_process()
    try:
        api_proc.wait()
    except KeyboardInterrupt:
        typer.echo("\nShutting down…")
    finally:
        api_proc.terminate()
        frontend_proc.terminate()


@app.command()
def demo(
    url: str = typer.Option("http://127.0.0.1:8000", help="Base URL of the API"),
) -> None:
    """Start a clean demo environment with fresh test data.

    Starts Supabase, resets the database, seeds test data, then launches
    the API and frontend. Press Ctrl+C to stop all services.
    """
    # 1. Start Supabase
    _supabase_start()

    # 2. Reset database to a clean state
    _db_reset()

    # 3. Start API in the background
    api_proc = _api_process()

    # 4. Wait until API is responsive before seeding
    typer.echo("Waiting for API to become ready…")
    if not _wait_for_api(url):
        typer.secho("✗  API did not become ready in time.", fg=typer.colors.RED)
        api_proc.terminate()
        raise typer.Exit(1)
    typer.secho("✓  API is ready.", fg=typer.colors.GREEN)

    # 5. Seed test data
    typer.echo("\nSeeding test data…")
    asyncio.run(_seed(url))

    # 6. Start frontend
    frontend_proc = _frontend_process()

    typer.echo()
    typer.secho("✓  Demo environment is ready.", fg=typer.colors.GREEN, bold=True)
    typer.echo("   API:      http://127.0.0.1:8000/docs")
    typer.echo("   Frontend: http://127.0.0.1:5173")
    typer.echo("\nPress Ctrl+C to stop all services.\n")

    try:
        api_proc.wait()
    except KeyboardInterrupt:
        typer.echo("\nShutting down…")
    finally:
        api_proc.terminate()
        frontend_proc.terminate()


@app.command()
def test(
    all_tests: bool = typer.Option(False, "--all", help="Run unit + integration tests"),
    integration: bool = typer.Option(False, "--integration", help="Run integration tests only"),
    verbose: bool = typer.Option(False, "-v", help="Verbose output"),
    path: str = typer.Option("tests/", help="Test path or file"),
) -> None:
    """Run the test suite.

    Default: unit tests only.
    --integration: integration tests only (requires a running Supabase instance).
    --all: unit tests + integration tests.
    """
    if all_tests and integration:
        typer.secho("✗  --all and --integration are mutually exclusive.", fg=typer.colors.RED)
        raise typer.Exit(1)

    cmd = [sys.executable, "-m", "pytest", path]

    if all_tests:
        cmd += ["-m", ""]
        typer.echo("Running all tests (unit + integration)…")
    elif integration:
        cmd += ["-m", "integration"]
        typer.echo("Running integration tests…")
    else:
        typer.echo("Running unit tests…")

    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd, cwd=str(_PROJECT_ROOT / "api"))
    raise typer.Exit(result.returncode)


@app.command()
def health(
    url: str = typer.Option("http://127.0.0.1:8000", help="Base URL of the API"),
) -> None:
    """Call the /health endpoint and print a structured report."""
    endpoint = f"{url}/health"
    typer.echo(f"Checking {endpoint} …\n")

    try:
        response = httpx.get(endpoint, timeout=5)
        data = response.json()
    except httpx.ConnectError:
        typer.secho("✗  API not reachable — is the server running?", fg=typer.colors.RED)
        raise typer.Exit(1)

    status = data.get("status", "unknown")
    version = data.get("version", "?")
    color = typer.colors.GREEN if status == "ok" else typer.colors.YELLOW

    typer.secho(f"Status:  {status}", fg=color, bold=True)
    typer.echo(f"Version: {version}\n")
    typer.echo("Checks:")

    for name, result in data.get("checks", {}).items():
        check_status = result.get("status", "unknown")
        icon = "✓" if check_status == "ok" else "✗"
        check_color = typer.colors.GREEN if check_status == "ok" else typer.colors.RED
        line = f"  {icon}  {name}: {check_status}"
        if "detail" in result:
            line += f" — {result['detail']}"
        typer.secho(line, fg=check_color)

    if status != "ok":
        raise typer.Exit(1)


@app.command()
def testdata(
    url: str = typer.Option("http://127.0.0.1:8000", help="Base URL of the running API"),
) -> None:
    """Seed the database with a consistent test dataset.

    Requires the API server to be running: klartext start
    """
    typer.echo("Seeding test data via API…\n")

    try:
        httpx.get(f"{url}/health", timeout=3).raise_for_status()
    except Exception:
        typer.secho("✗  API not reachable — run: klartext start", fg=typer.colors.RED)
        raise typer.Exit(1)

    asyncio.run(_seed(url))
    typer.echo()
    typer.secho("Done. System is seeded with test data.", fg=typer.colors.GREEN, bold=True)


# ---------------------------------------------------------------------------
# flush
# ---------------------------------------------------------------------------

_FLUSH_SQL = """
TRUNCATE TABLE
    causal_relations,
    slots,
    model_elements,
    causal_models,
    claims,
    narrative_actors,
    narrative_units,
    narrative
RESTART IDENTITY CASCADE;
""".strip()


@app.command()
def flush(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete all data rows without restarting the API or Supabase.

    Truncates all application tables and resets their ID sequences.
    The running API server keeps working — the DB is just empty afterwards.
    """
    if not yes:
        typer.confirm("Delete all data? This cannot be undone.", abort=True)

    project_id = _supabase_project_id()
    db_container = f"supabase_db_{project_id}"

    result = subprocess.run(
        ["docker", "exec", "-i", db_container, "psql", "-U", "postgres", "-d", "postgres"],
        input=_FLUSH_SQL.encode(),
        capture_output=True,
    )

    if result.returncode != 0:
        typer.secho(f"✗  Flush failed:\n{result.stderr.decode()}", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.secho("✓  All tables flushed. Database is empty.", fg=typer.colors.GREEN)


# ---------------------------------------------------------------------------
# merge — verified PR-merge wrapper (DELETE-404 retro action item)
# ---------------------------------------------------------------------------

_ALLOWED_MERGE_METHODS = ("squash", "merge")


def _validate_merge_method(method: str) -> str:
    """Returns the method if allowed. Rejects rebase — it rewrites SHAs and breaks stacks."""
    normalized = method.lower()
    if normalized in _ALLOWED_MERGE_METHODS:
        return normalized
    if normalized == "rebase":
        raise typer.BadParameter(
            "rebase rewrites commit SHAs and breaks stacked PRs — use 'squash' or 'merge'"
        )
    raise typer.BadParameter(f"unknown merge method '{method}' — use 'squash' or 'merge'")


def _evaluate_checks(checks: list[dict[str, Any]]) -> str:
    """Collapses a list of gh check buckets into one verdict: pass | fail | pending.

    fail/cancel anywhere → fail. Then only explicitly satisfied buckets count as done:
    a bucket that is neither 'pass' nor 'skipping' (including 'pending', an unknown
    value, or a missing bucket) blocks as 'pending'. This is deliberately conservative —
    a gatekeeper must never let an unrecognized status slip through to a merge. An empty
    check list is non-blocking (pass).
    """
    buckets = [c.get("bucket") for c in checks]
    if any(b in ("fail", "cancel") for b in buckets):
        return "fail"
    if any(b not in ("pass", "skipping") for b in buckets):
        return "pending"
    return "pass"


def _evaluate_preconditions(pr: dict[str, Any]) -> tuple[bool, str]:
    """Decides whether a PR's state permits merging. Returns (ok, reason).

    Hard-fails only on a non-OPEN state or a conflicting/dirty merge state. Transient
    states (UNKNOWN/UNSTABLE/BEHIND) proceed — CI status is the check-poll step's job.
    """
    state = pr.get("state")
    if state != "OPEN":
        return False, f"PR is {state}, not OPEN"
    if pr.get("mergeable") == "CONFLICTING" or pr.get("mergeStateStatus") == "DIRTY":
        return False, "PR has merge conflicts (resolve them before merging)"
    return True, ""


def _gh_json(args: list[str]) -> Any:
    """Runs a gh command expected to emit JSON on success and returns the parsed result."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        typer.secho(f"✗  gh {' '.join(args)} failed:\n{result.stderr}", fg=typer.colors.RED)
        raise typer.Exit(1)
    return json.loads(result.stdout)


def _fetch_check_buckets(pr: int) -> list[dict[str, Any]]:
    """Returns the check buckets for a PR.

    `gh pr checks` exits non-zero while checks are pending or failing, so the exit
    code is ignored — the JSON output is the source of truth. No checks configured →
    empty stdout → treated as no checks (non-blocking).
    """
    result = subprocess.run(
        ["gh", "pr", "checks", str(pr), "--json", "name,bucket"],
        capture_output=True,
        text=True,
    )
    out = result.stdout.strip()
    if not out:
        return []
    buckets: list[dict[str, Any]] = json.loads(out)
    return buckets


def _repo_slug() -> str:
    """Returns the owner/repo slug for the current repository via gh."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.secho(f"✗  could not resolve repository:\n{result.stderr}", fg=typer.colors.RED)
        raise typer.Exit(1)
    return result.stdout.strip()


@app.command()
def merge(
    pr: int = typer.Argument(..., help="PR number to merge"),
    method: str = typer.Option("squash", "--method", "-m", help="squash (default) or merge"),
    keep_branch: bool = typer.Option(
        False, "--keep-branch", help="Do not delete the branch after merge"
    ),
    timeout: int = typer.Option(900, "--timeout", help="Max seconds to wait for checks"),
) -> None:
    """Merge a PR the verified way: checks green → API-merge → delete branch → verify.

    Uses the GitHub API to merge — not `gh pr merge`, which fails when main is checked
    out in a worktree. rebase is intentionally unavailable (it rewrites SHAs and breaks
    stacks). Squash is the default; use --method merge for SHA-preserving stacks.
    """
    method = _validate_merge_method(method)

    # 1. Preconditions — refuse closed/conflicting PRs before doing anything.
    pr_info = _gh_json(
        ["pr", "view", str(pr), "--json", "state,mergeable,mergeStateStatus,headRefName"]
    )
    ok, reason = _evaluate_preconditions(pr_info)
    if not ok:
        typer.secho(f"✗  Cannot merge PR #{pr}: {reason}", fg=typer.colors.RED)
        raise typer.Exit(1)

    # 2. Poll required checks — never merge a red PR; abort on failure or timeout.
    typer.echo(f"Waiting for checks on PR #{pr} (timeout {timeout}s)…")
    deadline = time.monotonic() + timeout
    while True:
        verdict = _evaluate_checks(_fetch_check_buckets(pr))
        if verdict == "pass":
            typer.secho("✓  All checks passed.", fg=typer.colors.GREEN)
            break
        if verdict == "fail":
            typer.secho(f"✗  A check failed on PR #{pr} — not merging.", fg=typer.colors.RED)
            raise typer.Exit(1)
        if time.monotonic() >= deadline:
            typer.secho(f"✗  Timed out after {timeout}s waiting for checks.", fg=typer.colors.RED)
            raise typer.Exit(1)
        time.sleep(15)

    # 3. Merge via the GitHub API (not `gh pr merge` — worktree-safe).
    repo = _repo_slug()
    typer.echo(f"Merging PR #{pr} into main via {method}…")
    merge_path = f"repos/{repo}/pulls/{pr}/merge"
    result = subprocess.run(
        ["gh", "api", merge_path, "-X", "PUT", "-f", f"merge_method={method}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.secho(f"✗  Merge failed:\n{result.stderr}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"✓  PR #{pr} merged ({method}).", fg=typer.colors.GREEN)

    # 4. Delete the branch (short-lived by Merge Protocol rule 6) unless asked to keep it.
    head = pr_info.get("headRefName")
    if keep_branch:
        typer.echo(f"Keeping branch {head} (--keep-branch).")
    elif head:
        del_result = subprocess.run(
            ["gh", "api", f"repos/{repo}/git/refs/heads/{head}", "-X", "DELETE"],
            capture_output=True,
            text=True,
        )
        if del_result.returncode == 0:
            typer.secho(f"✓  Branch {head} deleted.", fg=typer.colors.GREEN)
        else:
            typer.secho(
                f"⚠  Branch {head} not deleted: {del_result.stderr.strip()}",
                fg=typer.colors.YELLOW,
            )

    # 5. Verify against artifacts — show main after the merge (Merge Protocol rule 4).
    subprocess.run(["git", "-C", str(_PROJECT_ROOT), "fetch", "origin", "--quiet"])
    typer.echo("\nmain after merge:")
    subprocess.run(["git", "-C", str(_PROJECT_ROOT), "log", "--oneline", "-5", "origin/main"])


# ---------------------------------------------------------------------------
# converge — guarded voluntary worktree convergence (ADR-0012)
# ---------------------------------------------------------------------------


class ConvergeAction(StrEnum):
    """Outcome of evaluating whether/how a worktree should converge to origin/main."""

    SYNC = "sync"
    ALREADY_CURRENT = "already_current"
    SKIP_DIRTY = "skip_dirty"
    SKIP_NOT_HOME_BRANCH = "skip_not_home_branch"
    SKIP_CONFLICT = "skip_conflict"
    SKIP_FETCH_FAILED = "skip_fetch_failed"
    SKIP_UNAVAILABLE = "skip_unavailable"


_HOME_BRANCH_RE = re.compile(r"^agent/[^/]+$")


def _is_home_branch(branch: str) -> bool:
    """True for an `agent/<slug>` home branch — the only branch converge rebases (ADR-0012 §B)."""
    return bool(_HOME_BRANCH_RE.match(branch))


def _is_worktree_clean(porcelain: str) -> bool:
    """True if `git status --porcelain` shows no WIP, ignoring the untracked `api/.venv` symlink.

    Every worktree carries an untracked `api/.venv` symlink to the shared venv; it is never WIP.
    Any other entry — modified, staged, or untracked — counts as dirty and blocks convergence.
    """
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        if line[3:].strip() in ("api/.venv", "api/.venv/"):
            continue
        return False
    return True


def _converge_decision(branch: str, is_clean: bool, commits_behind: int) -> ConvergeAction:
    """Pure guard decision for `klartext converge` (ADR-0012: guarded voluntary convergence).

    Guards in priority order: a non-home branch is never touched (feature branches converge via
    their PR lifecycle); a dirty worktree is never disturbed (consent over coercion); an up-to-date
    branch is a no-op; only a clean home branch that is behind main is rebased.
    """
    if not _is_home_branch(branch):
        return ConvergeAction.SKIP_NOT_HOME_BRANCH
    if not is_clean:
        return ConvergeAction.SKIP_DIRTY
    if commits_behind == 0:
        return ConvergeAction.ALREADY_CURRENT
    return ConvergeAction.SYNC


@dataclass(frozen=True)
class ConvergeResult:
    """Outcome of converging one worktree: the action taken, its branch, and how far behind."""

    action: ConvergeAction
    branch: str
    commits_behind: int


def _git_out(path: Path, *args: str) -> str:
    """Runs a read-only git command in `path` and returns stdout (raises on non-zero exit)."""
    return subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, check=True
    ).stdout


def _converge_worktree(path: Path) -> ConvergeResult:
    """Converges one worktree to `origin/main` under the ADR-0012 guards — never destructively.

    Applies the pure guard decision (only a clean `agent/<slug>` home branch behind main is rebased)
    and layers the failure modes that must never surprise an agent:
      * a path that is not a usable worktree (bare repo / git error) is skipped, not fatal;
      * a failed `git fetch` (offline) is reported, never masqueraded as "already current";
      * a rebase conflict is **aborted** (restoring the pre-rebase HEAD) and reported — the worktree
        is never left half-rebased with conflict markers.
    """
    # Read branch + cleanliness; a bare repo or any git error here means "not a usable worktree".
    try:
        branch = _git_out(path, "rev-parse", "--abbrev-ref", "HEAD").strip()
        porcelain = _git_out(path, "status", "--porcelain")
    except subprocess.CalledProcessError:
        return ConvergeResult(ConvergeAction.SKIP_UNAVAILABLE, branch="", commits_behind=0)
    is_clean = _is_worktree_clean(porcelain)

    # Skip decisions that don't depend on the remote — no need to touch the network for these.
    if not _is_home_branch(branch) or not is_clean:
        return ConvergeResult(_converge_decision(branch, is_clean, 0), branch, 0)

    # A failed fetch must surface, not pass off a stale ref as success.
    fetch = subprocess.run(
        ["git", "-C", str(path), "fetch", "origin", "--quiet"], capture_output=True, text=True
    )
    if fetch.returncode != 0:
        return ConvergeResult(ConvergeAction.SKIP_FETCH_FAILED, branch, 0)

    behind = int(_git_out(path, "rev-list", "--count", "HEAD..origin/main").strip() or "0")
    action = _converge_decision(branch, is_clean, behind)
    if action == ConvergeAction.SYNC:
        rebase = subprocess.run(
            ["git", "-C", str(path), "rebase", "origin/main"], capture_output=True, text=True
        )
        if rebase.returncode != 0:
            # Restore the pre-rebase HEAD — never leave the worktree mid-rebase.
            subprocess.run(["git", "-C", str(path), "rebase", "--abort"], capture_output=True)
            return ConvergeResult(ConvergeAction.SKIP_CONFLICT, branch, behind)
    return ConvergeResult(action=action, branch=branch, commits_behind=behind)


def _parse_worktree_list(porcelain: str) -> list[Path]:
    """Extracts worktree paths from `git worktree list --porcelain` output."""
    prefix = "worktree "
    return [Path(line[len(prefix) :]) for line in porcelain.splitlines() if line.startswith(prefix)]


def _list_worktrees() -> list[Path]:
    """Returns every git worktree of the current repository."""
    return _parse_worktree_list(_git_out(_PROJECT_ROOT, "worktree", "list", "--porcelain"))


def _print_converge_result(path: Path, result: ConvergeResult) -> None:
    """Prints a one-line, colour-coded summary of a worktree's convergence outcome."""
    name = path.name
    if result.action == ConvergeAction.SYNC:
        typer.secho(
            f"✓  {name}: synced ({result.commits_behind} behind → up to date)",
            fg=typer.colors.GREEN,
        )
    elif result.action == ConvergeAction.ALREADY_CURRENT:
        typer.secho(f"✓  {name}: already current", fg=typer.colors.GREEN)
    elif result.action == ConvergeAction.SKIP_DIRTY:
        typer.secho(
            f"⊘  {name}: skipped — uncommitted changes (rebase manually when ready)",
            fg=typer.colors.YELLOW,
        )
    elif result.action == ConvergeAction.SKIP_NOT_HOME_BRANCH:
        typer.secho(
            f"⊘  {name}: skipped — on {result.branch} (a feature branch converges via its PR)",
            fg=typer.colors.YELLOW,
        )
    elif result.action == ConvergeAction.SKIP_CONFLICT:
        typer.secho(
            f"✗  {name}: rebase conflict — aborted, worktree restored; resolve manually",
            fg=typer.colors.RED,
        )
    elif result.action == ConvergeAction.SKIP_FETCH_FAILED:
        typer.secho(
            f"✗  {name}: could not fetch origin (offline?) — not converged",
            fg=typer.colors.RED,
        )
    else:  # SKIP_UNAVAILABLE
        typer.secho(f"⊘  {name}: skipped — not a usable worktree", fg=typer.colors.YELLOW)


@app.command()
def converge(
    all_worktrees: bool = typer.Option(
        False, "--all", help="Converge every worktree of the repo, not just the current one"
    ),
) -> None:
    """Converge worktree(s) to origin/main under the ADR-0012 guards (voluntary convergence).

    Only a clean `agent/<slug>` home branch that is behind main is rebased; feature branches and
    dirty worktrees are reported and left untouched. Idempotent — safe to re-run.
    """
    targets = _list_worktrees() if all_worktrees else [Path.cwd()]
    for path in targets:
        _print_converge_result(path, _converge_worktree(path))


# ---------------------------------------------------------------------------
# skills sync — mirror repo skills into ~/.claude/skills/ (repo is the SoT)
# ---------------------------------------------------------------------------


class SkillsSyncAction(StrEnum):
    """Outcome of mirroring one skill from the repo into the install directory."""

    INSTALLED = "installed"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    PRUNED = "pruned"


def _collect_skill_files(source: Path) -> dict[str, bytes]:
    """Returns the desired install file set for one source skill, keyed by relative path.

    A flat `<name>.md` source becomes a single `SKILL.md`; a `<name>/` directory is mirrored
    file-for-file (multi-file skills like qa-review keep their companion docs). The
    `.repo-managed` marker is never part of the comparison set — it is install metadata.
    """
    if source.is_file():
        return {"SKILL.md": source.read_bytes()}
    files: dict[str, bytes] = {}
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        rel = path.relative_to(source).as_posix()
        if rel == _REPO_MANAGED_MARKER:
            continue
        files[rel] = path.read_bytes()
    return files


def _read_managed_files(skill_dir: Path) -> dict[str, bytes]:
    """Returns a target skill dir's installed files by relative path (excludes the marker)."""
    files: dict[str, bytes] = {}
    for path in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(skill_dir).as_posix()
        if rel == _REPO_MANAGED_MARKER:
            continue
        files[rel] = path.read_bytes()
    return files


def _source_skills(source_dir: Path) -> dict[str, Path]:
    """Maps skill name → source path. Skills are flat `<name>.md` files or `<name>/` directories."""
    skills: dict[str, Path] = {}
    if not source_dir.exists():
        return skills
    for entry in sorted(source_dir.iterdir()):
        if entry.is_dir():
            skills[entry.name] = entry
        elif entry.suffix == ".md":
            skills[entry.stem] = entry
    return skills


def _sync_skills(source_dir: Path, target_dir: Path) -> dict[str, SkillsSyncAction]:
    """Mirrors repo skills into the install dir, idempotently and prune-safely.

    The repo is the single source of truth. Each source skill (flat `<name>.md` or `<name>/`
    directory) is installed as `<target>/<name>/` with a `.repo-managed` marker. Re-running is a
    no-op (UNCHANGED) when content matches; changed content is overwritten (UPDATED). Managed
    target dirs whose source has disappeared are pruned (handles renames like pre-compact→anchor);
    unmarked foreign/plugin skills are never touched.
    """
    result: dict[str, SkillsSyncAction] = {}
    sources = _source_skills(source_dir)

    for name, source in sources.items():
        desired = _collect_skill_files(source)
        skill_dir = target_dir / name
        if not skill_dir.exists():
            action = SkillsSyncAction.INSTALLED
        elif _read_managed_files(skill_dir) != desired:
            action = SkillsSyncAction.UPDATED
        else:
            action = SkillsSyncAction.UNCHANGED

        if action in (SkillsSyncAction.INSTALLED, SkillsSyncAction.UPDATED):
            if skill_dir.exists():
                shutil.rmtree(skill_dir)
            for rel, content in desired.items():
                dest = skill_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
        # Always ensure the marker exists, even on an UNCHANGED re-sync of a hand-copied dir.
        marker = skill_dir / _REPO_MANAGED_MARKER
        if not marker.exists():
            marker.write_text("")
        result[name] = action

    # Prune managed dirs whose source is gone; leave unmarked foreign skills untouched.
    # Guard: never prune when the source yielded *no* skills. A missing or empty source dir
    # (a path typo, a wrong cwd, a broken checkout) must not be read as "every skill deleted"
    # and wipe the whole ~/.claude/skills/ install — pruning only ever follows a real source.
    if sources and target_dir.exists():
        for entry in sorted(target_dir.iterdir()):
            if (
                entry.is_dir()
                and entry.name not in sources
                and (entry / _REPO_MANAGED_MARKER).exists()
            ):
                shutil.rmtree(entry)
                result[entry.name] = SkillsSyncAction.PRUNED

    return result


@skills_app.command("sync")
def skills_sync() -> None:
    """Mirror the repo's skills into ~/.claude/skills/ — idempotent, prune-safe, repo is the SoT.

    Each skill under docs/superpowers/skills/ (flat `<name>.md` or `<name>/` directory) is installed
    as ~/.claude/skills/<name>/, marked `.repo-managed`. Re-running is safe; managed skills whose
    source was removed are pruned, foreign/plugin skills are left untouched.
    """
    # Fail loudly on a missing source rather than print a misleading "✓ synced" having done
    # nothing — its absence means a broken checkout or a wrong cwd, not an empty skill set.
    if not _SKILLS_SOURCE.exists():
        typer.secho(f"✗  skills source not found: {_SKILLS_SOURCE}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    result = _sync_skills(_SKILLS_SOURCE, _SKILLS_TARGET)
    colours = {
        SkillsSyncAction.INSTALLED: typer.colors.GREEN,
        SkillsSyncAction.UPDATED: typer.colors.GREEN,
        SkillsSyncAction.UNCHANGED: typer.colors.WHITE,
        SkillsSyncAction.PRUNED: typer.colors.YELLOW,
    }
    for name in sorted(result):
        action = result[name]
        typer.secho(f"  {action.value:>9}  {name}", fg=colours[action])
    typer.secho(f"✓  skills synced → {_SKILLS_TARGET}", fg=typer.colors.GREEN)


# ---------------------------------------------------------------------------
# db subcommands
# ---------------------------------------------------------------------------


@db_app.command("start")
def db_start() -> None:
    """Start the local Supabase instance."""
    _supabase_start()


@db_app.command("reset")
def db_reset() -> None:
    """Reset the local Supabase database and re-apply all migrations."""
    _db_reset()


@db_app.command("status")
def db_status() -> None:
    """Show the status of the local Supabase instance."""
    subprocess.run(["supabase", "status"], cwd=str(_PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app()
