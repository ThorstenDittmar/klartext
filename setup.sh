#!/usr/bin/env bash
# setup.sh — Bootstrap klartext.jetzt for local development.
#
# Run this once after cloning the repository. Subsequent starts use
# the klartext CLI (source api/.venv/bin/activate && klartext start).
#
# Prerequisites:
#   - Node.js 20+    https://nodejs.org
#   - Supabase CLI   https://supabase.com/docs/guides/cli
#   - uv             https://docs.astral.sh/uv (installed automatically if missing)
#
# Usage:
#   bash setup.sh

set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

info()    { echo "  → $*"; }
success() { echo "  ✓ $*"; }
error()   { echo "  ✗ $*" >&2; exit 1; }
section() { echo; echo "── $* ──────────────────────────────"; }

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

section "Checking prerequisites"

command -v node >/dev/null 2>&1 || error "Node.js 20+ is required (https://nodejs.org)"
NODE_VERSION=$(node --version)
info "Node $NODE_VERSION"

if ! command -v uv >/dev/null 2>&1; then
    info "uv not found — installing via official installer…"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
UV_VERSION=$(uv --version)
info "uv $UV_VERSION"

if ! command -v supabase >/dev/null 2>&1; then
    info "Supabase CLI not found — installing via npm…"
    command -v npm >/dev/null 2>&1 || error "npm is required to install the Supabase CLI"
    npm install -g supabase --silent
fi
SUPABASE_VERSION=$(supabase --version)
info "Supabase CLI $SUPABASE_VERSION"

if ! command -v claude >/dev/null 2>&1; then
    info "Claude Code not found — installing via npm…"
    command -v npm >/dev/null 2>&1 || error "npm is required to install Claude Code"
    npm install -g @anthropic-ai/claude-code --silent
fi
CLAUDE_VERSION=$(claude --version)
info "Claude Code $CLAUDE_VERSION"

success "All prerequisites found"

# ---------------------------------------------------------------------------
# API (Python)
# ---------------------------------------------------------------------------

section "Setting up API"

cd api

if [ ! -d ".venv" ]; then
    info "Creating virtual environment (Python 3.12)…"
    uv venv .venv --python 3.12
fi

info "Installing dependencies…"
uv pip install --python .venv/bin/python -q -e '.[dev]'

if [ ! -f ".env" ]; then
    info "Creating .env from .env.example…"
    cp .env.example .env
    echo
    echo "  ⚠️  Fill in your credentials in api/.env before starting:"
    echo "     ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY"
fi

success "API ready — activate with: source api/.venv/bin/activate"

cd ..

# ---------------------------------------------------------------------------
# Frontend (Node)
# ---------------------------------------------------------------------------

section "Setting up frontend"

cd frontend

info "Installing npm packages…"
npm install --silent

if [ ! -f ".env.local" ]; then
    info "Creating .env.local from .env.example…"
    cp .env.example .env.local
fi

success "Frontend ready"

cd ..

# ---------------------------------------------------------------------------
# Git hooks (pre-commit)
# ---------------------------------------------------------------------------

section "Installing git hooks"

info "Installing pre-commit hooks…"
api/.venv/bin/pre-commit install
success "Git hooks installed — hooks run automatically before every commit"

# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------

section "Starting local Supabase"

if [ "${SKIP_SUPABASE_START:-false}" = "true" ]; then
    info "Skipping supabase start (SKIP_SUPABASE_START=true)"
else
    info "Resetting and starting local Supabase (this may take a few minutes on first run)…"
    api/.venv/bin/klartext db reset
    success "Supabase running — Studio at http://127.0.0.1:54323"
fi

# ---------------------------------------------------------------------------
# External reference assets
# ---------------------------------------------------------------------------

section "External reference assets"

info "assets-local/ holds licensed/large reference files (gitignored, agents can read)."
info "Place PDFs and external materials there — never in ~/Downloads (TCC-blocked on macOS)."
info "See assets-local/README.md for the file register and provenance convention."

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

section "Setup complete"
echo
echo "  Next steps:"
echo "    1. Fill in api/.env (ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)"
echo "       Supabase values are printed above by 'supabase start'."
echo "    2. Start the API:      klartext start"
echo "    3. Run tests:          klartext test"
echo "    4. Check health:       klartext health"
echo "    5. Start the frontend: cd frontend && npm run dev"
echo
