# Governance activation ledger

One row per control the catalogue marks `planned`. Only the owner moves a control to `active`.

| Rule | Control | Stage | Evidence | Result | Owner check |
| --- | --- | --- | --- | --- | --- |
| GOV-001 | UserPromptSubmit hook blocks prompts (S04) | S04 | tests/governance/test_hooks.py::test_prompt_blocked_and_session_start_fails_when_spoiled | pass | none |
| GOV-001 | SessionStart hook injects the governance hash (S04) | S04 | tests/governance/test_hooks.py::test_session_start_reports_hash_session_and_plan | pass | none |
| GOV-002 | Claude Code permission deny on protected paths (S04) | S04 | tests/governance/test_settings.py::test_protected_path_has_a_deny_rule | pass | none |
| GOV-002 | Claude Code permission deny on git push (S04) | S04 | tests/governance/test_settings.py::test_other_deny_rules_are_kept, tests/governance/test_hooks.py::test_guard_denies_on_any_branch | pass | none |
| GOV-002 | PreToolUse hook denies git commit on main (S04) | S04 | tests/governance/test_hooks.py::test_guard_denies_commit_on_main | pass | none |
| GOV-002 | Claude Code sandbox blocks indirect writes to protected paths (S04) | S04 | tests/governance/test_settings.py::test_sandbox_has_no_escape proves the config only; a session under it must show the refusal | deferred | After the run step 7 |
| GOV-003 | tests/governance/test_rules.py (S03) | S03 | tests/governance/test_rules.py | pass | none |
| GOV-004 | AGENTS.md instruction (S03) | S03 | AGENTS.md, Git section | pass | none |
| GOV-004 | .githooks/commit-msg (S04) | S04 | tests/governance/test_hooks.py::test_commit_msg_rejects_bad_trailers | pass | After the run step 6 |
| GOV-004 | governance workflow trailer check (S05) | S05 | not built yet | pending | none |
| GOV-005 | governance layer fails closed at startup and halts on hash change (S06) | S06 | not built yet | pending | none |
| GOV-006 | UserPromptSubmit hook restates the hash and plan and blocks on a hash change (S04) | S04 | tests/governance/test_hooks.py::test_prompt_blocked_after_hash_change_until_clear | pass | none |
| GOV-006 | AGENTS.md instruction to start a new session per plan (S03) | S03 | AGENTS.md, While working section | pass | none |
| SCOPE-001 | PreToolUse hook denies edits (S04) | S04 | tests/governance/test_hooks.py::test_edit_needs_exactly_one_plan | pass | none |
| SCOPE-002 | PreToolUse hook checks scope_paths (S04) | S04 | tests/governance/test_hooks.py::test_scope_outside_denied | pass | none |
| EVID-001 | Governance and Plan trailers enforced by commit-msg (S04) | S04 | tests/governance/test_hooks.py::test_commit_msg_rejects_bad_trailers | pass | After the run step 6 |
| EVID-001 | durable session log with compaction off (S06) | S06 | not built yet | pending | none |
| EVID-001 | evidence review each sprint (S09) | S09 | not built yet | pending | none |
| SEC-002 | gitleaks in the governance workflow (S05) | S05 | not built yet | pending | none |
| SEC-002 | secrets stage of verify.sh (A02) | A02 | phase A02 builds this | pending | none |
| DATA-001 | test that collector exporters match the allowlist (S08) | S08 | not built yet | pending | none |
| DATA-001 | sandbox containers run without a TTY or exec access (A02) | A02 | phase A02 builds this | pending | none |
| DATA-001 | ORR data-handling sign-off (S09) | S09 | not built yet | pending | none |
| DEP-001 | allowlist and registry existence check (A01) | A01 | phase A01 builds this | pending | none |
| DEP-001 | confirmation on non-allowlisted dependencies (A01) | A01 | phase A01 builds this | pending | none |
| DEP-001 | vulnerability audit and osv-scanner (S05, A02) | S05, A02 | not built yet | pending | none |
| COST-001 | governance layer enforces session_token_budget (S06) | S06 | not built yet | pending | none |
| MODEL-001 | test that configured model IDs are allowlisted (S06) | S06 | not built yet | pending | none |
| MODEL-001 | eval pass-rate gate on model change (A04) | A04 | phase A04 builds this | pending | none |
| TOOL-001 | before-tool policy default-deny (S07) | S07 | not built yet | pending | none |
| SPEC-001 | confirmation on approve_intent (A03) | A03 | phase A03 builds this | pending | none |
| SPEC-001 | executor input schema accepts only ApprovedIntent (A03) | A03 | phase A03 builds this | pending | none |
| FS-001 | before-tool path check (S07) | S07 | not built yet | pending | none |
| SBX-001 | verification sandbox container (A02) | A02 | phase A02 builds this | pending | none |
| VER-001 | verify gate blocks delivery (A02, A03) | A02, A03 | phase A02, A03 builds this | pending | none |
| VER-001 | user acknowledges high findings (A03) | A03 | phase A03 builds this | pending | none |
| REV-001 | test that reviewer and executor model IDs differ (A03) | A03 | phase A03 builds this | pending | none |
| OBS-001 | in-memory span exporter test (S08) | S08 | not built yet | pending | none |
| QUAL-001 | test that every score above 1 links to an existing file or test (S09) | S09 | not built yet | pending | none |
