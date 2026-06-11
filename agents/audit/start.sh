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
#
# Allowlists live in agents/audit/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" audit
