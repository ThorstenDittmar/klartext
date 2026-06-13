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
# Compact-Monitor (macOS only)
# ---------------------------------------------------------------------------

section "Installing compact monitor"

if [[ "$(uname)" == "Darwin" ]]; then
    PLIST_DEST="$HOME/Library/LaunchAgents/com.klartext.compact-monitor.plist"
    REPO_DIR="$(pwd)"
    # The compact-log lives centrally in the pinned team memory, not per repo/worktree,
    # so this one launchd instance catches compacts from every per-agent worktree.
    MONITOR_MEMORY_DIR="$HOME/.claude/klartext-team-memory"
    mkdir -p "$MONITOR_MEMORY_DIR"

    info "Installing launchd agent for auto-compact monitoring…"
    sed -e "s|@@REPO_DIR@@|$REPO_DIR|g" -e "s|@@MEMORY_DIR@@|$MONITOR_MEMORY_DIR|g" \
        scripts/com.klartext.compact-monitor.plist.template > "$PLIST_DEST"
    chmod +x scripts/check-compact-log.sh

    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    launchctl load "$PLIST_DEST"

    success "Compact monitor installed — checks hourly, notifies on auto-compacts"
else
    info "Skipping compact monitor (launchd is macOS-only — not available on Linux/Codespace)"
fi

# ---------------------------------------------------------------------------
# Auto-memory location (shared team blackboard)
# ---------------------------------------------------------------------------

section "Auto-memory location"

# The team blackboard lives at a fixed path that every worktree resolves to. The
# pin now lives in the COMMITTED .claude/settings.json (autoMemoryDirectory), which
# the desktop app honors after the worktree's trust dialog is accepted and which is
# byte-identical in every worktree — so all agents share one memory directory.
#
# Why not the user-global ~/.claude/settings.json (the old approach): a user-global
# pin redirects EVERY machine session — klartext or not — onto the team memory. This
# setup step therefore (1) ensures the directory exists and (2) CLEANS any stale
# user-global pin left by previous setup runs, so unrelated projects stop leaking.
# Empirics behind this: docs/superpowers/improvement/environment/claude-code-app.md.
MEMORY_DIR="$HOME/.claude/klartext-team-memory"
USER_SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$MEMORY_DIR" "$HOME/.claude"

# Remove the stale user-global auto-memory pin without clobbering other values
# (theme, plugins, …). Idempotent: a no-op once the keys are gone.
if [ -f "$USER_SETTINGS" ]; then
    python3 - "$USER_SETTINGS" <<'PY'
import json, pathlib, sys

path = pathlib.Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except (json.JSONDecodeError, FileNotFoundError):
    sys.exit(0)
removed = [k for k in ("autoMemoryEnabled", "autoMemoryDirectory") if k in data]
for k in removed:
    data.pop(k)
if removed:
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("cleaned stale user-global auto-memory keys: " + ", ".join(removed))
PY
fi

success "Team memory at $MEMORY_DIR — pinned via committed .claude/settings.json"
info "First open of each worktree: accept the trust dialog (same gate as the hooks)."
info "Untrusted worktrees silently fall back to a per-cwd default — not the team blackboard."

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
