#!/bin/bash
# System Architect — Agent startup script
#
# Domain: Architecture decisions, Coding Standards (CLAUDE.md, ADRs)
#
# Grants write access to:
#   - CLAUDE.md                       (coding standards, shared mit DevOps)
#   - docs/adr/                       (Architecture Decision Records)
#   - docs/superpowers/skills/        (projekt-spezifische Skills)
#   - .semgrep/rules/arch/            (Architektur-Semgrep-Rules)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.
#
# TODO: Permissions to be finalized when System Architect agent is onboarded.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Write(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Edit(CLAUDE.md)" \
  --allowedTools "Write(CLAUDE.md)" \
  --allowedTools "Edit(docs/adr/)" \
  --allowedTools "Write(docs/adr/)" \
  --allowedTools "Edit(docs/superpowers/skills/)" \
  --allowedTools "Write(docs/superpowers/skills/)" \
  --allowedTools "Edit(.semgrep/rules/arch/)" \
  --allowedTools "Write(.semgrep/rules/arch/)" \
  --allowedTools "Edit(agents/system-architect/)" \
  --allowedTools "Write(agents/system-architect/)"
