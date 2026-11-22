# Telemetry stack

The local stack that records what the product agent does in each session: which model
and tool calls it made, what the governance layer decided, and what each call cost.

![Telemetry data flow from the agent to the collector, then to Tempo, Prometheus and Loki, and Grafana](observability.svg)

The source of truth is the code and config below. This page copies facts from them, so
check them when it and they disagree:

- [`ARCHITECTURE.md`](../ARCHITECTURE.md), "Telemetry invariants": the required span
  attributes (OBS-001)
- [`app/governance.py`](../app/governance.py): `GovernancePlugin`, which sets them
- [`collector.yaml`](collector.yaml): where each signal goes (DATA-001)
- [`alerts.yaml`](alerts.yaml): the alert rules

## What is observed

### Spans (Tempo)

| Span | Carries | Lets you answer |
| --- | --- | --- |
| Every model and tool span | `session.id`, `user.id`, `governance.sha`, `guardrail.result` | Which session and user made this call, under which rules, and what the guardrail decided |
| `governance.model_call` | `model.id`, `tokens.input`, `tokens.output`, `latency.ms` | Which model ran, what it cost in tokens and how long it took |
| `execute_tool <name>` | `tool.name`, `tool.tier` | Which tool ran, and at what tier in `governance/tools.yaml` |

`guardrail.result` is `allowed`, `denied`, `waiting` (a confirmation is pending),
`confirmed` or `rejected` on tool spans, and `allowed` or `refused` on model spans.

On an error, a span also carries `failure.source`, so a failure is attributed rather
than guessed at:

| Value | Set when |
| --- | --- |
| `model` | The model call raised an error |
| `harness` | The model's response had no token count |
| `tool` | The tool raised an error |
| `policy` | A tool was denied, or the session was over its token budget |

Phase A02 adds `sandbox`, and phase A04 adds the work-item attributes `intent.sha`,
`work_item` and `verify.gate`.

### Metrics (Prometheus)

The collector sends metrics to Prometheus over OTLP, which renames them: dots become
underscores and counters gain `_total`. So `governance.tool_calls.blocked` is queried as
`governance_tool_calls_blocked_total`. `GovernancePlugin` emits all four.

| Metric | Lets you catch |
| --- | --- |
| `governance.tool_calls.blocked` (`tool.name`, `rule`) | Which rule is blocking which tool, and how often |
| `governance.confirmations` (`outcome`: asked, approved, rejected) | Whether confirmations still get read, or are approved on reflex |
| `governance.budget_refusals` | Sessions stopped by `session_token_budget` |
| `governance.session_tokens` (gauge, `session.id`) | Sessions heading for their budget |

### Alerts (Prometheus)

| Alert | Fires when | Suggests |
| --- | --- | --- |
| `BlockedToolCallsRising` | Blocked calls in the last hour more than doubled on the same hour yesterday, and are over 5 | The agent is trying something new that policy refuses |
| `ApprovalRateNearTotal` | Over 95% of at least 20 confirmations in a day were approved | Consent fatigue: confirmations are no longer read |
| `SessionTokenSpike` | A session has used over 150,000 tokens, 75% of `session_token_budget` | A run is looping or reading too much |

There is no Alertmanager, so alerts notify nobody. See them at
<http://localhost:9090/alerts>.

### Logs (Loki)

ADK's own GenAI log events for each model call. Each carries the trace ID of the call
that emitted it.

## How it works

1. `adk web` sets up OpenTelemetry exporters once, at server start, and only when an
   `OTEL_EXPORTER_OTLP_*` variable is already in its environment (`_setup_telemetry` in
   `google/adk/cli/api_server.py`). The agent's `.env` is loaded later, so it cannot
   carry the variable.
2. `GovernancePlugin` opens a `governance.model_call` span around each model call, adds
   attributes to ADK's `execute_tool` span on each tool call, and records the metrics
   above. ADK emits the log events.
3. Everything goes over OTLP/HTTP to the collector on port 4318. The collector batches
   it and runs one pipeline per signal: traces to Tempo, metrics to Prometheus and logs
   to Loki. Its exporters must match `telemetry_exporters` in
   `governance/allowlists/services.yaml` (DATA-001, tested by
   [`tests/governance/test_observability.py`](../tests/governance/test_observability.py)).
4. Grafana reads all three stores. Its datasources and the Governance dashboard are
   provisioned from [`grafana/`](grafana/).

Every port is bound to 127.0.0.1, and every image is pinned to a version.

## Running it

Run docker from your own terminal: the Claude Code sandbox blocks it.

One-time setup:

1. Add this line to `~/.zshrc`, then open a new terminal:

   ```sh
   export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
   ```

   Check it in the terminal that will run `adk web`:

   ```sh
   echo $OTEL_EXPORTER_OTLP_ENDPOINT
   ```

   It prints `http://localhost:4318`. Terminals opened before the edit, including VS
   Code's integrated terminal, don't have it until you reopen them. `adk web` started
   from one of them sends no traces and gives no warning.

2. In Docker Desktop's settings, turn on "Start Docker Desktop when you sign in".
3. Start the stack:

   ```sh
   docker compose -f observability/compose.yaml up -d
   ```

Every service has `restart: unless-stopped`, so from then on the stack starts whenever
Docker does. It stays down only after `docker compose stop` or `down`, until you start
it again. While it runs it holds memory between sessions.

To check, restart Docker Desktop, then, without running `up`:

```sh
curl -s localhost:3200/ready
```

It prints `ready`.

The stack is the Compose project `agentic_bootstrap-observability`, with its own
volumes. Only one stack can hold its ports (4317, 4318, 3000, 3100, 3200, 9090). If `up`
fails with "port is already allocated", another stack holds them, for example one from
another project with the same setup. Stop that stack first.

If the endpoint is set but the stack is down, the exporter logs connection errors, the
session still runs, and its telemetry is lost.

Check it is up:

```sh
curl -s localhost:3200/ready
```

### Finding a session's trace

1. Run `adk web .` and send a message. Note the session ID in the web UI.
2. Open Grafana at <http://localhost:3000>. The first login is admin/admin.
3. For an overview, open Dashboards → Governance. Its "Recent traces" panel lists the
   latest traces.
4. For one session, open Explore, choose Tempo, and search with TraceQL:

   ```text
   { span.session.id = "<session ID>" }
   ```

5. Open the trace. Each `governance.model_call` and `execute_tool` span shows the
   attributes above. Look for `failure.source` on any span that errored.
