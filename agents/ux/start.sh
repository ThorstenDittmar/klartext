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

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(frontend/src/)" \
  --allowedTools "Write(frontend/src/)" \
  --allowedTools "Edit(frontend/public/)" \
  --allowedTools "Write(frontend/public/)" \
  --allowedTools "Edit(frontend/src/lib/api.ts)" \
  --allowedTools "Write(frontend/src/lib/api.ts)" \
  --allowedTools "Edit(agents/ux/)" \
  --allowedTools "Write(agents/ux/)"
