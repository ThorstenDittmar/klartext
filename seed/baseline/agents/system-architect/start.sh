#!/bin/bash
# system-architect agent startup — launches the session with this role's allowlist.
# Maintained by the team-formation / method role (the seed's OE-equivalent).
# Allowlist: agents/system-architect/allowed-tools.txt (one entry per line), read by scripts/start-agent.sh.
exec "$(dirname "$0")/../../scripts/start-agent.sh" system-architect
