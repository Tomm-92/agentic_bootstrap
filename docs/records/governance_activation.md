# Governance activation ledger

One row per control the catalogue marks `planned`. Only the owner moves a control to `active`.

`Result` is `pass`, `deferred`, `blocked`, `failed` or `pending`. `scripts/check_activation.py`
accepts an activation only with result `pass`, and an owner check of `none` or one the owner has
rewritten to start with `Confirmed`.

| Rule | Control | Stage | Evidence | Result | Owner check |
| --- | --- | --- | --- | --- | --- |
| GOV-001 | UserPromptSubmit hook blocks prompts (S04) | S04 | tests/governance/test_hooks.py::test_prompt_blocked_and_session_start_fails_when_spoiled | pass | none |
| GOV-001 | SessionStart hook injects the governance hash (S04) | S04 | tests/governance/test_hooks.py::test_session_start_reports_hash_session_and_plan | pass | none |
| GOV-002 | Claude Code permission deny on protected paths (S04) | S04 | tests/governance/test_settings.py::test_protected_path_has_a_deny_rule | pass | none |
| GOV-002 | Claude Code permission deny on git push (S04) | S04 | tests/governance/test_settings.py::test_other_deny_rules_are_kept, tests/governance/test_hooks.py::test_guard_denies_on_any_branch | pass | none |
| GOV-002 | PreToolUse hook denies git commit on main (S04) | S04 | tests/governance/test_hooks.py::test_guard_denies_commit_on_main | pass | none |
| GOV-002 | Claude Code sandbox blocks indirect writes to protected paths (S04) | S04 | tests/governance/test_settings.py::test_sandbox_has_no_escape proves the config only; a session under it must show the refusal | pass | Confirmed by the owner, 2026-11-11 |
| GOV-003 | tests/governance/test_rules.py (S03) | S03 | tests/governance/test_rules.py | pass | none |
| GOV-004 | AGENTS.md instruction (S03) | S03 | AGENTS.md, Git section | pass | none |
| GOV-004 | .githooks/commit-msg (S04) | S04 | tests/governance/test_hooks.py::test_commit_msg_rejects_bad_trailers | pass | Confirmed by the owner, 2026-11-11 |
| GOV-004 | governance workflow trailer check (S05) | S05 | proposals/0001/.github/workflows/governance.yml, actionlint; .githooks/check_trailers.sh ran clean locally | pass | Confirmed by the owner, 2026-11-11 |
| GOV-005 | governance layer fails closed at startup and halts on hash change (S06) | S06 | tests/unittests/test_governance_plugin.py::test_startup_fails_when_governance_is_dirty, tests/unittests/test_governance_plugin.py::test_run_halts_on_a_hash_change, tests/unittests/test_governance_plugin.py::test_every_event_carries_the_hash | pass | none |
| GOV-006 | UserPromptSubmit hook restates the hash and plan and blocks on a hash change (S04) | S04 | tests/governance/test_hooks.py::test_prompt_blocked_after_hash_change_until_clear | pass | none |
| GOV-006 | AGENTS.md instruction to start a new session per plan (S03) | S03 | AGENTS.md, While working section | pass | none |
| SCOPE-001 | PreToolUse hook denies edits (S04) | S04 | tests/governance/test_hooks.py::test_edit_needs_exactly_one_plan | pass | none |
| SCOPE-002 | PreToolUse hook checks scope_paths (S04) | S04 | tests/governance/test_hooks.py::test_scope_outside_denied | pass | none |
| SCOPE-002 | governance workflow scope check (S05) | S05 | tests/governance/test_check_scope.py; scripts/check_scope.py over main's 48 commits reported only 7d58e45, an owner edit to governance/profile.yaml | pass | Confirmed by the owner, 2026-11-16: the "Plan scope" step passed on the agent-instructions-split pull request, which applies proposal 0010 (commit a2ac814) |
| EVID-001 | Governance and Plan trailers enforced by commit-msg (S04) | S04 | tests/governance/test_hooks.py::test_commit_msg_rejects_bad_trailers | pass | Confirmed by the owner, 2026-11-11 |
| EVID-001 | durable session log with compaction off (S06) | S06 | tests/unittests/test_governance_plugin.py::test_compaction_is_off; .venv/bin/python -m scripts.local_session --fake wrote stamped events to .sessions/sessions.db | pass | none |
| EVID-001 | evidence review each sprint (S09) | S09 | docs/EVIDENCE_REVIEW.md, review of 2026-11-11 (.venv/bin/python -m scripts.evidence_report and .sessions/sessions.db) | pass | Confirmed by the owner, 11-11-2026 |
| SEC-002 | gitleaks in the governance workflow (S05) | S05 | proposals/0001/.github/workflows/governance.yml, actionlint; gitleaks git ran clean locally | pass | Confirmed by the owner, 2026-11-11 |
| SEC-002 | secrets stage of verify.sh (A02) | A02 | phase A02 builds this | pending | none |
| DATA-001 | test that collector exporters match the allowlist (S08) | S08 | tests/governance/test_observability.py::test_collector_exporters_match_the_allowlist | pass | none |
| DATA-001 | sandbox containers run without a TTY or exec access (A02) | A02 | phase A02 builds this | pending | none |
| DATA-001 | ORR data-handling sign-off (S09) | S09 | docs/SECURITY.md | deferred | Sign off docs/SECURITY.md, After the run step 9 in docs/agent_governance_implementation.md |
| DEP-001 | allowlist and registry existence check (A01) | A01 | phase A01 builds this | pending | none |
| DEP-001 | confirmation on non-allowlisted dependencies (A01) | A01 | phase A01 builds this | pending | none |
| DEP-001 | vulnerability audit and osv-scanner (S05, A02) | S05, A02 | proposals/0001/.github/workflows/governance.yml, actionlint; pip-audit and osv-scanner found nothing locally; A02 adds output scanning | pass | Confirmed by the owner, 2026-11-11 |
| COST-001 | Claude Code permission ask on paid-model commands (S04) | S04 | tests/governance/test_settings.py::test_paid_model_runs_ask_first proves the config only; a session under it must show the prompt | pass | Confirmed by the owner, 2026-11-16: in a session under governance b233b58, `.venv/bin/pytest -q -m integration` and `.venv/bin/python -m scripts.local_session --real hi` both prompted and were declined, and `.venv/bin/python -m scripts.local_session hi` ran without a prompt and returned the scripted reply |
| COST-001 | unit-test fixture refuses network connections | codequality | tests/unittests/conftest.py::no_network; plan 0010 probe: a raw socket and an anthropic client call were both refused | pass | none |
| COST-001 | governance layer enforces session_token_budget (S06) | S06 | tests/unittests/test_governance_plugin.py::test_session_is_refused_once_over_budget, tests/unittests/test_governance_plugin.py::test_missing_token_count_is_an_error; on 2026-11-11 the Stage 6 manual run logged real claude-haiku-5-5 token counts in .sessions/sessions.db, and pytest -m integration passed | pass | Confirmed by the owner, 2026-11-11 |
| MODEL-001 | test that configured model IDs are allowlisted (S06) | S06 | tests/unittests/test_governance_plugin.py::test_every_configured_model_is_allowlisted | pass | none |
| MODEL-001 | eval pass-rate gate on model change (A04) | A04 | phase A04 builds this | pending | none |
| TOOL-001 | before-tool policy default-deny (S07) | S07 | tests/unittests/test_tool_policy.py::test_unlisted_tool_on_the_agent_is_denied, tests/unittests/test_tool_policy.py::test_deny_tier_tool_is_denied, tests/unittests/test_tool_policy.py::test_non_allowlisted_target_is_denied, tests/unittests/test_tool_policy.py::test_confirm_tool_not_built_with_governed_tool_is_denied | pass | none |
| SPEC-001 | confirmation on approve_intent (A03) | A03 | phase A03 builds this | pending | none |
| SPEC-001 | executor input schema accepts only ApprovedIntent (A03) | A03 | phase A03 builds this | pending | none |
| FS-001 | before-tool path check (S07) | S07 | tests/unittests/test_tool_policy.py::test_path_escape_is_denied, tests/unittests/test_tool_policy.py::test_symlink_escape_is_denied, tests/unittests/test_tool_policy.py::test_work_item_that_escapes_the_output_root_is_denied | pass | none |
| SBX-001 | verification sandbox container (A02) | A02 | phase A02 builds this | pending | none |
| VER-001 | verify gate blocks delivery (A02, A03) | A02, A03 | phase A02, A03 builds this | pending | none |
| VER-001 | user acknowledges high findings (A03) | A03 | phase A03 builds this | pending | none |
| REV-001 | test that reviewer and executor model IDs differ (A03) | A03 | phase A03 builds this | pending | none |
| OBS-001 | in-memory span exporter test (S08) | S08 | tests/unittests/test_telemetry.py::test_session_emits_every_invariant_attribute; a --fake session showed as a complete trace in Tempo with every attribute | pass | none |
| QUAL-001 | test that every score above 1 links to an existing file or test (S09) | S09 | tests/governance/test_quality_score.py::test_every_score_above_one_has_existing_evidence | pass | none |
