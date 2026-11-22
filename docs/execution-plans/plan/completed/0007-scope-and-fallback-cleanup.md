---
id: '0007'
rules: [SCOPE-001, SCOPE-002, GOV-002, GOV-004, EVID-001, COST-001]
scope_paths:
  - tests/**
  - docs/exec-plans/**
  - proposals/0007/**
---

# Plan 0007: remove two hook tests and the proposal fallbacks, and test multi-glob scope

## Goal

Apply another project's plans 0007 and 0008 here. They do four things:

1. Remove `test_hooks::test_scope_with_this_runs_own_plan`.
2. Remove the `'git stash push'` case of `test_guard_allows_lookalikes`.
3. Remove the `proposals/0001` fallbacks in `test_hooks.py` and `test_settings.py`.
4. Give the test plan a second scope path, and parametrize `test_scope_inside_allowed`,
   to cover the gap that item 1 leaves.

They also bring the bootstrap spec in line, through a proposal. No application code or
hook changes.

Plan 0006 kept items 1 to 3, because `docs/governance_implementation.md` requires them.
On 2026-11-14 the owner chose to apply them, with a matching spec change in
`proposals/0007/`.

## Checklist

- [x] Check the preconditions. The gate decides scope with one `fnmatch` over all
      globs (`governance_gate.sh:92`). The guard reads the branch only after the commit
      check (`branch_guard.sh:31-35`). `proposals/0001/` does not exist.
- [x] Baseline: 270 run without integration, all pass in 14.0 s.
- [x] Apply items 1 to 4 to `tests/governance/test_hooks.py` and `test_settings.py`.
- [x] Prove the new `scripts/x.sh` case fails against a copy of the hooks, in
      `$TMPDIR`, that checks only `globs[0]`. Never edit `.claude/hooks/` (GOV-002).
      The owner ran it on 2026-11-14, because auto mode refused it to the agent.
      `[scripts/x.sh]` failed and `[app/deep/x.py]` passed.
- [x] Write the updated `docs/governance_implementation.md` to `proposals/0007/`.
      Auto mode refused the copy to the agent, so the owner copied the file and the
      agent edited Build 10 and 11 in the copy.
- [x] Run ruff, vulture, mypy and the unit tests. Expect 269.
- [x] Commit with the trailers, and move this plan to `completed/`.
- [ ] Delete `.venv` after the commit, as the owner asked. It can't be ticked in the
      commit, because the edit hooks need `.venv`.

## Result

- Before: 270 run without integration, all pass in 14.0 s.
- After: 269, all pass in 15.3 s. Ruff, ruff format, vulture and mypy are clean.
- Two tests removed, and one case added to `test_scope_inside_allowed`.
- The owner applies `proposals/0007/docs/governance_implementation.md`, which changes
  only Build 10 and 11.

## Decisions

- The spec is the recipe for bootstrapping a new project. During that run the hooks
  exist only in `proposals/0001/`, and the Stop hook runs the suite without
  `HOOKS_DIR`. So the proposal keeps the fallback for the bootstrap run, and adds a
  step to delete it once the owner applies proposal 0001. That keeps the run green and
  still removes the silent switch afterwards.
- The proposal replaces the "include this run's own plan" scope case with the
  two-glob case. It moves `git stash push` from the lookalikes to the commands allowed
  on `main`.

## Risks

- The tests and the spec disagree until the owner applies `proposals/0007/`. Both are
  in one commit.
