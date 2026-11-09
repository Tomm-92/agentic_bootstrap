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
| EVID-001 | `DatabaseSessionService` in `scripts/local_session.py`, compaction off | Built |
| SEC-002 | Gitleaks in CI; phase A02 adds `verify.sh` | CI |
| DATA-001 | Collector allowlist test (S08), ORR sign-off (S09); phase A02 adds the sandbox | Stage 8, 9 |
| DEP-001 | Owner review, CI audit; phase A01 adds the runtime check | CI |
| COST-001 | `before_model_callback` and `after_model_callback` | Built |
| MODEL-001 | `tests/unittests/test_governance_plugin.py`; phase A04 adds evals | Commit |
| TOOL-001 | Before-tool policy (S07) | Stage 7 |
| SPEC-001 | Phase A03 | Planned |
| FS-001 | Before-tool policy (S07) | Stage 7 |
| SBX-001 | Phase A02 | Planned |
| VER-001 | Phases A02 and A03 | Planned |
| REV-001 | Phase A03; `ai-review.yml` applies it to pull requests | Planned |
| OBS-001 | Span test (S08) | Stage 8 |
| QUAL-001 | Quality score test (S09) | Stage 9 |

## Telemetry invariants

Stage 8 fills this in.
