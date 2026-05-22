#!/usr/bin/env bash
# setup.sh — Bootstrap klartext.jetzt for local development.
#
# Run this once after cloning the repository. Subsequent starts use
# the klartext CLI (pip install -e api/).
#
# Prerequisites:
#   - Python 3.12+   https://python.org
#   - Node.js 20+    https://nodejs.org
#   - Supabase CLI   https://supabase.com/docs/guides/cli
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

command -v python3 >/dev/null 2>&1 || error "Python 3.12+ is required (https://python.org)"
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PYTHON_VERSION"

command -v node >/dev/null 2>&1 || error "Node.js 20+ is required (https://nodejs.org)"
NODE_VERSION=$(node --version)
info "Node $NODE_VERSION"

if ! command -v supabase >/dev/null 2>&1; then
    info "Supabase CLI not found — installing via npm…"
    command -v npm >/dev/null 2>&1 || error "npm is required to install the Supabase CLI"
    npm install -g supabase --silent
fi
SUPABASE_VERSION=$(supabase --version)
info "Supabase CLI $SUPABASE_VERSION"

success "All prerequisites found"

# ---------------------------------------------------------------------------
# API (Python)
# ---------------------------------------------------------------------------

section "Setting up API"

cd api

if [ ! -d ".venv" ]; then
    info "Creating virtual environment…"
    python3 -m venv .venv
fi

info "Installing dependencies…"
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pip install -q -e .

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
# Supabase
# ---------------------------------------------------------------------------

section "Starting local Supabase"

if [ "${SKIP_SUPABASE_START:-false}" = "true" ]; then
    info "Skipping supabase start (SKIP_SUPABASE_START=true)"
else
    info "Running supabase start (this may take a few minutes on first run)…"
    supabase start
    success "Supabase running — Studio at http://127.0.0.1:54323"
fi

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
