#!/bin/bash
# Narrative Expert — Agent startup script
#
# Domain: Narrative domain backend (api/*/narrative*, api/*/scene*)
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.
#
# TODO: Permissions to be finalized when Narrative Expert agent is onboarded.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Bash(source api/.venv/bin/activate && python*)" \
  --allowedTools "Bash(pytest api/tests/test_narrative* *)" \
  --allowedTools "Bash(pytest api/tests/test_scene* *)" \
  --allowedTools "Edit(api/models/narrative*)" \
  --allowedTools "Write(api/models/narrative*)" \
  --allowedTools "Edit(api/models/scene*)" \
  --allowedTools "Write(api/models/scene*)" \
  --allowedTools "Edit(api/services/narrative*)" \
  --allowedTools "Write(api/services/narrative*)" \
  --allowedTools "Edit(api/repositories/narrative*)" \
  --allowedTools "Write(api/repositories/narrative*)" \
  --allowedTools "Edit(api/routers/narratives*)" \
  --allowedTools "Write(api/routers/narratives*)" \
  --allowedTools "Edit(api/schemas/narrative*)" \
  --allowedTools "Write(api/schemas/narrative*)" \
  --allowedTools "Edit(api/exceptions/narrative*)" \
  --allowedTools "Write(api/exceptions/narrative*)" \
  --allowedTools "Edit(api/tests/test_narrative*)" \
  --allowedTools "Write(api/tests/test_narrative*)" \
  --allowedTools "Edit(api/tests/test_scene*)" \
  --allowedTools "Write(api/tests/test_scene*)" \
  --allowedTools "Edit(agents/narrative/)" \
  --allowedTools "Write(agents/narrative/)"
