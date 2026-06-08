#!/bin/bash
# QA Expert — Agent startup script
#
# Grants permissions for the QA Expert agent beyond the project baseline.
# Read/Analyse permissions are already granted project-wide in .claude/settings.json.
#
# QA Expert may write to:
#   - api/tests/                              (tests)
#   - .semgrep/rules/qa/                      (QA-owned Semgrep rules)
#   - scripts/check_test_coverage.py          (coverage script)
#   - docs/superpowers/qa-learnings/          (QA learnings docs)
#   - ~/.claude/skills/qa-review/             (QA review skill)
#   - ~/.claude/skills/qa-retro/              (QA retro skill)
#
# DevOps Perimeter: This file is maintained by DevOps only.
# To request a permission change, send a DevOps Briefing.

cd "$(dirname "$0")/../.." || exit 1

claude \
  --allowedTools "Bash(source api/.venv/bin/activate && python*)" \
  --allowedTools "Bash(python3 scripts/check_test_coverage.py*)" \
  --allowedTools "Edit(api/tests/)" \
  --allowedTools "Write(api/tests/)" \
  --allowedTools "Edit(.semgrep/rules/qa/)" \
  --allowedTools "Write(.semgrep/rules/qa/)" \
  --allowedTools "Edit(scripts/check_test_coverage.py)" \
  --allowedTools "Write(scripts/check_test_coverage.py)" \
  --allowedTools "Edit(docs/superpowers/qa-learnings/)" \
  --allowedTools "Write(docs/superpowers/qa-learnings/)" \
  --allowedTools "Edit($HOME/.claude/skills/qa-review/)" \
  --allowedTools "Write($HOME/.claude/skills/qa-review/)" \
  --allowedTools "Edit($HOME/.claude/skills/qa-retro/)" \
  --allowedTools "Write($HOME/.claude/skills/qa-retro/)" \
  --allowedTools "Edit(agents/qa/)" \
  --allowedTools "Write(agents/qa/)"
