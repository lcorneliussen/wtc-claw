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
