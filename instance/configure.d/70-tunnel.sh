# shellcheck shell=sh
# A local tunnel in front of the gateway (`wtc svc tunnel claw tailscale`).
# Instance-owned.
#
# The tunnel reaches the gateway through Docker's port forward, so its
# requests arrive from the claw network's gateway address with forwarded
# headers. Without trusting exactly that address the gateway refuses them.
# Token auth still applies. Set CLAW_TUNNEL_PROXY in .secrets/claw.env (it is
# per machine); unset, nothing changes.
if [ -n "${CLAW_TUNNEL_PROXY:-}" ]; then
  set_json gateway.trustedProxies "$(json '[a[0]]' "$CLAW_TUNNEL_PROXY")"
fi
