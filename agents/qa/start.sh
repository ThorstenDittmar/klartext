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
#
# Allowlists live in agents/qa/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" qa
