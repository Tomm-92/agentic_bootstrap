# Quality score

| Score | Meaning |
| --- | --- |
| 1 | Not built, or no evidence |
| 2 | Built, with partial evidence |
| 3 | Built and tested, but not yet proven in real use |
| 4 | Proven in real use |
| 5 | Proven in real use, and improved through evidence reviews |

QUAL-001: a score above 1 needs linked evidence that exists. `tests/governance/test_quality_score.py`
checks this. Phase A05 adds the areas that depend on the agent's purpose.

| Area | Score | Evidence |
| --- | --- | --- |
| Governance enforcement | 3 | [hook tests](../../tests/governance/test_hooks.py), [settings tests](../../tests/governance/test_settings.py) |
| Scope control | 3 | [hook tests](../../tests/governance/test_hooks.py) |
| Supply chain | 2 | [pinned lock file](../../requirements-dev.lock), [activation ledger](governance_activation.md) |
| Evidence | 3 | [plugin tests](../../tests/unittests/test_governance_plugin.py), [evidence report](../../scripts/evidence_report.py) |
| Runtime governance | 3 | [plugin tests](../../tests/unittests/test_governance_plugin.py) |
| Tool policy | 3 | [policy tests](../../tests/unittests/test_tool_policy.py) |
| Observability | 3 | [span tests](../../tests/unittests/test_telemetry.py), [stack tests](../../tests/governance/test_observability.py) |
| Cost per session | 1 | No real session has run yet |
