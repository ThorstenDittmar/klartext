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
#
# Allowlists live in agents/system-architect/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" system-architect
