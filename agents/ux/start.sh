#!/bin/bash
# UX/UI Expert — Agent startup script
#
# Domain: React components, frontend (frontend/src/)
#
# Grants write access to:
#   - frontend/src/     (alle React-Komponenten, Pages, Hooks, Styles)
#   - frontend/public/  (statische Assets)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.
#
# TODO: Permissions to be finalized when UX/UI agent is onboarded.
#
# Allowlists live in agents/ux/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" ux
