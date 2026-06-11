#!/bin/bash
# DevOps — Agent startup script
#
# Domain: Infrastructure, CI/CD, Tooling — Gatekeeper
#
# Grants write access to the full Infrastructure Perimeter:
#   - .github/workflows/          (CI/CD pipelines)
#   - setup.sh                    (bootstrap script)
#   - .pre-commit-config.yaml     (pre-commit hooks)
#   - tach.toml                   (layer enforcement)
#   - api/pyproject.toml          (Python dependencies + tools)
#   - frontend/package.json       (Node dependencies)
#   - frontend/package-lock.json  (Node lockfile)
#   - frontend/vite.config.ts     (build config)
#   - frontend/tsconfig*.json     (TypeScript config)
#   - frontend/eslint.config.js   (frontend linting)
#   - api/cli.py                  (klartext CLI)
#   (agents/ is OE domain — OE owns all agent start scripts and knowledge files)
#   - .claude/settings.json       (base permissions)
#   - .semgrep/                   (Semgrep rules)
#   - api/tests/infrastructure/   (infrastructure tests)
#   - CLAUDE.md                   (coding standards)
#   - docs/                       (developer documentation)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
#
# Allowlists live in agents/devops/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" devops
