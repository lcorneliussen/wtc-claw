# shellcheck shell=sh
# wtc's collection plugin, embedded in the wtc binary the image carries
# (instance/image/Dockerfile). Instance-owned.
#
# `wtc openclaw install` installs the plugin of the wtc it runs from over an
# older one, so a newer image is picked up on the next deploy. It turns on
# custom Control UI plugins and consents to the capabilities the plugin
# declares (a panel and session actions).
wtc openclaw install >/dev/null

# The harness this claw works in. A collection starts in it when the
# repository asked for is in its registry; no defaultHarness, so a
# repository it does not list is asked about. The harness must also be a
# project on the gateway (the Collection panel's Add repository).
set_json plugins.entries.wtc.config.harnesses '[{"name":"wtc","remote":"https://github.com/lcorneliussen/wtc-agent-harness.git","ref":"main"}]'
