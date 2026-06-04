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
  klartext db start           Start the local Supabase instance
  klartext db reset           Reset the local Supabase database (re-applies migrations)
  klartext db status          Show the status of the local Supabase instance
"""

from __future__ import annotations

import asyncio
import re
import subprocess
import sys
import time
from pathlib import Path

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

_PROJECT_ROOT = Path(__file__).parent.parent
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"


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
    all_tests: bool = typer.Option(False, "--all", help="Include integration tests"),
    verbose: bool = typer.Option(False, "-v", help="Verbose output"),
    path: str = typer.Option("tests/", help="Test path or file"),
) -> None:
    """Run the test suite."""
    cmd = [sys.executable, "-m", "pytest", path]

    if all_tests:
        cmd += ["-m", ""]
        typer.echo("Running all tests (unit + integration)…")
    else:
        typer.echo("Running unit tests…")

    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd)
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
