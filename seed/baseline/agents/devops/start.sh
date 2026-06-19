#!/bin/bash
# devops agent startup — launches the session with this role's allowlist.
# Maintained by the team-formation / method role (the seed's OE-equivalent).
# Allowlist: agents/devops/allowed-tools.txt (one entry per line), read by scripts/start-agent.sh.
exec "$(dirname "$0")/../../scripts/start-agent.sh" devops
