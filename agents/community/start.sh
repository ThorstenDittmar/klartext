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
#
# Allowlists live in agents/community/allowed-tools.txt (one entry per line),
# read by the central launcher scripts/start-agent.sh.

exec "$(dirname "$0")/../../scripts/start-agent.sh" community
