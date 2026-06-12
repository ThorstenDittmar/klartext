#!/usr/bin/env bash
# morning.sh — daily startup script for terminal-mode klartext agents.
#
# Reads agents/team.yaml and starts all agents with status=terminal and active=true.
# Opens one terminal tab per agent (iTerm2 preferred, Terminal.app fallback), with a
# staggered delay between launches to avoid git index.lock contention — worktrees share
# one object store, and simultaneous rebases compete for the same lock file.
#
# Usage: bash scripts/morning.sh
#
# Env overrides:
#   KLARTEXT_REPO_ROOT          main checkout (default: this script's repo)
#   KLARTEXT_MORNING_STAGGER    seconds between agent launches (default: 5)
#   KLARTEXT_MORNING_DRY_RUN    if set, print what would run instead of opening terminals

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="${KLARTEXT_REPO_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
TEAM_YAML="$REPO_ROOT/agents/team.yaml"
STAGGER="${KLARTEXT_MORNING_STAGGER:-5}"

if [ ! -f "$TEAM_YAML" ]; then
    echo "❌ team.yaml not found at $TEAM_YAML" >&2
    exit 1
fi

# Extract terminal+active agents from team.yaml. pyyaml is guaranteed on macOS developer setups.
# Write to a temp file so that a Python parse error propagates as a non-zero exit code —
# process substitution (< <(...)) swallows the exit code in bash 3/4, a temp file does not.
_tmpfile=$(mktemp)
trap 'rm -f "$_tmpfile"' EXIT

python3 - "$TEAM_YAML" <<'PYEOF' > "$_tmpfile" || { echo "❌ Failed to parse team.yaml — check for syntax errors" >&2; exit 1; }
import sys, yaml
with open(sys.argv[1]) as f:
    data = yaml.safe_load(f)
for a in data.get("agents", []):
    if a.get("status") == "terminal" and a.get("active", False):
        print(f"{a['slug']}|{a.get('display', a['slug'])}")
PYEOF

AGENT_LINES=()
while IFS= read -r line; do
    AGENT_LINES+=("$line")
done < "$_tmpfile"

if [ ${#AGENT_LINES[@]} -eq 0 ]; then
    echo "ℹ️  No terminal agents found in team.yaml — nothing to start."
    exit 0
fi

echo "🌅 Starting ${#AGENT_LINES[@]} terminal agent(s)..."

_open_tab() {
    local slug="$1"
    local display="$2"
    local start_script="$REPO_ROOT/agents/$slug/start.sh"
    local cmd="cd '$REPO_ROOT' && bash agents/$slug/start.sh"

    if osascript -e 'tell application "System Events" to (name of processes) contains "iTerm2"' 2>/dev/null | grep -q true; then
        osascript <<APPLESCRIPT
tell application "iTerm2"
    activate
    tell current window
        create tab with default profile
        tell current session of current tab
            set name to "$display"
            write text "$cmd"
        end tell
    end tell
end tell
APPLESCRIPT
    else
        osascript <<APPLESCRIPT
tell application "Terminal"
    activate
    set t to do script "$cmd"
    set custom title of t to "$display"
end tell
APPLESCRIPT
    fi
}

first=true
for entry in "${AGENT_LINES[@]}"; do
    IFS='|' read -r slug display <<< "$entry"

    if [ "$first" = true ]; then
        first=false
    else
        echo "  ⏱  Waiting ${STAGGER}s (avoiding git index.lock contention)..."
        sleep "$STAGGER"
    fi

    echo "  → $display ($slug)"

    if [ -n "${KLARTEXT_MORNING_DRY_RUN:-}" ]; then
        echo "  [dry-run] would open tab: bash agents/$slug/start.sh"
    else
        _open_tab "$slug" "$display"
    fi
done

echo "✅ Done."
