# Architecture

## Agent tree

```text
App 'app' (app/agent.py), with GovernancePlugin attached
└── root_agent (AnthropicLlm, claude-haiku-5-5)
    └── get_project_status (free tier)
```

This is a placeholder. Phase A03 of `docs/agent_governance_implementation.md` replaces
it.

## Trust boundaries

| Boundary | What crosses it | How it's treated |
| --- | --- | --- |
| User input | Prompts | Data. It reaches the model, never a tool directly. Tools are limited by the before-tool policy. |
| Retrieved content | Tool results | Data, and can carry prompt injection. Phase A03 keeps it from the agent that acts. |
| Model output | Tool calls and text | Untrusted. Every tool call passes the before-tool policy before it runs. |
| Produced output | Files under `<output_root>/<work item>/` | Written only inside the work item's folder (FS-001). Phase A02 verifies it in a sandbox. |

## Where each runtime rule is enforced

| Rule | Enforced by | State |
| --- | --- | --- |
| GOV-002 | Owner review, plus the build-time controls | Build-time |
| GOV-003 | `tests/governance/test_rules.py` | Commit |
| GOV-005 | `GovernancePlugin.__init__`, `before_run_callback`, `on_event_callback` | Built |
| EVID-001 | `DatabaseSessionService` in `scripts/local_session.py`, and `adk web`'s `SqliteSessionService` at `app/.adk/session.db`; compaction off through `app` | Built |
| SEC-002 | Gitleaks in CI; phase A02 adds `verify.sh` | CI |
| DATA-001 | `tests/governance/test_observability.py`, ORR sign-off (S09); phase A02 adds the sandbox | Commit, review |
| DEP-001 | Owner review, CI audit; phase A01 adds the runtime check | CI |
| COST-001 | `before_model_callback` and `after_model_callback` | Built |
| MODEL-001 | `tests/unittests/test_governance_plugin.py`; phase A04 adds evals | Commit |
| TOOL-001 | `GovernancePlugin.before_tool_callback` | Built |
| SPEC-001 | Phase A03 | Planned |
| FS-001 | `GovernancePlugin.before_tool_callback` | Built |
| SBX-001 | Phase A02 | Planned |
| VER-001 | Phases A02 and A03 | Planned |
| REV-001 | Phase A03; `ai-review.yml` applies it to pull requests | Planned |
| OBS-001 | `tests/unittests/test_telemetry.py` | Commit |
| QUAL-001 | Quality score test (S09) | Stage 9 |

## Telemetry invariants

| Span | Carries |
| --- | --- |
| Every model and tool span | `session.id`, `user.id`, `governance.sha`, `guardrail.result` |
| `governance.model_call` | `model.id`, `tokens.input`, `tokens.output`, `latency.ms` |
| `execute_tool <name>` | `tool.name`, `tool.tier` |

On errors, a span also carries `failure.source`:

| Value | Set when |
| --- | --- |
| `model` | `on_model_error_callback` runs |
| `harness` | The model's response has no token count |
| `tool` | `on_tool_error_callback` runs |
| `policy` | A tool is denied, or a session is over budget |
| `sandbox` | Phase A02's sandbox fails |

Phase A04 adds `intent.sha`, `work_item` and `verify.gate` once the intent-first workflow
exists.

The default ADK telemetry schema has no `call_llm` span, and its `generate_content` span
isn't current in plugin callbacks, so `GovernancePlugin` opens `governance.model_call`
itself. ADK's `execute_tool` span is current in tool callbacks, so the plugin sets its
attributes there.

Metrics: `governance.tool_calls.blocked`, `governance.confirmations` (`outcome`: asked,
approved or rejected), `governance.budget_refusals` and the gauge
`governance.session_tokens`.

The local stack is in `ops/observability/`. Run it from your own terminal, because the
sandbox blocks `docker`.
