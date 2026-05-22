# Developer Guide

This guide covers everything you need to get klartext.jetzt running locally, understand the project structure, and work effectively in a GitHub Codespace.

---

## Prerequisites

| Tool | Version | Install | Notes |
|---|---|---|---|
| Python | 3.12+ | [python.org](https://python.org) | Required |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) | Required |
| Supabase CLI | latest | [supabase.com/docs/guides/cli](https://supabase.com/docs/guides/cli) | Installed automatically by `setup.sh` if missing |
| GitHub CLI | latest | [cli.github.com](https://cli.github.com) | Optional — needed for Codespace management |

---

## Local setup

Clone the repo and run the bootstrap script once:

```bash
git clone https://github.com/ThorstenDittmar/klartext.git
cd klartext
bash setup.sh
```

`setup.sh` will:

1. Check all prerequisites
2. Create `api/.venv` and install Python dependencies
3. Install the `klartext` CLI command (`pip install -e api/`)
4. Run `npm install` for the frontend
5. Start the local Supabase stack (`supabase start`)

After `supabase start` prints the connection details, copy the values into `api/.env`:

```bash
# api/.env
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...
ENVIRONMENT=development
```

---

## Environment variables

### `api/.env`

| Variable | Description | Where to find it |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| `SUPABASE_URL` | Local Supabase API URL | Printed by `supabase start` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (bypasses RLS) | Printed by `supabase start` |
| `ENVIRONMENT` | `development` or `production` | Set manually |

### `frontend/.env.local`

| Variable | Description |
|---|---|
| `VITE_SUPABASE_URL` | Same as `SUPABASE_URL` above |
| `VITE_SUPABASE_ANON_KEY` | Anon key printed by `supabase start` |

---

## CLI commands

After setup, the `klartext` command is available in your virtual environment:

```bash
source api/.venv/bin/activate
```

| Command | Description |
|---|---|
| `klartext start` | Start the FastAPI server with auto-reload at `http://localhost:8000` |
| `klartext test` | Run unit tests (excludes integration tests) |
| `klartext test --all` | Run unit + integration tests (requires running Supabase + API keys) |
| `klartext test -v` | Run unit tests with verbose output |
| `klartext health` | Call `/health` and print per-dependency status |
| `klartext testdata` | Seed the database with a consistent test dataset (requires running API + Supabase) |
| `klartext db reset` | Reset local database and re-apply all migrations |
| `klartext db status` | Show status of the local Supabase instance |

---

## API endpoints

The interactive API docs are available at `http://localhost:8000/docs` when the server is running.

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Infrastructure health check |
| `GET` | `/docs` | Interactive Swagger UI |
| `POST` | `/narratives/import` | Import a narrative from a Markdown file |
| `GET` | `/narratives` | List all narratives |
| `GET` | `/narratives/{id}` | Get a narrative with its scenes |
| `POST` | `/narratives/{id}/scenes/{scene_id}/extract-claims` | Extract claims from a scene |
| `GET` | `/narratives/{id}/scenes/{scene_id}/claims` | List claims for a scene |
| `POST` | `/claims/extract` | Extract claims from raw text |

### Health check response

```json
{
  "status": "ok",
  "version": "0.1.0",
  "checks": {
    "database": { "status": "ok" },
    "anthropic": { "status": "ok" }
  }
}
```

`status` is `"ok"` when all checks pass, `"degraded"` when one or more fail. HTTP status is always `200` — read the body to detect degradation.

---

## Database

Schema is managed via migration files in `supabase/migrations/`. Never run SQL manually in the Supabase dashboard.

| Migration | Description |
|---|---|
| `20260521000001_initial_schema.sql` | Core tables: users, narratives, Wirkmodelle, RLS policies |
| `20260521000002_claims_table.sql` | Claims table with FK to narrative_einheiten |

To apply new changes:

```bash
# Create a new migration (Supabase generates the timestamp)
supabase migration new my_change_description

# Reset (drops and recreates the local DB, re-applies all migrations)
klartext db reset
```

---

## Testing

```bash
klartext test          # unit tests only (fast, no external services)
klartext test --all    # includes integration tests (needs Supabase + API keys)
klartext test -v       # verbose output
```

The test suite follows four layers, always written before implementation:

1. **Domain** — pure unit tests, no mocks
2. **Services** — unit tests with fake repositories
3. **Repositories** — `@pytest.mark.integration` tests against real Supabase
4. **Routers** — API tests via FastAPI `TestClient`

Integration tests are excluded from the default run (`pytest.ini` sets `-m 'not integration'`).

---

## GitHub Codespaces

The repository works out of the box in a GitHub Codespace.

### First-time setup in a Codespace

The Codespace already has the repository cloned. Run the bootstrap script — it installs the Supabase CLI automatically if missing:

```bash
bash setup.sh
```

Then fill in `api/.env` with the values printed by `supabase start`:

```bash
nano api/.env
# SUPABASE_URL=http://127.0.0.1:54321
# SUPABASE_SERVICE_ROLE_KEY=sb_secret_...
# ANTHROPIC_API_KEY=sk-ant-...   ← see section below
```

### Adding secrets to a Codespace

Set the `ANTHROPIC_API_KEY` as a Codespace secret so it is available automatically:

```bash
gh secret set ANTHROPIC_API_KEY --app codespaces --repo ThorstenDittmar/klartext
```

Then restart the Codespace for the secret to take effect. Alternatively, export it for the current session:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Running integration tests in a Codespace

```bash
cd api
SUPABASE_URL=http://127.0.0.1:54321 \
SUPABASE_SERVICE_ROLE_KEY=sb_secret_... \
python3 -m pytest tests/ -m integration -v
```

---

## CI/CD

GitHub Actions workflows run on every push and pull request:

| Workflow | Trigger | What it does |
|---|---|---|
| `lint.yml` | push / PR | `ruff check`, `ruff format --check`, `mypy` on API; `eslint`, `tsc` on frontend |
| `test.yml` | push / PR | Unit tests (no Supabase required) |
| `deploy-docs.yml` | push to `main` (docs/** changed) | Builds and deploys MkDocs to GitHub Pages |

---

## Architecture

```
klartext/
├── api/                   # Python 3.12 + FastAPI
│   ├── routers/           # HTTP routing only
│   ├── services/          # Business logic (OOP)
│   ├── repositories/      # Data access (Supabase adapters)
│   ├── models/            # Domain objects
│   ├── schemas/           # Pydantic request/response shapes
│   ├── exceptions/        # Exception hierarchy per layer
│   ├── providers/         # AI provider adapters (Claude)
│   ├── parsers/           # Input parsers (Markdown)
│   ├── cli.py             # typer CLI
│   └── main.py            # FastAPI app entry point
├── frontend/              # React 18 + TypeScript + Vite
├── supabase/
│   ├── migrations/        # SQL migration files (source of truth)
│   └── config.toml        # Supabase project config
├── docs/                  # MkDocs Material — specification + developer docs
├── setup.sh               # One-shot bootstrap script
└── .github/workflows/     # CI/CD pipelines
```

See [`CLAUDE.md`](../CLAUDE.md) for the full coding standards.
