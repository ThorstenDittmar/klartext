#!/bin/bash
# OE — Organisationsentwicklung Agent startup script
#
# Domain: agents/ (vollständig — start.sh, claude.md, neue Verzeichnisse)
#
# OE ist alleinige Eigentümerin von agents/.
# Das schließt Start-Skripte ein — OE vergibt Permissions sorgfältig und konsistent.
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by OE only.
#
# Allowlists live in agents/oe/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" oe
