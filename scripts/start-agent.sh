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

# 3. Surface unread inbox messages — the file-based channel for terminal sessions.
if [ -x "$INBOX" ]; then
    count="$(bash "$INBOX" unread "$SLUG")"
    echo "📬 inbox: $count unread message(s) for $SLUG"
    [ "$count" -gt 0 ] && echo "   read with: bash scripts/inbox.sh read $SLUG"
fi

# 4. Build the per-agent allowlist flags (if the agent declares one).
ALLOW_FLAGS=()
if [ -f "$ALLOWLIST" ]; then
    while IFS= read -r tool; do
        # Skip blank lines and comments.
        [ -z "$tool" ] && continue
        case "$tool" in \#*) continue ;; esac
        ALLOW_FLAGS+=(--allowedTools "$tool")
    done < "$ALLOWLIST"
fi

# 5. Launch in the worktree root: cwd = worktree → settings load, hooks fire.
cd "$WORKTREE"
if [ -n "${KLARTEXT_NO_LAUNCH:-}" ]; then
    echo "cwd=$(pwd)"
    echo "branch=$(git branch --show-current)"
    echo "allowlist-flags=${#ALLOW_FLAGS[@]}"
    exit 0
fi
exec claude "${ALLOW_FLAGS[@]}"
