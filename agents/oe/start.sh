#!/bin/bash
# OE — Organisationsentwicklung Agent startup script
#
# Domain: agents/ (vollständig — start.sh, claude.md, neue Verzeichnisse)
#
# OE ist alleinige Eigentümerin von agents/.
# Das schließt Start-Skripte ein — OE vergibt Permissions sorgfältig und konsistent.
#
# Read/Analyse permissions are granted project-wide in .claude/settings.json.
# DevOps Perimeter: This file is maintained by OE only.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Edit(agents/)" \
  --allowedTools "Write(agents/)" \
  --allowedTools "Edit(CLAUDE.md)" \
  --allowedTools "Write(CLAUDE.md)" \
  --allowedTools "Edit(docs/superpowers/skills/agent-onboarding.md)" \
  --allowedTools "Write(docs/superpowers/skills/agent-onboarding.md)" \
  --allowedTools "Bash(git add agents/)" \
  --allowedTools "Bash(git add CLAUDE.md)" \
  --allowedTools "Bash(git add docs/superpowers/skills/agent-onboarding.md)" \
  --allowedTools "Bash(git commit *)" \
  --allowedTools "Bash(chmod +x agents/*/start.sh)"
