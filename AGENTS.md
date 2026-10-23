# AGENTS.md — wtc-claw

Read `README.md` first. This is a **private** derived claw; the boilerplate it
comes from is **public**.

- Values and agents live in `instance/`. Mechanisms (`bin/`, `core/`, `hosting/`,
  `tools/`, `docs/`) are upstream-owned: prefer fixing them in the
  boilerplate and taking the fix with `tools/upstream apply`.
- An edit to an upstream-owned path here is allowed when it is urgent or an
  experiment; keep it in its own commit, generic, and backport it
  (`docs/backporting.md`). `tools/upstream status` lists every divergence.
- Upgrade commits are subject `upstream: clawfather-boilerplate <sha>`.
- Nothing from this repository — names, collections, people — goes into a
  boilerplate issue, PR or commit. `tools/upstream backport` checks
  `.clawfather/private-terms` and the ignored `.secrets/private-terms`; read
  the patch anyway. This repository is public: nothing private goes into it
  either, and its own terms list only what may be public.
- Branch per task, PR into `main`, merge commit.
