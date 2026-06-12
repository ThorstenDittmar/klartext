#!/usr/bin/env bash
# inbox.sh — file-based mailbox for klartext agents.
#
# Terminal-started agent sessions are not part of the desktop app's messaging
# fabric (no app session list, no ccd_session_mgmt tools). Cross-agent messages
# therefore travel as files in the pinned shared memory, readable by every
# session regardless of its git worktree. The semantics are unchanged from the
# app transport: the user is the channel — the recipient reads its inbox at
# session start and when the user nudges it.
#
# Usage:
#   inbox.sh send <to> <from> <subject>   # message body is read from stdin
#   inbox.sh read <slug>                  # print unread messages, then mark them read
#   inbox.sh unread <slug>                # print the unread count (for boot display)
#
# Storage (override the base with KLARTEXT_INBOX_BASE, e.g. in tests):
#   $KLARTEXT_INBOX_BASE/<slug>/        unread messages (*.md)
#   $KLARTEXT_INBOX_BASE/<slug>/.read/  read archive

set -euo pipefail

BASE="${KLARTEXT_INBOX_BASE:-$HOME/.claude/klartext-team-memory/inbox}"

usage() {
    echo "usage: inbox.sh {send <to> <from> <subject> | read <slug> | unread <slug>}" >&2
    exit 2
}

# Reduces an arbitrary string to a filename-safe slug.
slugify() {
    echo "$1" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-'
}

# Counts the unread *.md messages for a slug (0 when the inbox does not exist).
count_unread() {
    local dir="$BASE/$1"
    [ -d "$dir" ] || { echo 0; return; }
    find "$dir" -maxdepth 1 -name '*.md' -type f | wc -l | tr -d ' '
}

cmd="${1:-}"
shift || usage

case "$cmd" in
    send)
        [ $# -eq 3 ] || usage
        to="$1"; from="$2"; subject="$3"
        body="$(cat -)"
        # Empty-body guard: refuse to deliver a message with no content. An empty
        # briefing is a silent failure — the recipient sees a heading with nothing
        # under it and does double work guessing what was meant. Fail loudly, write
        # nothing. Whitespace-only counts as empty.
        if [ -z "$(printf '%s' "$body" | tr -d '[:space:]')" ]; then
            echo "error: refusing to send an empty message body (subject: $subject)" >&2
            echo "       pipe the body on stdin, e.g.: echo 'text' | inbox.sh send $to $from '$subject'" >&2
            exit 1
        fi
        dir="$BASE/$to"
        mkdir -p "$dir"
        ts="$(date -u +%Y-%m-%dT%H:%M:%S)"
        subject_slug="$(slugify "$subject")"
        subject_slug="${subject_slug:0:80}"
        file="$dir/${ts}__from-$(slugify "$from")__${subject_slug}.md"
        if ! {
            echo "# $subject"
            echo
            echo "> from: $from · to: $to · $ts UTC"
            echo
            printf '%s\n' "$body"
        } > "$file"; then
            echo "error: could not write message to $file" >&2
            exit 1
        fi
        echo "delivered: $file"
        ;;
    unread)
        [ $# -eq 1 ] || usage
        count_unread "$1"
        ;;
    read)
        [ $# -eq 1 ] || usage
        slug="$1"; dir="$BASE/$slug"; archive="$dir/.read"
        if [ "$(count_unread "$slug")" -eq 0 ]; then
            echo "(no unread messages for $slug)"
            exit 0
        fi
        mkdir -p "$archive"
        # Oldest first; the timestamp prefix sorts chronologically.
        find "$dir" -maxdepth 1 -name '*.md' -type f | sort | while read -r f; do
            echo "----------------------------------------"
            cat "$f"
            echo
            mv "$f" "$archive/"
        done
        ;;
    *)
        usage
        ;;
esac
