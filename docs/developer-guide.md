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
| `klartext flush` | TRUNCATE all data tables without restarting anything — server keeps running, DB is empty after reload |
| `klartext flush --yes` | Same, without confirmation prompt |
| `klartext db reset` | Reset local database and re-apply all migrations |
| `klartext db status` | Show status of the local Supabase instance |
| `klartext converge` | Rebase the current worktree onto `origin/main` under the [ADR-0012](adr/0012-worktree-convergence-model.md) guards (clean `agent/<slug>` home branch only; never touches WIP or feature branches) |
| `klartext converge --all` | Same, across every worktree of the repo — the one-liner that propagates a committed settings/hook/pin change to all home-branch worktrees |

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

The migration files in `supabase/migrations/` are the single source of truth for the schema — `klartext db reset` rebuilds the database entirely from them. Never run SQL manually in the Supabase dashboard.

To add a schema change:

```bash
# 1. Create a new migration file (Supabase generates the timestamp prefix)
supabase migration new describe_your_change

# 2. Write the SQL in the generated file

# 3. Apply and verify locally
klartext db reset
```

The migration history lives in `git log -- supabase/migrations/`. Planned schema changes belong in GitHub Issues, not here.

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

## Agent session identity (SessionStart hook)

Each specialist agent works in its own git worktree under `~/klartext-worktrees/<slug>/`. So a
session knows *which* agent it is, a `SessionStart` hook in `.claude/settings.json` injects that
agent's Hoheitswissen at session start — and on `/clear`, which the desktop app reports as
`source=startup`:

- **Script:** `scripts/load_agent_identity.py` derives the slug from the worktree basename
  (`CLAUDE_PROJECT_DIR`); if `agents/<slug>/claude.md` exists it emits it as SessionStart
  `additionalContext` (an `EXTREMELY_IMPORTANT` preamble plus the full file). For any other
  directory (main checkout, clones, CI) it is a silent no-op — exit 0, no output.
- **Matcher:** `startup|clear|compact` — covers session open, `/clear`, and re-injection after a compaction.
- **Verification:** `api/tests/infrastructure/test_session_start_hook.py` gates the wiring and the
  loader behaviour. The runtime injection (the desktop app cannot be scripted) is checked by the
  manual Canary in [`environment/claude-code-app.md`](superpowers/improvement/environment/claude-code-app.md).

Rationale and the return-to-app gate: [ADR-0011](adr/0011-return-to-desktop-app-session-start.md) (condition G1).

### Session health / drift warning (SessionStart hook)

A second `SessionStart` hook (`scripts/session_health.py`, matcher `startup|clear`) warns — **never
blocks** — when the worktree is behind `origin/main`, so a session does not resume work on a stale
substrate. This is the *"verify current before resume"* clause of the Controlled-Method-Rollout
practice and the detection half of [ADR-0012](adr/0012-worktree-convergence-model.md); the action is
`klartext converge`.

- **Fail-soft:** stdlib only; any error or an unreachable remote → exit 0, no warning (never nags on
  a state it cannot verify, never blocks a session).
- **Detection behind a port:** `DriftSignal` with the L1 `CommitCountDrift` adapter; a later L2
  (shared-layer-weighted) is an adapter swap (OE's Drift-Awareness practice).
- **Memory-substrate checks:** the same hook also warns on a broken memory substrate (the
  [contract](superpowers/improvement/contracts/memory-substrate.md)) — **C1** the committed
  `autoMemoryDirectory` resolves to the shared team path, **C3** the cross-agent inbox transport
  (`scripts/inbox.sh`) is reachable. Both apply only to an agent worktree (a `.claude/` dir present).
- **Verification:** `api/tests/infrastructure/test_session_health.py` (pure signal, real-git
  assessment, e2e hook, settings wiring, C1/C3 checks).

---

## Team auto-memory (shared blackboard)

All agents share one auto-memory directory — the team blackboard at
`~/.claude/klartext-team-memory`. Auto-memory is otherwise keyed by the sanitized *cwd*, so each
worktree would get its own store; pinning a fixed `autoMemoryDirectory` makes every worktree resolve
to the same directory.

- **Where the pin lives:** the **committed** `.claude/settings.json` (`autoMemoryDirectory`,
  `autoMemoryEnabled`). It is byte-identical in every worktree, so all agents share one store. The
  desktop app honors a project-scope `autoMemoryDirectory` **after the worktree's trust dialog is
  accepted** — the same gate as the hooks.
- **Trust matters:** an *untrusted* worktree silently ignores the pin and falls back to a per-cwd
  default — a lonely store, not the team blackboard. Accept the trust dialog on first open of each
  worktree (you already do this for the SessionStart hook).
- **Not user-global:** the pin must **not** live in `~/.claude/settings.json`. A user-global pin
  redirects *every* machine session — klartext or not — onto the team memory. `setup.sh` cleans any
  stale user-global pin on each run.
- **Verification:** `api/tests/infrastructure/test_automemory_settings.py` gates the committed pin
  and the setup cleanup. The runtime honoring (the desktop app cannot be scripted) was verified
  empirically and is re-checked after app updates by the Canary in
  [`environment/claude-code-app.md`](superpowers/improvement/environment/claude-code-app.md).

---

## CI/CD

GitHub Actions workflows run on every push and pull request:

| Workflow | Trigger | What it does |
|---|---|---|
| `lint.yml` | push to `main` / PR | `ruff check`, `ruff format --check`, `mypy` on API; `eslint`, `tsc` on frontend |
| `test.yml` | push to `main` / PR | Unit tests (no Supabase required) |
| `classify-gate.yml` | PR | Requires a `rolling`/`breaking` label on Way-of-Working PRs (see below) |
| `deploy-docs.yml` | push to `main` (docs/** changed) | Builds and deploys MkDocs to GitHub Pages |

> CI triggers on `push` are restricted to `main`; PRs are validated via the `pull_request`
> event. This avoids duplicate `push`+`pull_request` check runs on the same commit.

### Classification labels (`rolling` / `breaking`)

A PR that touches a **Way-of-Working surface** must carry exactly one classification label,
per [ADR-0012](adr/0012-worktree-convergence-model.md). `classify-gate.yml` enforces this; the
decision lives in `scripts/classify_gate.py`.

| Label | Meaning |
|---|---|
| `rolling` | Additive / backward-compatible. Worktrees adopt it lazily via `klartext converge`. |
| `breaking` | Changes the meaning of an existing rule, hook, path, or contract. Needs a coordinated rollout (all worktrees converge before it is relied upon). |

**In-scope surfaces:** `CLAUDE.md`, `docs/superpowers/skills/**`, `agents/**/claude.md`,
`.claude/settings.json`, `scripts/**`, `api/cli.py`.

The gate is **default-free** — if unsure, choose `breaking`. PRs that touch no Way-of-Working
surface need no label (the gate passes automatically). Adding the label re-runs the check
without a new commit (it listens for `labeled`/`unlabeled` events).

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
