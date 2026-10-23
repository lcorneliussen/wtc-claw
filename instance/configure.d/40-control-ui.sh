# shellcheck shell=sh
# Control UI preferences of this deployment. Instance-owned.

# No community invitation (Reddit, Discord, X) in the sidebar.
set_json gateway.controlUi.communityInvite 'false'
