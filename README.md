# wtc-claw

An [OpenClaw](https://github.com/openclaw/openclaw) gateway for working on
[wtc](https://github.com/lcorneliussen/wtc-cli), derived from
[clawfather-boilerplate](https://github.com/lcorneliussen/clawfather-boilerplate)
and run locally with Docker Compose (`local` profile). It comes with wtc and
its OpenClaw plugin, and with the **wtc project** configured
([wtc-agent-harness](https://github.com/lcorneliussen/wtc-agent-harness)): a
conversation that says "let's work on the site" gets a collection of the
site, the CLI and whatever else the task needs.

It is also the test bed for the boilerplate: changes are tried here first
(`tools/upstream apply`), and generic fixes go back with
`tools/upstream backport`.

## Run it locally

You need Docker with Compose v2, git, bash and openssl.

```bash
git clone https://github.com/lcorneliussen/wtc-claw.git
cd wtc-claw
bin/claw deploy            # build, configure, start, wait for health
bin/claw open              # the Control UI URL, with the gateway token
```

`bin/claw deploy` generates the gateway token into `.secrets/claw.env`
(ignored by git) on its first run. Everything else is yours to provide;
nothing in this repository signs in for you:

- **Your model:** sign in with your own subscription in the Control UI,
  under Settings → Models.
- **Pushing:** connect your own GitHub account under Settings → Profile →
  GitHub connections. The wtc card pushes with it, after you confirm each
  push.
- **The wtc project's repositories:** add them with **Add repository** in
  the wtc Collection panel, starting with
  `lcorneliussen/wtc-agent-harness`, or let a conversation ask for them.
- **Optional, the project suggestion:** an OpenAI Platform API key as
  `WTC_DECISIONS_OPENAI_API_KEY` in `.secrets/claw.env` or your shell. The
  card then asks OpenAI's Decisions API which project a sent message is
  about. It reaches the gateway under that name only, so the chat model never
  uses it.

`bin/claw down` stops it. Its data lives in `.data/`, also ignored.

Inside a worktree collection the port is the collection's `WTC_CLAW_PORT`
(`.env.collection`), so every collection can run its own claw.

### Run as a collection service

The committed `.harness/dekit.tasks.yaml` defines `wtc-claw/claw` for
collections whose harness enables the dekit runtime. From the collection root:

```sh
wtc svc up wtc-claw/claw
wtc svc logs wtc-claw/claw
wtc svc down wtc-claw/claw
```

Starting it deploys the gateway with `CLAW_BUILD=auto`, then keeps Compose in
the foreground. Stopping the service stops its gateway container. Each
collection uses its allocated port and Compose project name. The first start
still needs the Docker and model setup described above. Adding the repository
or checking status does not start the service.

Tunnels stay opt-in for each collection:

```sh
wtc svc tunnel wtc-claw/claw tailscale
```

If a collection already registered `claw/main` in its local
`.wtc/svc/wtc-claw.yaml`, remove that local task when adopting the shared
definition; retain any tunnel tasks. Duplicate task names are rejected.
Collections using a custom Compose recipe should keep that local task under
a distinct service name and start only the recipe they intend to use.

`python3 -I instance/tests/shared_service_test.py` checks this service command
with a disposable Compose stub, including failed deployment rollback and
termination cleanup, without starting Docker or touching a running gateway.

### Verify an upgrade

After upgrading the pinned image or installing a matching plugin, check the
running components, not only the gateway's health endpoint:

```sh
bin/claw compose exec -T claw wtc --version
bin/claw openclaw health --json
bin/claw openclaw gateway call plugins.sessionAction --json \
  --params '{"pluginId":"wtc","actionId":"collection","agentId":"main","sessionKey":"agent:main:wtc-version-check"}'
bin/claw openclaw gateway call models.list --json
```

Confirm that the CLI and loaded wtc plugin versions match, wtc and any plugin
providing the selected model's agent runtime are loaded, and the chosen model is
available after sign-in. A healthy gateway can still have its selected agent
runtime disabled. Reload Control UI tabs after updating the plugin.

## Layout

The generic parts are the boilerplate's — see `docs/` and
`.clawfather/ownership`. What is this repository's own:

| Path | What |
|---|---|
| `instance/claw.env` | instance `wtc-claw`, local profile, collection port |
| `instance/configure.d/`, `instance/workspaces/` | the agents |
| `.clawfather/upstream.env` | the boilerplate commit this copy last took |
| `.clawfather/private-terms` | what the backport leak check refuses; terms this public repository can't name go in the ignored `.secrets/private-terms` |

Hosting profiles `azure` and `hetzner-cloudflare` are dropped
(`UPSTREAM_SKIP`).
