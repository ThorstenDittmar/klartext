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

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Bash(git *)" \
  --allowedTools "Bash(gh *)" \
  --allowedTools "Bash(bash scripts/*)" \
  --allowedTools "Bash(klartext *)" \
  --allowedTools "Bash(docker *)" \
  --allowedTools "Bash(pre-commit *)" \
  --allowedTools "Bash(pip *)" \
  --allowedTools "Bash(npm *)" \
  --allowedTools "Bash(tach *)" \
  --allowedTools "Bash(ruff *)" \
  --allowedTools "Bash(pytest *)" \
  --allowedTools "Bash(mypy *)" \
  --allowedTools "Edit(.github/workflows/)" \
  --allowedTools "Write(.github/workflows/)" \
  --allowedTools "Edit(setup.sh)" \
  --allowedTools "Write(setup.sh)" \
  --allowedTools "Edit(.pre-commit-config.yaml)" \
  --allowedTools "Write(.pre-commit-config.yaml)" \
  --allowedTools "Edit(tach.toml)" \
  --allowedTools "Write(tach.toml)" \
  --allowedTools "Edit(api/pyproject.toml)" \
  --allowedTools "Write(api/pyproject.toml)" \
  --allowedTools "Edit(frontend/package.json)" \
  --allowedTools "Write(frontend/package.json)" \
  --allowedTools "Edit(frontend/package-lock.json)" \
  --allowedTools "Write(frontend/package-lock.json)" \
  --allowedTools "Edit(frontend/vite.config.ts)" \
  --allowedTools "Write(frontend/vite.config.ts)" \
  --allowedTools "Edit(frontend/tsconfig.json)" \
  --allowedTools "Write(frontend/tsconfig.json)" \
  --allowedTools "Edit(frontend/tsconfig.app.json)" \
  --allowedTools "Write(frontend/tsconfig.app.json)" \
  --allowedTools "Edit(frontend/tsconfig.node.json)" \
  --allowedTools "Write(frontend/tsconfig.node.json)" \
  --allowedTools "Edit(frontend/eslint.config.js)" \
  --allowedTools "Write(frontend/eslint.config.js)" \
  --allowedTools "Edit(api/cli.py)" \
  --allowedTools "Write(api/cli.py)" \
  --allowedTools "Edit(.claude/settings.json)" \
  --allowedTools "Write(.claude/settings.json)" \
  --allowedTools "Edit(.semgrep/)" \
  --allowedTools "Write(.semgrep/)" \
  --allowedTools "Edit(api/tests/infrastructure/)" \
  --allowedTools "Write(api/tests/infrastructure/)" \
  --allowedTools "Edit(CLAUDE.md)" \
  --allowedTools "Write(CLAUDE.md)" \
  --allowedTools "Edit(docs/)" \
  --allowedTools "Write(docs/)"
