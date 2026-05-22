"""klartext CLI — infrastructure commands for local development.

Usage (after pip install -e .):
  klartext start          Start the API server (dev mode with auto-reload)
  klartext test           Run the unit test suite
  klartext test --all     Run unit tests + integration tests
  klartext health         Call the /health endpoint and print results
  klartext testdata       Seed the database with a consistent test dataset
  klartext db reset       Reset the local Supabase database (re-applies migrations)
  klartext db status      Show the status of the local Supabase instance
"""

from __future__ import annotations

import subprocess
import sys

import httpx
import typer

app = typer.Typer(
    name="klartext",
    help="Infrastructure commands for the klartext.jetzt API.",
    no_args_is_help=True,
)

db_app = typer.Typer(help="Database commands (Supabase).")
app.add_typer(db_app, name="db")


# ---------------------------------------------------------------------------
# start
# ---------------------------------------------------------------------------


@app.command()
def start(
    host: str = typer.Option("127.0.0.1", help="Bind address"),
    port: int = typer.Option(8000, help="Port"),
    reload: bool = typer.Option(True, help="Enable auto-reload (dev mode)"),
) -> None:
    """Start the FastAPI development server."""
    cmd = [
        sys.executable, "-m", "uvicorn", "api.main:app",
        "--host", host,
        "--port", str(port),
    ]
    if reload:
        cmd.append("--reload")

    typer.echo(f"Starting klartext API on http://{host}:{port}")
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------------------
# test
# ---------------------------------------------------------------------------


@app.command()
def test(
    all_tests: bool = typer.Option(False, "--all", help="Include integration tests"),
    verbose: bool = typer.Option(False, "-v", help="Verbose output"),
    path: str = typer.Option("tests/", help="Test path or file"),
) -> None:
    """Run the test suite."""
    cmd = [sys.executable, "-m", "pytest", path]

    if all_tests:
        cmd += ["-m", ""]          # deselect nothing → runs everything
        typer.echo("Running all tests (unit + integration)…")
    else:
        typer.echo("Running unit tests…")

    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd)
    raise typer.Exit(result.returncode)


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# testdata
# ---------------------------------------------------------------------------


@app.command()
def testdata(
    url: str = typer.Option(
        "http://127.0.0.1:8000", help="Base URL of the running API"
    ),
) -> None:
    """Seed the database with a consistent test dataset.

    Connects to the running API and creates a narrative with scenes and
    pre-defined claims. Safe to run repeatedly — creates new records each time.

    Requires the API server to be running: klartext start
    """
    import asyncio
    import json

    import httpx

    typer.echo("Seeding test data via API…\n")

    # -- verify API is reachable --
    try:
        httpx.get(f"{url}/health", timeout=3).raise_for_status()
    except Exception:
        typer.secho("✗  API not reachable — run: klartext start", fg=typer.colors.RED)
        raise typer.Exit(1)

    async def seed() -> None:
        from api.seeddata import FIXTURE_PATH, SEED_CAUSAL_MODEL, SEED_CLAIMS

        async with httpx.AsyncClient(base_url=url, timeout=30) as client:
            # 1. Import narrative
            typer.echo("  → Importing Klartext narrative…")
            response = await client.post(
                "/narratives/import", json={"path": str(FIXTURE_PATH)}
            )
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

            # 2. Extract claims for the first three scenes

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

            # 4. Add axioms to the causal model
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
                        f"  ⚠  Axiom '{axiom.label}' failed "
                        f"({axiom_response.status_code})",
                        fg=typer.colors.YELLOW,
                    )

    asyncio.run(seed())

    typer.echo()
    typer.secho("Done. System is seeded with test data.", fg=typer.colors.GREEN, bold=True)


# ---------------------------------------------------------------------------
# db reset / db status
# ---------------------------------------------------------------------------


@db_app.command("reset")
def db_reset(
    project_dir: str = typer.Option(".", help="Supabase project directory"),
) -> None:
    """Reset the local Supabase database and re-apply all migrations."""
    typer.echo("Resetting local database…")
    result = subprocess.run(
        ["supabase", "db", "reset"],
        cwd=project_dir,
    )
    raise typer.Exit(result.returncode)


@db_app.command("status")
def db_status(
    project_dir: str = typer.Option(".", help="Supabase project directory"),
) -> None:
    """Show the status of the local Supabase instance."""
    subprocess.run(["supabase", "status"], cwd=project_dir)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
