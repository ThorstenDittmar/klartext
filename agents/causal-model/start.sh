#!/bin/bash
# Causal Model Expert — Agent startup script
#
# Domain: Wirkgefüge backend (api/*/causal_model*, api/*/slot*)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.
#
# TODO: Permissions to be finalized when Causal Model Expert agent is onboarded.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Write(docs/superpowers/plans/PENDING.md)" \
  --allowedTools "Bash(source api/.venv/bin/activate && python*)" \
  --allowedTools "Bash(pytest api/tests/test_causal_model* *)" \
  --allowedTools "Bash(pytest api/tests/test_slot* *)" \
  --allowedTools "Bash(pytest api/tests/test_causal_relation* *)" \
  --allowedTools "Edit(api/models/causal_model*)" \
  --allowedTools "Write(api/models/causal_model*)" \
  --allowedTools "Edit(api/models/causal_relation*)" \
  --allowedTools "Write(api/models/causal_relation*)" \
  --allowedTools "Edit(api/models/slot*)" \
  --allowedTools "Write(api/models/slot*)" \
  --allowedTools "Edit(api/services/causal_model*)" \
  --allowedTools "Write(api/services/causal_model*)" \
  --allowedTools "Edit(api/repositories/causal_model*)" \
  --allowedTools "Write(api/repositories/causal_model*)" \
  --allowedTools "Edit(api/routers/causal_model*)" \
  --allowedTools "Write(api/routers/causal_model*)" \
  --allowedTools "Edit(api/schemas/causal_model*)" \
  --allowedTools "Write(api/schemas/causal_model*)" \
  --allowedTools "Edit(api/exceptions/causal_model*)" \
  --allowedTools "Write(api/exceptions/causal_model*)" \
  --allowedTools "Edit(api/tests/test_causal_model*)" \
  --allowedTools "Write(api/tests/test_causal_model*)" \
  --allowedTools "Edit(agents/causal-model/)" \
  --allowedTools "Write(agents/causal-model/)"
