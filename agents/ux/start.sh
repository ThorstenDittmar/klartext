#!/bin/bash
# UX/UI Expert — Agent startup script
#
# Domain: React components, frontend (frontend/src/)
#
# Grants write access to:
#   - frontend/src/                           (alle React-Komponenten, Pages, Hooks, Styles)
#   - frontend/public/                        (statische Assets)
#   - docs/superpowers/skills/frontend.md     (eigener Skill — Self-Write)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# OE Perimeter: This file is maintained by OE only.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(frontend/src/)" \
  --allowedTools "Write(frontend/src/)" \
  --allowedTools "Edit(frontend/public/)" \
  --allowedTools "Write(frontend/public/)" \
  --allowedTools "Edit(frontend/src/lib/api.ts)" \
  --allowedTools "Write(frontend/src/lib/api.ts)" \
  --allowedTools "Edit(docs/superpowers/skills/frontend.md)" \
  --allowedTools "Write(docs/superpowers/skills/frontend.md)" \
  --allowedTools "Edit(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Write(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Edit(agents/ux/)" \
  --allowedTools "Write(agents/ux/)"
