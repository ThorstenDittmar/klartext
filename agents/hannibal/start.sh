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
#
# Allowlists live in agents/hannibal/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" hannibal
