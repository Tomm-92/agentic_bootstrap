---
id: '0026'
rules: [GOV-002, GOV-004, GOV-006, SCOPE-001, SCOPE-002, COST-001, DEP-001, SEC-002, EVID-001]
scope_paths:
  - proposals/0026/**
  - scripts/check_chain.py
  - tests/governance/**
  - README.md
  - REVIEW.md
  - AGENTS.md
  - docs/bootstrapper_tech_debt_tracker.md
  - .claude/settings.json
  - .claude/hooks/governance_gate.sh
  - .githooks/check_trailers.sh
  - .github/workflows/governance.yml
  - .github/workflows/scheduled-scans.yml
  - .gitleaksignore
---

# Plan 0026: decide on the gaps not assigned to a stage

Status: done. The owner approved it in plan mode on 2026-11-25.

<!-- Written to docs/execution-plans/plan/active/<ID>-<name>.md when the owner approves it
in plan mode. Moved to docs/execution-plans/plan/completed/ when done. -->

## Goal

Intent: [0026-unassigned-gaps-decision](../../intent/0026-unassigned-gaps-decision.md)
Spec: [0026-unassigned-gaps-decision](../../spec/0026-unassigned-gaps-decision.md)

Linear TMW-19. Resolve every gap from the handover's "Gaps not assigned to a stage"
here, with no new Linear issue and no new tech-debt row. That covers weekly full-repo
scans, one commit per gate, a CI chain check, a session gate on acceptance lines,
`disableBypassPermissionsMode`, and an auto mode policy. The managed settings file is
added only if the owner's bypass test shows a flag still wins. The handover, README,
`REVIEW.md` and tracker record the result.

## Files that change

Unprotected, written directly:
- `scripts/check_chain.py` (new): spec requirements 8 to 10. Same shape as
  `scripts/check_scope.py`: `_git()`, `problems(rev_range)`, and a `__main__` that
  writes problems to stderr. Added plans come from
  `git diff --name-only --diff-filter=A --find-renames <range> -- docs/execution-plans/plan/`,
  and files are read at the head with `git show <head>:<path>`.
- `tests/governance/test_check_chain.py` (new): requirement 12. Reuses the throwaway
  repo fixture pattern from `tests/governance/test_check_scope.py`.
- `tests/governance/test_hooks.py`: requirements 7 and 14. `Repo.edit()` gains
  `**tool_input`, so a test can pass `new_string` or `content`. These are written
  after the owner applies the proposals.
- `tests/governance/test_settings.py`: requirement 15, also after the apply.
- `README.md`: replace "One commit holds all three" (requirement 22), and add "When to
  use auto mode" (requirement 18). If requirement 17 applies, add the managed settings
  install step.
- `REVIEW.md`: "Do not report" gains the chain check (requirement 23).
- `docs/execution-plans/handover.md`: the decision table, stage 4's play 12 line, and
  the per-gate commit bullet (requirement 20).
- `docs/bootstrapper_tech_debt_tracker.md`: remove the chain row and the intent-commit
  row, and add "and acceptance lines" to the shell-write row (requirement 21).

Protected, written to `proposals/0026/` at the same path:
- `.github/workflows/scheduled-scans.yml` (new): requirements 1 to 5. It copies the
  `secrets` and `dependencies` jobs from `governance.yml`. gitleaks runs with no
  `--log-opts`, so it covers the full history, and with `--redact`. There's no
  `continue-on-error`. The triggers are `schedule: cron '0 6 * * 1'` and
  `workflow_dispatch`.
- `.github/workflows/governance.yml`: a "Chain" step after "Plan scope", in the same
  form, saving `governance-report/chain.txt`. pip-audit is pinned at the current PyPI
  release, found with `pip index versions pip-audit`.
- `.githooks/check_trailers.sh`: requirement 6. The `compgen` glob covers
  `plan/active`, `plan/completed`, `intent` and `spec`, and the error message names
  all four.
- `.claude/hooks/governance_gate.sh`: requirement 13. In the PreToolUse branch, before
  the `docs/execution-plans/*` exemption returns, a path under
  `docs/execution-plans/{intent,spec}/` runs a short `python -I` block. It denies when
  `new_string` (for an Edit) or `content` (for a Write) adds a `Status: accepted` line,
  or an `Accepted by:` line other than `<owner>, <YYYY-MM-DD>`, that the file on disk
  doesn't already have.
- `.claude/settings.json`: `permissions.disableBypassPermissionsMode: "disable"`.
- `AGENTS.md`: the owner's committed edit plus one line pointing to the README's
  auto mode part (requirement 19).
- `managed-settings.json`: only if requirement 17 applies.

## Order of work

- [x] Copy this plan to `docs/execution-plans/plan/active/0026-unassigned-gaps-decision.md`.
      Commit the intent, spec and plan together, since the old trailer rule is still live.
- [x] Owner: commit the `AGENTS.md` edit with `Plan: 0026`, wrapped to the file's width.
- [x] `scripts/check_chain.py` and its tests. Run them, then commit.
- [x] Write the proposals, except `managed-settings.json`. Run the new gate cases
      against `HOOKS_DIR=proposals/0026/.claude/hooks` from a scratch test file. Commit.
- [x] README, `REVIEW.md`, handover and tracker. Commit.
- [x] Owner: review the proposals, approve the pip-audit pin (DEP-001), and apply them
      in one commit that deletes `proposals/0026/`, with `Plan: 0026`.
- [x] Tests for requirements 7, 14 and 15 against the real paths. Commit.
- [x] Owner: the bypass test in a new terminal session (requirement 16), with the result
      recorded under Proof. If a flag wins: the managed settings proposal and README step,
      the owner installs it, and the test is repeated.
- [x] ruff, mypy, vulture, and the unit and governance tests pass, through the
      `verifier` subagent, with output pasted under Proof.
- [x] Comment the decisions on TMW-19, and move it to Done.
- [x] Move this plan to `completed/`. Make every edit before this step.

## Risks

- **The acceptance gate blocks legitimate work.** For example, the agent rewrites an
  accepted file and the comparison misreads it. The tests in requirement 14 cover
  Edit elsewhere, Write keeping the header, and Write setting draft.
- **The chain check fails on this plan's own pull request.** Plan 0026 links an
  accepted intent and spec that name `spec-security`, so it should pass. Run the check
  locally on `main..HEAD` before handing over.
- **The first scheduled gitleaks run fails on old findings.** This shows after merge.
  The owner triages, and `.gitleaksignore` is in scope.
- **The session runs long.** The unprotected work comes first. Anything left moves to
  a new plan with no Linear issue.

## Proof

- `.venv/bin/pytest -q tests/governance/test_hooks.py tests/governance/test_settings.py tests/governance/test_check_chain.py`:
  `172 passed in 9.09s`, after the owner's apply commit `65c9608`. `ruff check` and
  `ruff format --check` on `tests/governance`: `All checks passed!`, `12 files already
  formatted`.
- The `verifier` subagent, from the repo root on `agent-governance-rerun`:
  - `echo '{"force": true}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh`
    (ruff lint and format, vulture, mypy, unit and governance tests): exit 0, no output.
  - No changes under `app/`, so no scripted session.
  - `.venv/bin/python scripts/check_chain.py main..HEAD`: exit 0, no output.
  - `.githooks/check_trailers.sh main..HEAD`: exit 0, no output.
- The owner's `AGENTS.md` edit went in through the `proposals/0026/AGENTS.md` apply,
  so it had no separate commit.
- Bypass test (requirement 16), run by the owner on 2026-11-25 with Claude Code 2.1.332
  in a new terminal session in this repo, after the apply commit:
  - `claude --dangerously-skip-permissions`: started in plan mode (`⏸ plan mode on`),
    and cycling modes with Shift+Tab never offered bypass permissions.
  - `claude --permission-mode bypassPermissions`: showed "Bypass permissions mode was
    disabled by settings" and started in plan mode.
  - Neither flag reaches bypass mode, so the project setting is enough. Requirement 17's
    managed settings file isn't needed and wasn't shipped.

## Decisions

- **The chain check starts at plan 0026** (`FIRST_CHECKED` in `scripts/check_chain.py`).
  Spec requirement 8 relied on renames to skip old plans, but `main` predates the docs
  move (plan 0020), so this branch's pull request adds every plan as a new path. Plans
  0017 to 0025 also predate the `spec-security` report, and 0018 and 0019 link with
  the old folder depth. A run on `main..HEAD` flagged 21 plans and two `.gitkeep` files before the cutoff, and
  none after it.
- **pip-audit is pinned at 2.10.1**, the current PyPI release (published 2026-06-10),
  pending the owner's DEP-001 approval.
- **The proposed hooks were tested before the handover.** The 37 existing gate tests
  passed with `HOOKS_DIR=proposals/0026/.claude/hooks`. A throwaway test file ran 14 new
  cases against the proposed gate and `check_trailers.sh`, all passing, and was deleted.
  The same cases go into `test_hooks.py` after the apply.
- No memory file for the tech-debt bar. The owner put it in `AGENTS.md`, and the gate
  denies writes outside the repo in any case.
- Tests that read protected paths land after the owner's apply commit, as in plan 0025.
  The gate cases are checked first against the proposal through `HOOKS_DIR`.

## Owner actions

1. Commit your `AGENTS.md` edit under `Plan: 0026`.
2. Review `proposals/0026/`, approve the pip-audit version, and apply it in one commit
   that deletes the folder.
3. Run the bypass test in a new terminal: `claude --dangerously-skip-permissions`, then
   `claude --permission-mode bypassPermissions`. Report whether either reaches bypass
   mode.
4. After merge, run "scheduled-scans" once from the Actions tab and triage any
   findings.
