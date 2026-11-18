---
id: '0016'
rules: [SCOPE-001, SCOPE-002, OBS-001, EVID-001]
scope_paths:
  - ops/observability/README.md
  - ops/observability/docker-compose.yaml
  - tests/governance/test_observability.py
  - docs/exec-plans/**
---

# Plan 0016: give the stack its own name, and document the checks that prove it works

## Goal

On 18 Nov 2026 the owner checked plans 0014 and 0015 end to end against the live stack.
That turned up one fault and three gaps in `ops/observability/README.md`.

**Fault: this stack and `agentic_tools_v2`'s are one Compose project.** Neither compose
file sets `name:`, so Compose names both after their directory, `observability`. The
owner's `docker compose ls -a` shows a single `observability` project, last started from
this repo. `docker volume ls` shows one each of `observability_grafana-data`,
`observability_loki-data`, `observability_prometheus-data` and
`observability_tempo-data`. So:

- Both projects' traces, metrics, logs and Grafana settings go into the same volumes,
  and a TraceQL search can't tell which project a trace came from.
- `up -d` in either repo silently replaces the containers the other started, with that
  repo's config.

Fix: set a project name in this repo's compose file. Only one side needs to change for
the two to separate.

**Gaps in the README:**

1. **The endpoint must be set in the terminal that runs `adk web`.** `~/.zshrc` exported
   `OTEL_EXPORTER_OTLP_ENDPOINT`, but a shell started before that edit didn't have it.
   `adk web` started from such a terminal, including VS Code's integrated terminal,
   emits no traces and gives no warning. The README says "open a new terminal" but gives
   no way to check it.
2. **The stack must come back after Docker restarts.** Lines 110–112 say it should. The
   owner checked it by restarting Docker Desktop and running
   `curl -s localhost:3200/ready` without `up`, and it printed `ready`. The README
   doesn't give this check.
3. **Only one stack can run at a time.** `agentic_tools_v2` binds the same ports (4317,
   4318, 3000, 3100, 3200, 9090), and both projects send to whichever stack is running.
   This is only in plan 0014's risks and owner actions.

## Checklist

- [ ] `ops/observability/docker-compose.yaml`: add a top-level
      `name: agentic_bootstrap-observability`. Change nothing else.
- [ ] `tests/governance/test_observability.py`: add a test that
      `COMPOSE['name'] == 'agentic_bootstrap-observability'`. Prove it can fail by
      removing the key, running the test, and restoring the key.
- [ ] `docker compose -f ops/observability/docker-compose.yaml config -q` passes.
- [ ] README, "One-time setup", after the `~/.zshrc` step: check the variable with
      `echo $OTEL_EXPORTER_OTLP_ENDPOINT`, and say that terminals opened before the
      edit, including VS Code's integrated terminal, don't have it until reopened.
- [ ] README, after the `restart: unless-stopped` paragraph (lines 110–112): give the
      check. Restart Docker Desktop, then run `curl -s localhost:3200/ready` without
      `up`. It prints `ready`.
- [ ] README: add a short note that the stack is the Compose project
      `agentic_bootstrap-observability`, with its own volumes. If `up` fails with "port
      is already allocated", another stack holds the ports (4317, 4318, 3000, 3100,
      3200, 9090), for example one from another project with the same setup. Stop that
      stack first. Name no other project.
- [ ] Change nothing else in the README. Keep its style: short sentences, numbered
      steps, `sh` code blocks.
- [ ] The unit and governance test suites pass, as do ruff, mypy and vulture.

## Decisions

- Rename this repo's project, not `agentic_tools_v2`'s. That keeps the change inside
  this repo's governance. `agentic_tools_v2` keeps `observability` and the existing
  volumes.
- Leave the existing `observability_*` volumes alone. They hold both projects' history,
  which EVID-001 keeps for 90 days (`docs/SECURITY.md` names the stack's Docker
  volumes). This repo starts with empty volumes, so its earlier traces, including the
  owner's 18 Nov check of session `f47619ce-dfe7-40a2-b78b-2683d35cb149`, stay in the
  old volumes. `agentic_tools_v2`'s stack can still show them.
- Keep the shared ports. Separate ports would need a different
  `OTEL_EXPORTER_OTLP_ENDPOINT` per project, which `~/.zshrc` sets once per machine.
  With separate project names, a port clash makes `up` fail loudly instead of silently
  taking over the other stack.
- The README names no other project. Which projects share this machine is the owner's
  setup, not this repo's, so the note covers any stack on the same ports.
- Session-database checks from plan 0015 stay in `docs/REVIEW.md` and
  `docs/SECURITY.md`, which already cover them.

## Risks

- After the rename, `observability`'s containers keep running and hold the ports until
  stopped, so this repo's `up -d` fails. That is the first owner action.
- None from the README note: it names no other project, so it doesn't go stale when
  one changes.

## Owner actions

1. Start a new session to implement this plan (one plan per session, GOV-006).
2. After it's committed, from your own terminal, in this repo:

   ```sh
   docker compose -p observability stop
   docker compose -f ops/observability/docker-compose.yaml up -d
   docker compose ls -a
   ```

   `docker compose ls -a` should list `agentic_bootstrap-observability` as running(5)
   and `observability` as exited. Grafana starts with fresh data, so the first login is
   admin/admin again.
3. Rerun the end-to-end check: one `adk web` session, then find its trace in Tempo.
