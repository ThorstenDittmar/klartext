#!/bin/bash
# Audit Expert — Agent startup script
#
# Domain: Verification procedures, claim extraction (api/providers/, api/*/claim*)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.
#
# TODO: Permissions to be finalized when Audit Expert agent is onboarded.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Bash(source api/.venv/bin/activate && python*)" \
  --allowedTools "Bash(pytest api/tests/test_claim* *)" \
  --allowedTools "Bash(pytest api/tests/test_claude_* *)" \
  --allowedTools "Edit(api/providers/)" \
  --allowedTools "Write(api/providers/)" \
  --allowedTools "Edit(api/models/claim*)" \
  --allowedTools "Write(api/models/claim*)" \
  --allowedTools "Edit(api/services/claim*)" \
  --allowedTools "Write(api/services/claim*)" \
  --allowedTools "Edit(api/services/narrative_analysis*)" \
  --allowedTools "Write(api/services/narrative_analysis*)" \
  --allowedTools "Edit(api/repositories/claim*)" \
  --allowedTools "Write(api/repositories/claim*)" \
  --allowedTools "Edit(api/routers/claims*)" \
  --allowedTools "Write(api/routers/claims*)" \
  --allowedTools "Edit(api/schemas/claim*)" \
  --allowedTools "Write(api/schemas/claim*)" \
  --allowedTools "Edit(api/exceptions/claim*)" \
  --allowedTools "Write(api/exceptions/claim*)" \
  --allowedTools "Edit(api/tests/test_claim*)" \
  --allowedTools "Write(api/tests/test_claim*)" \
  --allowedTools "Edit(api/tests/test_claude_*)" \
  --allowedTools "Write(api/tests/test_claude_*)" \
  --allowedTools "Edit(agents/audit/)" \
  --allowedTools "Write(agents/audit/)"
