---
id: '0024'
rules: [COST-001, SCOPE-001, SCOPE-002, GOV-002]
scope_paths:
  - docs/execution-plans/**
  - proposals/0024/**
  - docs/bootstrapper_tech_debt_tracker.md
---

# Plan 0024: eval ask rule in the first proposal

<!-- Written to docs/execution-plans/plan/active/<ID>-<name>.md when the owner approves it
in plan mode. Moved to docs/execution-plans/plan/completed/ when done. -->

## Goal

Intent: none (a gap found while preparing the rerun of `agent_governance.md`, scoped by
the owner in plan mode on 2026-11-23)
Spec: none (the owner approved this plan's Files that change as the spec)

The owner will rerun `agent_governance.md` on a fresh base. That base is 119267c, the
last commit before run A00. It has no `Bash(*eval_pass_rate*)` ask rule, which run A00
added only as an extra the owner approved. `agent_governance.md` doesn't tell the
design session to add it, so in manual mode A04's eval script would run with no
COST-001 prompt. This plan adds the rule to the first proposal and to A04's test.

It also records the false positives seen in plan 0023's paid-command deny. The plan
doesn't start the fresh run.

## Files that change

- `proposals/0024/docs/bootstrap-implementation/agent_governance.md`: a full copy of the
  live file, with:
  - **"First proposal and commit":** a `proposals/A00/.claude/settings.json` bullet,
    with one `ask` rule per paid command the run adds
  - **A04 Build 2:** the rule goes in `test_paid_model_runs_ask_first`
  - **A04's acceptance criteria:** the same check
- `docs/bootstrapper_tech_debt_tracker.md`: one row, appended last, for the deny's false
  positives.

## Order of work

- [x] Commit this plan.
- [x] Write the proposal copy, and `diff` it against the live file.
- [x] Append the tracker row.
- [x] Check that the owner's port of 0023 and 0024 applies to 119267c, in a throwaway
      index.
- [x] ruff, mypy, vulture, and the unit and governance tests pass. The `verifier` output
      goes in Proof.
- [x] Move this plan to `completed/`.

## Risks

- **The port's `git diff c5efbd7 ...` misses changes.** Everything since c5efbd7 belongs
  to plans 0023 and 0024. Any later commit on the branch would also be ported, so the
  owner runs the port straight after applying this plan.

## Proof

**The proposal copy.** `diff` against the live `agent_governance.md` shows three hunks
and nothing else:
- the `settings.json` bullet in "First proposal and commit"
- the sentence added to A04 Build 2
- the acceptance criterion added to A04

**The port, dry run.** I ran it in a throwaway index (`GIT_INDEX_FILE=$TMPDIR/port2.idx`),
starting from `git read-tree 119267c`:
- `git diff c5efbd7 HEAD -- . ':!docs/bootstrapper_tech_debt_tracker.md' ':!proposals'`
  applied with `git apply --cached`.
- So did the diff from the live document to the proposed one, as if the proposal were
  already applied.
- Result: 9 files changed, with no A00 files. They are `verifier.md`, `branch_guard.sh`,
  `checks_on_stop.sh`, `README.md`, `agent_governance.md`, `project_governance.md`, the
  two plans and `test_hooks.py`.

**Checks.** `echo '{"force": true}' | CLAUDE_PROJECT_DIR=$PWD
.claude/hooks/checks_on_stop.sh`: no output, exit 0.

`verifier` output after commit 3e1fc8b. It's the first `verifier` run with plan 0023's
`force` command: no fingerprint was deleted, and the classifier blocked nothing.

```text
1. echo '{"force": true}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh
   - Exit code: 0
   - Output: none
2. git status --porcelain -- app / git diff HEAD --name-only -- app
   - Exit code: 0
   - Output: none, so no scripted session
```

## Decisions

- **2026-11-23, owner, in plan mode.**
  - Fix the document before the rerun, rather than letting the rerun find the gap.
  - Rename the old local branch to `governance-agent-purpose-run1`, so the rerun's design
    session can create `governance-agent-purpose` as the document says.
  - This plan doesn't start the fresh run or prepare its branch. The run starts only when
    the owner approves it.
- **2026-11-23, owner, after the plan closed.** Work from `agent-governance-rerun` only.
  This replaces the rename above.
  - The old `governance-agent-purpose` is used only as the source of the port, then
    deleted.
  - The design session runs on `agent-governance-rerun` instead of creating
    `governance-agent-purpose`. The start prompt says so.
  - This is a known departure from "One plan, one branch" in `agent_governance.md`.

## Owner actions

Each is for your own terminal. The fresh run starts only when you approve it.

1. **Apply this proposal** on `governance-agent-purpose`:

   ```bash
   cp -R proposals/0024/. . && rm -rf proposals/0024
   git add -A && git commit -m "Apply proposal 0024: eval ask rule in the first proposal" \
     -m "Governance: $(git rev-parse HEAD:governance)
   Plan: 0024"
   ```

2. **Set up `agent-governance-rerun`.** The branch switch rewrites protected files, so
   the session can't do it.

   ```bash
   # Optional: save run A00's purpose inputs, so the interview needn't repeat them.
   git show governance-agent-purpose:docs/execution-plans/intent/A00-agent-purpose.md > ~/a00-purpose-inputs.md
   git switch -c agent-governance-rerun 119267c
   # Port plans 0023 and 0024: every change since the A00 build (c5efbd7), except the
   # tracker, which differs on the base.
   git diff c5efbd7 governance-agent-purpose -- . ':!docs/bootstrapper_tech_debt_tracker.md' | git apply --index
   # Tracker: drop the auto-mode row 0023 closed, and add 0024's row.
   sed -i '' "/^| Auto mode hasn't been shown to prompt every time/d" docs/bootstrapper_tech_debt_tracker.md
   git show governance-agent-purpose:docs/bootstrapper_tech_debt_tracker.md | tail -1 >> docs/bootstrapper_tech_debt_tracker.md
   .venv/bin/pytest -q tests/governance
   git add -A && git commit -m "Port plans 0023 and 0024 onto the pre-A00 base" \
     -m "Governance: $(git rev-parse HEAD:governance)
   Plan: 0024"
   ```

3. **Delete the old branch**, once the port is committed. This removes run A00 from your
   machine. `git reflog` can recover it for about 90 days.

   ```bash
   git branch -D governance-agent-purpose
   ```

   `origin/governance-agent-purpose` holds an older push of run A00 (dd15a3d). Delete
   it with `git push origin --delete governance-agent-purpose` if you don't want it
   there either.
4. **Start the run in a new session** on `agent-governance-rerun`, because the
   governance hash changes (GOV-006). Say: "Run the design session in
   docs/bootstrap-implementation/agent_governance.md. Use the current branch,
   agent-governance-rerun, instead of creating governance-agent-purpose." If you saved
   the inputs, add: "The purpose inputs are in ~/a00-purpose-inputs.md."
   - Auto mode is allowed now. That is what the rerun tests.
