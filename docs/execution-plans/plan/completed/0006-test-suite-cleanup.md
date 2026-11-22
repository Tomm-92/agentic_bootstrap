---
id: '0006'
rules: [SCOPE-001, SCOPE-002, GOV-002, GOV-003, QUAL-001, EVID-001, COST-001]
scope_paths:
  - tests/**
  - docs/exec-plans/**
  - proposals/0006/**
---

# Plan 0006: remove tests that add no value

## Goal

Cut the suite down to tests that catch a real regression or prove a governance control.
This plan applies the findings of another project's plan 0007 to this repo, where they
still hold. No application code changes.

## What counts as no value

A test is a candidate for removal or merging when it:

- repeats another test's assertion on the same code path
- tests the framework, Pydantic or Python rather than this project's code
- asserts on implementation detail that a refactor would break with no change in
  behaviour
- is a parametrized case that adds no new equivalence class
- cannot fail
- belongs to code or a control that no longer exists

A test is kept, whatever its overlap, when it is the evidence for a control. That
covers tests named in `docs/governance-activation.md`, `docs/QUALITY_SCORE.md`,
`docs/SECURITY.md` or a `controls` entry in `governance/rules.yaml`, plus
`tests/governance/test_rules.py`, which `.github/workflows/governance.yml` runs.

## Checklist

- [x] Record the baseline (Findings).
- [x] Check which of plan 0007's items apply here (Findings).
- [x] Check that no removed test is named as evidence. The evidence search names 28
      tests, and none of them is on the list below.
- [x] Owner approves the remove and merge list, and decides on items 4, 5 and C below.
      Approved items 1, 2, 3, 6, 7 and 9 on 2026-11-14. Items 4, 5 and C stay.
- [x] Apply the approved changes one file at a time. Delete what becomes unused.
- [x] If C is approved, write the updated `docs/governance_implementation.md` to
      `proposals/0006/` for the owner to apply. Not needed: C was not approved.
- [x] Run ruff, vulture, mypy and the unit and governance tests. Record the before and
      after counts and the run time.
- [x] Integration tests are not run without owner approval (COST-001). Not run.
- [ ] After the task, delete `.venv` and run `pip cache purge`, as the owner asked.
      This happens after the commit, because the edit hooks need `.venv`.

## Result

- Before: 278 tests run without integration, all passing in 16.0 s.
- After: 270, all passing in 14.4 s. Ruff, ruff format, vulture and mypy are clean.
- 8 removed, not 9 or 10: items 4 and 5 stay. Item 7 removes three cases, and item 9
  merges two tests into one.
- Also deleted, because the changes left it unused: the `shutil` import in
  `test_hooks.py`.

## Findings

Baseline, 2026-11-14: 279 collected, 278 run without integration, all pass in 16.0 s.

`proposals/0001/` and `proposals/A00/` do not exist here. This repo never had the A00
pieces (`ADDITIONS`, `LIVE_TOOLS`, `needs_proposed_governance`, `test_proving_repo.py`,
`test_sandbox.py`), so plan 0007's items 8 and 10, the A00 cleanup and the ledger edits
do not apply.

### Proposed changes (need owner approval)

| # | Test | Change | Reason | Still covered by |
| --- | --- | --- | --- | --- |
| 1 | `test_adk_conventions::test_agent_loads` | remove | Duplicate | `test_governance_plugin::test_agent_loads_the_way_the_runner_loads_it` |
| 2 | `test_governance_plugin::test_startup_fails_when_governance_is_missing` | remove | Same path: `rev-parse HEAD:governance` fails, and `_git` raises `GovernanceError` in its one `except` | `test_startup_fails_when_governance_is_uncommitted` |
| 3 | `test_hooks::test_hook_scripts_are_executable` | remove, and the `shutil` import | Every other hook test runs these scripts directly | The gate, guard and commit-msg tests |
| 4 | `test_hooks::test_scope_with_this_runs_own_plan` | remove (**needs C**) | Same `fnmatch` check as the scope tests | `test_scope_inside_allowed`, `test_scope_outside_denied` |
| 5 | `test_hooks::test_guard_allows_lookalikes['git stash push']` | remove case (**needs C**) | The same command is allowed on `main` | `test_guard_allows_other_commands_on_main['git stash push']` |
| 6 | `test_hooks::test_guard_allows_other_commands_on_main['git log --oneline']` | remove case | No commit, so `branch_guard.sh` exits early, like `git status` | `['git status']` |
| 7 | `test_check_activation::test_a_rule_field_change_fails` | 4 cases → 1 (`tier`) | `_compare_rule` compares every non-control field in one dict check | The `tier` case |
| 9 | `test_rules::test_profile_has_every_key`, `test_bootstrap_keys_are_filled` | merge into `test_profile_is_complete` | Same file, overlapping checks. This repo has no `test_purpose_keys_are_filled` | The merged test keeps every assertion |

That removes 9 tests: items 1 to 6 remove one each, item 7 removes three cases and
item 9 merges two tests into one. 278 becomes 269.

### Dead code (no test removed)

- C: delete the `proposals/0001` defaults in `test_hooks.py` (`PROPOSED`) and
  `test_settings.py` (`PROPOSED`, and the two-folder loop in
  `test_every_hook_script_exists`). Keep the `HOOKS_DIR` and `SETTINGS_PATH` overrides.

`scripts/arm_governance.py` also names `proposals/0001`. That is the live step that
applies the proposal in a new project, so it stays. It is outside this plan's scope.

## Decisions

- No test is removed until the owner approves the list.
- C, and items 4 and 5, contradict `docs/governance_implementation.md:572-591`, a
  protected path. That section specifies the `proposals/0001` default, a scope test
  against `0001-bootstrap.md`, and `git stash push` as a lookalike, for the bootstrap
  run in a new project. The owner chose to keep them, so the tests still match the
  spec, and the fallbacks still work when a new project is bootstrapped from this
  repo.

## Risks

- A removed test may have been the only check on an edge case. Each removal names the
  test that still covers it.
- The tests and the bootstrap spec could drift apart, if C is applied before the owner
  applies the doc proposal. Mitigation: commit both together.
