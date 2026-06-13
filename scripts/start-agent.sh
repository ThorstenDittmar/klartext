#!/usr/bin/env bash
# start-agent.sh — launch a klartext agent session in its own long-lived git worktree.
#
# One central launcher holds all the mechanism; agents/<slug>/start.sh are thin
# wrappers that call this with their slug. Each agent gets a persistent worktree +
# branch (agent/<slug>) so its uncommitted work is physically isolated from every
# other agent — the structural fix for the shared-tree loss class (RC5).
#
# Starting in the worktree root (a real git working dir containing .claude/) also
# fixes the cwd problem: project settings load, the PostCompact hook fires, and the
# per-agent --allowedTools allowlist (agents/<slug>/allowed-tools.txt) is enforced.
#
# Usage: scripts/start-agent.sh <slug>
#
# Env overrides (mainly for tests):
#   KLARTEXT_REPO_ROOT      main checkout (default: this script's repo)
#   KLARTEXT_WORKTREE_BASE  where worktrees live (default: $HOME/klartext-worktrees)
#   KLARTEXT_NO_LAUNCH      if set, print the resolved cwd and exit instead of exec claude

set -euo pipefail

SLUG="${1:?usage: start-agent.sh <slug>}"
WAKE_PROMPT="${2:-Lies dein Postfach: bash scripts/inbox.sh read ${SLUG} — und folge der Handoff-Notiz.}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="${KLARTEXT_REPO_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
WORKTREE_BASE="${KLARTEXT_WORKTREE_BASE:-$HOME/klartext-worktrees}"
WORKTREE="$WORKTREE_BASE/$SLUG"
BRANCH="agent/$SLUG"
INBOX="$SCRIPT_DIR/inbox.sh"
ALLOWLIST="$REPO_ROOT/agents/$SLUG/allowed-tools.txt"

# 1. Provision the worktree idempotently. Never reset an existing one — its
#    uncommitted WIP and commits on agent/<slug> must survive a re-launch.
if [ ! -d "$WORKTREE" ]; then
    mkdir -p "$WORKTREE_BASE"
    if git -C "$REPO_ROOT" show-ref --verify --quiet "refs/heads/$BRANCH"; then
        git -C "$REPO_ROOT" worktree add "$WORKTREE" "$BRANCH"
    else
        git -C "$REPO_ROOT" worktree add "$WORKTREE" -b "$BRANCH" origin/main
    fi
else
    echo "→ reusing existing worktree at $WORKTREE"
fi

# 2. Bring the agent branch up to date with main (daily-restart cadence). Only when
#    the worktree is clean — never disturb uncommitted WIP. Pre-Restart commits it.
git -C "$WORKTREE" fetch origin --quiet || true
if [ -z "$(git -C "$WORKTREE" status --porcelain)" ]; then
    git -C "$WORKTREE" rebase origin/main || echo "⚠️  rebase hit conflicts in $WORKTREE — resolve manually" >&2
else
    echo "→ worktree has uncommitted changes — skipping rebase (commit WIP, then rebase)"
fi

# 3. Ensure the Python venv is reachable inside the worktree — pre-commit hooks look
#    for api/.venv/bin/tach and api/.venv/bin/semgrep relative to the worktree root.
#    Worktrees share the git object store but not the working tree, so we symlink the
#    venv from the main checkout on first provision (idempotent, skipped if present).
VENV_LINK="$WORKTREE/api/.venv"
VENV_SOURCE="$REPO_ROOT/api/.venv"
if [ -d "$VENV_SOURCE" ] && [ ! -e "$VENV_LINK" ]; then
    mkdir -p "$(dirname "$VENV_LINK")"
    ln -s "$VENV_SOURCE" "$VENV_LINK"
    echo "→ symlinked api/.venv into worktree"
fi

# 4. Surface unread inbox messages — the file-based channel for terminal sessions.
if [ -x "$INBOX" ]; then
    count="$(bash "$INBOX" unread "$SLUG")"
    echo "📬 inbox: $count unread message(s) for $SLUG"
    [ "$count" -gt 0 ] && echo "   read with: bash scripts/inbox.sh read $SLUG"
fi

# 5. Build the per-agent allowlist flags (if the agent declares one).
ALLOW_FLAGS=()
if [ -f "$ALLOWLIST" ]; then
    while IFS= read -r tool; do
        # Skip blank lines and comments.
        [ -z "$tool" ] && continue
        case "$tool" in \#*) continue ;; esac
        ALLOW_FLAGS+=(--allowedTools "$tool")
    done < "$ALLOWLIST"
fi

# 6. Resolve the tab title from the roster (team.yaml). Falls back to the slug when the
#    roster is absent or lacks the agent — the title is cosmetic, never block the launch.
#    Parsed with awk, NOT python+yaml: the roster is a fixed, flat, test-guarded format,
#    and a cosmetic title must not depend on a PyYAML install being present (a fresh CI
#    runner's system python3 has none — the bug this replaces). `|| resolved=""` keeps a
#    parse failure from aborting the launch under set -e.
TEAM_YAML="$REPO_ROOT/agents/team.yaml"
AGENT_TITLE="$SLUG"
if [ -f "$TEAM_YAML" ]; then
    resolved="$(awk -v target="$SLUG" '
        /^[[:space:]]*-?[[:space:]]*slug:[[:space:]]*/ {
            v=$0; sub(/^[^:]*:[[:space:]]*/,"",v); gsub(/[" '\'']/,"",v); cur=v
        }
        /^[[:space:]]*display:[[:space:]]*/ {
            if (cur==target) {
                d=$0; sub(/^[^:]*:[[:space:]]*/,"",d); sub(/^["'\'']/,"",d); sub(/["'\'']$/,"",d)
                print d; exit
            }
        }
    ' "$TEAM_YAML")" || resolved=""
    [ -n "$resolved" ] && AGENT_TITLE="$resolved"
fi

# Stop Claude Code from rewriting the terminal title at runtime. Official env var
# (docs: code.claude.com/docs/en/env-vars). Without it, claude overwrites whatever
# title we set with conversation-derived text, defeating the per-agent tab label.
export CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1

# 7. Launch in the worktree root: cwd = worktree → settings load, hooks fire.
cd "$WORKTREE"
if [ -n "${KLARTEXT_NO_LAUNCH:-}" ]; then
    echo "cwd=$(pwd)"
    echo "branch=$(git branch --show-current)"
    echo "allowlist-flags=${#ALLOW_FLAGS[@]}"
    echo "wake-prompt=${WAKE_PROMPT}"
    echo "disable-terminal-title=${CLAUDE_CODE_DISABLE_TERMINAL_TITLE}"
    echo "terminal-title=${AGENT_TITLE}"
    exit 0
fi

# Set the tab title once to the agent's roster display name. OSC 0 sequence works in
# Terminal.app and iTerm2; it sticks because claude no longer overwrites it (above).
printf '\033]0;%s\007' "$AGENT_TITLE"
exec claude "${ALLOW_FLAGS[@]}" "$WAKE_PROMPT"
