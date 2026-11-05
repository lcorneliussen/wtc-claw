# shellcheck shell=sh
# The agents of this deployment. Instance-owned; the boilerplate ships one.
#
# Every agent is an entry here plus a directory under instance/workspaces/ with the
# same id. `bin/claw sync-workspaces` copies the instruction files there.
set_json agents.defaults.skipBootstrap 'true'
# Write only instance-owned leaves, preserving the selected model and custom fields.
set_str 'agents.entries["main"].name' 'Team Claw'
set_str 'agents.entries["main"].workspace' '/home/node/.openclaw/workspaces/main'
set_str 'agents.entries["main"].identity.name' 'Team Claw'
set_str 'agents.entries["main"].identity.emoji' '🦞'

# Bundled skills the core image supports (GitHub CLI).
set_json 'skills.entries["github"].enabled' 'true'
set_json 'skills.entries["gh-issues"].enabled' 'true'
