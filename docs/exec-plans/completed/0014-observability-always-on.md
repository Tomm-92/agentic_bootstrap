---
id: '0014'
rules: [SCOPE-001, SCOPE-002, OBS-001, DATA-001]
scope_paths:
  - ops/observability/docker-compose.yaml
  - ops/observability/README.md
  - ops/observability/observability.svg
  - tests/governance/test_observability.py
  - docs/exec-plans/**
---

# Plan 0014: keep the telemetry stack running between sessions

Ported from plan 0009 of `agentic_tools_v2` (commit `20b9b93`), not cherry-picked.

## Goal

A session the owner can observe takes two manual steps every time. First,
`docker compose -f ops/observability/docker-compose.yaml up -d` must have been run
since Docker last started. Second, `OTEL_EXPORTER_OTLP_ENDPOINT` must be set in the
terminal that starts `adk web`. If either is missed, nothing warns the owner, and that
run has no traces.

Make both one-time setup:

- **Containers.** Give every service in the compose file `restart: unless-stopped`.
  Docker then restarts the stack whenever its daemon starts. The stack stays down only
  after an explicit `docker compose stop` or `down`.
- **Endpoint.** `adk web` sets up its exporters once, at server start, and only when an
  `OTEL_EXPORTER_OTLP_*` variable is already in its environment (`_setup_telemetry` in
  `google/adk/cli/api_server.py`). The agent's `.env` is loaded later, so it cannot
  carry the variable. The owner exports it from their shell profile: an owner action.

## Evidence

- The compose file and `test_compose_service_is_pinned_and_local` match
  `agentic_tools_v2` before `20b9b93`. `collector.yaml`, `grafana/` and
  `governance/thresholds.yaml` match too.
- This project is pre-A01, so the source README and diagram don't fit as-is. Here there
  is no `app/workflows.py` or `scripts/eval_pass_rate.py`, so no `governance.verify.runs`
  or `governance.eval.pass_rate` metric, no `EvalPassRateDrop` or
  `FirstPassVerifyRateLow` alert, and no `work_item`, `intent.sha` or `verify.*` span
  attributes. Nothing sets `failure.source = sandbox` yet.

## Checklist

- [x] In `ops/observability/docker-compose.yaml`, add `restart: unless-stopped` to all
      five services: collector, tempo, prometheus, loki and grafana. Change nothing
      else.
- [x] In `tests/governance/test_observability.py`, extend
      `test_compose_service_is_pinned_and_local` to assert
      `service['restart'] == 'unless-stopped'`. Prove it can fail by removing the key
      from one service, running the test, and restoring the key.
- [x] `docker compose ... config -q` passes, and
      so do the unit and governance test suites, ruff, mypy and vulture.
- [x] Write `ops/observability/README.md` from the source README, cut to what this
      project emits: three alerts, four metrics, no work-item attributes.
- [x] Draw `ops/observability/observability.svg` from the source diagram, without the
      verify step and eval script, legible on GitHub's light and dark themes.

## Decisions

- Restart policy, not a wrapper script around `adk web`: nothing to remember per run.
- No in-repo `.env` or `.envrc` for the endpoint: ADK loads it too late, and SEC-001
  keeps agents out of `.env` files.
- SVG next to the README, as plan 0002 did, so GitHub renders it and it diffs as text.
- Adapt the README and diagram rather than copy them, so they describe only what exists.
  Phases A02 to A04 add the missing rows when they add the telemetry.

## Risks

- When the endpoint is set but the stack is down, the exporter logs connection errors
  and the run's traces are lost. Same as today, so no guard is added.
- The README and diagram copy facts from `ARCHITECTURE.md` and the stack config, so
  they go stale when those change. The README names them as the source of truth.
- The containers use memory between sessions. `docker compose stop` stops them.
- The diagram hasn't been rendered: the sandbox blocks headless browsers.
- `agentic_tools_v2` uses the same ports, so only one stack runs at a time. Both
  projects send to whichever is running.

## Owner actions

1. Add `export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318` to `~/.zshrc`, then
   open a new terminal. Per machine: skip if already done for `agentic_tools_v2`.
2. In Docker Desktop's settings, turn on "Start Docker Desktop when you sign in".
3. From your own terminal: in `agentic_tools_v2`, run
   `docker compose -f ops/observability/docker-compose.yaml stop`; here, run
   `docker compose -f ops/observability/docker-compose.yaml up -d`.
4. Check: restart Docker Desktop, then `curl -s localhost:3200/ready` without running
   `up`. Run `adk web .`, send one message, and find its trace in Grafana
   (http://localhost:3000, Explore → Tempo, `{ span.session.id = "<session ID>" }`).
5. View the diagram on GitHub in light and dark themes.
