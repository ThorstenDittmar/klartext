#!/usr/bin/env bash
# check-compact-log.sh — Compact-Monitor für klartext
#
# Prüft .claude/compact-log.txt auf neue "| auto |"-Einträge seit dem letzten Lauf
# und sendet eine macOS-Notification als nachlaufendes Feedback-Signal.
#
# Wird via launchd stündlich ausgeführt (macOS-only — auf Linux/Codespace kein launchd).
# Installation: setup.sh registriert die launchd-Agent-Plist.
#
# State: .claude/compact-log-lastcheck speichert die zuletzt geprüfte Zeilennummer.
# Digest: .claude/compact-monitor-digest.txt — lesbar für OE beim Session-Start.

set -euo pipefail

# Repo-Verzeichnis ist der erste Parameter (wird vom Plist gesetzt)
REPO_DIR="${1:-$(pwd)}"
LOG_FILE="$REPO_DIR/.claude/compact-log.txt"
STATE_FILE="$REPO_DIR/.claude/compact-log-lastcheck"
DIGEST_FILE="$REPO_DIR/.claude/compact-monitor-digest.txt"

# Log existiert noch nicht → nichts zu tun
if [ ! -f "$LOG_FILE" ]; then
    exit 0
fi

CURRENT_LINES=$(wc -l < "$LOG_FILE")
LAST_CHECKED=0

if [ -f "$STATE_FILE" ]; then
    LAST_CHECKED=$(cat "$STATE_FILE")
fi

# Keine neuen Zeilen
if [ "$CURRENT_LINES" -le "$LAST_CHECKED" ]; then
    echo "$CURRENT_LINES" > "$STATE_FILE"
    exit 0
fi

# Neue Zeilen seit letztem Check auf auto-Einträge prüfen.
# `grep -c` zählt Treffer; bei null Treffern liefert grep Exit 1, was unter
# `set -euo pipefail` das Skript abbrechen würde (State bliebe stehen) — daher
# `|| true`, damit "keine auto-Compacts" ein regulärer 0-Fall ist, kein Fehler.
NEW_AUTO=$(tail -n +"$((LAST_CHECKED + 1))" "$LOG_FILE" | grep -c "| auto |" || true)

# State aktualisieren
echo "$CURRENT_LINES" > "$STATE_FILE"

# Keine neuen auto-Compacts → fertig
if [ "$NEW_AUTO" -eq 0 ]; then
    exit 0
fi

# Digest schreiben
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")
echo "$TIMESTAMP — $NEW_AUTO Auto-Compact(s) seit letzter Prüfung" >> "$DIGEST_FILE"

# macOS-Notification
osascript -e "display notification \"$NEW_AUTO Auto-Compact(s) seit letzter Prüfung. Signal: künftig früher proaktiv komprimieren. Prüfen, ob etwas zu sichern war.\" with title \"klartext — Auto-Compact erkannt\""
