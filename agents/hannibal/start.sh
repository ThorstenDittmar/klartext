#!/bin/bash
# Hannibal — Projektleiter Agent startup script
#
# Domain: Planung, Koordination, Dispatch großer Arbeitspakete
#
# Grants write access to:
#   - docs/superpowers/plans/             (Umsetzungspläne)
#   - docs/superpowers/plans/PENDING.md   (Delegations-Tracking)
#   - agents/hannibal/                    (eigenes Hoheitswissen)
#
# Explizit kein Write-Access auf:
#   - api/, frontend/, .github/ — kein operatives Tun
#   - agents/ (andere Agents) — OE-Domain
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# OE Perimeter: This file is maintained by OE only.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(docs/superpowers/plans/)" \
  --allowedTools "Write(docs/superpowers/plans/)" \
  --allowedTools "Edit(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Write(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Edit(agents/hannibal/)" \
  --allowedTools "Write(agents/hannibal/)" \
  --allowedTools "Bash(git add docs/superpowers/plans/)" \
  --allowedTools "Bash(git add agents/hannibal/)" \
  --allowedTools "Bash(git commit *)"
