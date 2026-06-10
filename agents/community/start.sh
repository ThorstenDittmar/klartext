#!/bin/bash
# Community Expert — Agent startup script
#
# Domain: User/community backend (api/*/user*)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.
#
# TODO: Permissions to be finalized when Community Expert agent is onboarded.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Write(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Bash(source api/.venv/bin/activate && python*)" \
  --allowedTools "Bash(pytest api/tests/test_user* *)" \
  --allowedTools "Edit(api/models/user*)" \
  --allowedTools "Write(api/models/user*)" \
  --allowedTools "Edit(api/services/user*)" \
  --allowedTools "Write(api/services/user*)" \
  --allowedTools "Edit(api/repositories/user*)" \
  --allowedTools "Write(api/repositories/user*)" \
  --allowedTools "Edit(api/routers/users*)" \
  --allowedTools "Write(api/routers/users*)" \
  --allowedTools "Edit(api/schemas/user*)" \
  --allowedTools "Write(api/schemas/user*)" \
  --allowedTools "Edit(api/exceptions/user*)" \
  --allowedTools "Write(api/exceptions/user*)" \
  --allowedTools "Edit(api/tests/test_user*)" \
  --allowedTools "Write(api/tests/test_user*)" \
  --allowedTools "Edit(agents/community/)" \
  --allowedTools "Write(agents/community/)"
