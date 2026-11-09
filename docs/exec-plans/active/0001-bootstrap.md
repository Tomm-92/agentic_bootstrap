---
id: '0001'
rules: [GOV-001, GOV-002, GOV-003, GOV-004, GOV-005, GOV-006, SCOPE-001, SCOPE-002, EVID-001, SEC-001, SEC-002, DATA-001, DEP-001, COST-001, MODEL-001, TOOL-001, SPEC-001, FS-001, SBX-001, VER-001, REV-001, OBS-001, QUAL-001]
scope_paths:
  - app/**
  - governance/**
  - docs/**
  - scripts/**
  - tests/**
  - ops/observability/**
  - proposals/0001/**
  - .claude/**
  - .github/**
  - .githooks/**
  - AGENTS.md
  - CLAUDE.md
  - README.md
  - ARCHITECTURE.md
  - .gitignore
  - pytest.ini
  - requirements.txt
  - requirements-dev.txt
  - requirements-dev.lock
---

# Plan 0001: governance bootstrap

## Goal

Build every governance, control and observability check that can exist before the
product agent's purpose is known, following `docs/governance_implementation.md`, in
one run. Controls are built disarmed and proposed under `proposals/0001/`. The owner
applies the proposal.

## Rules

Every rule in `governance/rules.yaml`: the IDs in the front matter.

## Inputs received

| Input | Value |
| --- | --- |
| Project name | `agentic_tools_v2` |
| Base branch | `governance_implementation` |
| Branch | `governance_bootstrap` |
| Agent package path | `app` |
| Framework | `google-adk==2.14.0` |
| Output folder | `output` |
| Planner and executor model | `claude-haiku-5-5` (`AnthropicLlm`, Anthropic API) |
| Reviewer model | `claude-sonnet-5-5` (`AnthropicLlm`, Anthropic API) |
| Telemetry backend | Local stack: collector, Tempo, Prometheus, Loki, Grafana |

No input is missing.

## Paid-model approval

Approved for the Claude API, only for the Stage 6 manual run and integration tests.
Any other paid call needs new owner approval.

## Prerequisites (2026-11-09)

| Tool | State |
| --- | --- |
| Python 3.14 | 3.14.10 in `.venv` |
| `jq`, `shasum` | present |
| `git` | 2.38.1 |
| Container runtime and Compose | running; Compose v2.15.1 |
| `actionlint`, `gitleaks`, `osv-scanner` | present |
| `ANTHROPIC_API_KEY` | **unset**: Stage 6's manual run and integration tests are deferred |
| `bwrap`, `socat` | not applicable on macOS |

The tree was clean at the start, so no uncommitted changes were carried over.
`governance_bootstrap_run1` and the stash are ignored, as instructed.

## Stages

- [x] Stage 1: on `governance_bootstrap`; `main` and the base branch unchanged; plan and ledger exist, every input recorded.
- [x] Stage 2: `governance/` committed; every value traces to the inputs or the instructions.
- [x] Stage 3: the rule catalogue and profile pass `test_rules.py`.
- [x] Stage 4: `pytest tests/governance` and existing checks pass; all hook cases pass; `test_settings.py` passes against the proposal; sandbox proof or tech-debt entry; locked files unchanged.
- [x] Stage 5: workflows pass `actionlint`; each job's command runs locally, apart from the paid call.
- [x] Stage 6: tests pass with no real model calls; one manual run, or `deferred` without the key.
- [x] Stage 7: tests pass, no network in unit tests.
- [x] Stage 8: span test passes; one fake-model session shows as a complete trace, or `deferred`.
- [x] Stage 9: QUAL-001 test passes; evidence report runs against real evidence.
- [ ] Stage 10: `check_activation.py` passes; `test_settings.py` passes; everything committed; dry run of the apply step passes.
- [ ] Stage 11: settings and hook suites pass against the proposal; final report lists every item not `pass`.

## Assumptions, decisions and risks

- **Decision (Stage 1):** the ledger is generated from the catalogue so `Control` text matches exactly.
- **Decision (Stage 2):** `.gitignore` uses `.venv` without the trailing slash. `.venv/` matches only directories, so a symlinked `.venv` (the temporary repos and the Stage 10 clone) would be committed by `git add -A`.
- **Decision (Stage 4):** `commit-msg` passes the message file to `check_trailers.sh --message`, because a commit being made isn't in any range.
- **Check (Stage 4):** hook tests were mutation-checked by hand: disabling the hash-change block, path normalising, the push denial, the no-verify denial and per-commit parent comparison each made tests fail.
- **Risk (Stage 4):** the sandbox can't be proven inside this run. Its configuration is tested; the behaviour is step 7's check.
- **Decision (Stage 5):** `ai-review.yml` skips every step while `ANTHROPIC_API_KEY` isn't a repo secret, so merging the proposal alone starts no paid calls. The review logic is `scripts/ai_review.py`, tested with a stub client. Its model comes from `allowlists/models.yaml`. The model was never called, because the paid-model approval doesn't cover this workflow.
- **Decision (Stage 5):** no refusal fallback, although the Anthropic API guidance recommends one by default. The instructions forbid it (MODEL-001).
- **Risk (Stage 5):** `ai-review.yml` runs the PR's own `scripts/ai_review.py` with the API key available. GitHub withholds secrets from forks, and there's one author, so this is acceptable until the repo gains collaborators.
- **Decision (Stage 6):** the layer is `app/governance.py`, attached with `App(plugins=[...])` in `app/agent.py`. Token counts live in session state through `callback_context.state`, so they land on the model response event and persist across runs.
- **Deployment without git (Stage 6):** `governance_hash` needs `git` and a checkout. A deployment without them must compute `git rev-parse HEAD:governance` at image build, bake it into the image with `governance/`, and change `governance_hash` to return that value. Not built: nothing deploys yet.
- **Deferred (Stage 6):** `ANTHROPIC_API_KEY` is unset, so the manual run and integration tests didn't run: `.venv/bin/python -m scripts.local_session "What is the status of demo?"`, then `.venv/bin/pytest -m integration`. Token counting has only seen ADK's offline conversion of an Anthropic `Message`.
- **DEP-001 for review (Stage 6):** `google-adk[db]` added these to the lock: alembic==1.20.1 google-api-core==2.44.0 google-cloud-core==2.8.0 google-cloud-monitoring==2.32.0 google-cloud-spanner==3.71.0 googleapis-common-protos==1.76.0 greenlet==3.5.6 grpc-google-iam-v1==0.14.6 grpc-interceptor==0.15.4 grpcio==1.85.1 grpcio-status==1.85.1 Mako==1.4.3 MarkupSafe==3.0.4 mmh3==5.3.1 opentelemetry-resourcedetector-gcp==1.14.0 proto-plus==1.29.0 protobuf==7.36.2 SQLAlchemy==2.1.8 sqlalchemy-spanner==1.20.1 sqlparse==0.6.1 
- **Decision (Stage 7):** the governance log is session state, one key per decision (`governance_log:<call ID>:<result>`), because parallel tool calls would overwrite a shared list. It's stored on the events, so the durable session log holds it. A call waiting on a human logs nothing until the answer comes back through the policy as `confirmed` or `rejected`.
- **Check (Stage 8):** the Docker daemon was running, so the end-to-end check ran rather than being deferred, using the `--fake` model with no paid calls. Tempo returned the complete trace (trace `7153a67e271ba3da308613d64ea17a95`) with every invariant attribute, Prometheus held `governance_session_tokens` and loaded the three alert rules (`promtool check rules` passes), Loki received logs, and Grafana's three data sources and the dashboard were healthy. The stack was then stopped and its volumes removed. Tempo search took about 30 seconds to show a new trace.
- **Decision (Stage 8):** Stage 8's own acceptance criterion starts the local stack, so it's the stated exception to "never start services".
- **Decision (Stage 8):** Tempo's config comes from the v3.1.1 single-binary example, without its metrics generator (a remote-write path) and MCP server. Collector exporters use `otlp_grpc` and `otlp_http`, because the collector warns that `otlp` and `otlphttp` are deprecated aliases.
- **DEP-001 for review (Stage 8):** `google-adk[otel]` added these to the lock: opentelemetry-exporter-http-transport==0.66b2 opentelemetry-exporter-otlp-common==0.66b2 opentelemetry-exporter-otlp-proto-common==1.45.2 opentelemetry-exporter-otlp-proto-http==1.45.2 opentelemetry-instrumentation==0.66b2 opentelemetry-instrumentation-google-genai==1.3b0 opentelemetry-instrumentation-grpc==0.66b2 opentelemetry-instrumentation-httpx==0.66b2 opentelemetry-proto==1.45.2 opentelemetry-util-genai==1.3b0 opentelemetry-util-http==0.66b2 wrapt==2.5.2 
