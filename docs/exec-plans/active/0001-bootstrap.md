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
- [ ] Stage 3: the rule catalogue and profile pass `test_rules.py`.
- [ ] Stage 4: `pytest tests/governance` and existing checks pass; all hook cases pass; `test_settings.py` passes against the proposal; sandbox proof or tech-debt entry; locked files unchanged.
- [ ] Stage 5: workflows pass `actionlint`; each job's command runs locally, apart from the paid call.
- [ ] Stage 6: tests pass with no real model calls; one manual run, or `deferred` without the key.
- [ ] Stage 7: tests pass, no network in unit tests.
- [ ] Stage 8: span test passes; one fake-model session shows as a complete trace, or `deferred`.
- [ ] Stage 9: QUAL-001 test passes; evidence report runs against real evidence.
- [ ] Stage 10: `check_activation.py` passes; `test_settings.py` passes; everything committed; dry run of the apply step passes.
- [ ] Stage 11: settings and hook suites pass against the proposal; final report lists every item not `pass`.

## Assumptions, decisions and risks

- **Decision (Stage 1):** the ledger is generated from the catalogue so `Control` text matches exactly.
