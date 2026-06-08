#!/bin/bash
# System Architect — Agent startup script
#
# Domain: Architecture decisions, Coding Standards (CLAUDE.md, ADRs)
#
# Grants write access to:
#   - CLAUDE.md                       (coding standards, shared mit DevOps)
#   - docs/adr/                       (Architecture Decision Records)
#   - .semgrep/rules/arch/            (Architektur-Semgrep-Rules)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# OE Perimeter: This file is maintained by OE only.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(CLAUDE.md)" \
  --allowedTools "Write(CLAUDE.md)" \
  --allowedTools "Edit(docs/adr/)" \
  --allowedTools "Write(docs/adr/)" \
  --allowedTools "Edit(.semgrep/rules/arch/)" \
  --allowedTools "Write(.semgrep/rules/arch/)" \
  --allowedTools "Edit(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Write(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Edit(agents/system-architect/)" \
  --allowedTools "Write(agents/system-architect/)"
