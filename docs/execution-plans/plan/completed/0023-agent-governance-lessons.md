---
id: '0023'
rules: [GOV-002, GOV-004, COST-001, SCOPE-001, SCOPE-002, VER-001, TOOL-001, QUAL-001,
        EVID-001]
scope_paths:
  - docs/execution-plans/**
  - proposals/0023/**
  - tests/governance/test_hooks.py
---

# Plan 0023: agent governance lessons

<!-- Written to docs/execution-plans/plan/active/<ID>-<name>.md when the owner approves it
in plan mode. Moved to docs/execution-plans/plan/completed/ when done. -->

## Goal

Intent: none (lessons from run A00, scoped by the owner in plan mode on 2026-11-23)
Spec: none (the owner approved this plan's Files that change as the spec)

Run A00 hit problems a repeat run must not hit again. The changes go into
`agent_governance.md` and the hooks it relies on, so that the whole of
`agent_governance.md` can run in auto mode:

1. **Verify gate.** Code written after a `pass` or an acknowledgement reached the reviewer
   unverified.
2. **Conformance and `stdin`.** `conformance.py` crashed on an example without the
   optional `stdin`, and no free test covered the stage.
3. **Missing test file.** A05 needed `tests/governance/test_quality_score.py`, which the
   spec's file list missed.
4. **EVID-001.** The document says the EVID-001 review stays `deferred`, but it was
   already `active` from S09.
5. **Extra `tools.yaml` proposals.** Two were needed, because ADK exposes tool names the
   first proposal didn't list (`executor`, `reviewer`, `set_model_response`).
6. **Auto mode.**
   - The run was banned from it (COST-001).
   - The classifier blocked the live hook probe.
   - It blocked a check command that deleted hook state.

Also covered: the `acknowledge` confirmation design, which caused a stop in A03.

## Files that change

Each protected file goes into `proposals/0023/` as a full copy of the live file, edited.
`README.md`, the tracker, the hook tests and the verifier go in the proposal too, so
everything lands in the one commit that applies it.

- `proposals/0023/docs/bootstrap-implementation/agent_governance.md`:
  - **Prerequisites:** auto mode allowed, and the paid-command deny and the owner batch
    described.
  - **First proposal:** the `tools.yaml` entries that ADK itself exposes.
  - **Spec:** file lists include the tests that read each changed file, and the intent
    artifact's fields are fixed.
  - **Build session:** a hook check replaces the live probe. The subagent's check
    command doesn't delete hook state.
  - **A02:** fixtures without optional fields, and a free unit test per stage.
  - **A03:** writes reset the gate, the `acknowledge` design, and ADK notes.
  - **A05:** EVID-001 stays `active`, and the final report has the owner batch.
  - **After the run:** step 7 is reworded.
- `proposals/0023/.claude/hooks/branch_guard.sh`: denies paid-model commands unless
  `permission_mode` is `default` (COST-001).
- `proposals/0023/.claude/hooks/checks_on_stop.sh`: `{"force": true}` input skips the
  fingerprint comparison.
- `proposals/0023/docs/bootstrap-implementation/project_governance.md`: the same two
  hook changes, in its branch_guard spec and in its verbatim hook copies.
- `tests/governance/test_hooks.py`, the live file: tests for the paid-command deny. The
  ones that need the proposed hook are marked `xfail(strict=True)`, and the apply commit
  removes those markers.
- `proposals/0023/.claude/agents/verifier.md`: the `force` check command.
- `proposals/0023/README.md`: the auto-mode prerequisite.
- `proposals/0023/docs/bootstrapper_tech_debt_tracker.md`: removes the auto-mode row and
  the EVID-001 conflict row, which this closes.

## Order of work

- [x] Commit this plan.
- [x] Copy each file into `proposals/0023/`, then edit the copies.
- [x] `diff` each copy against its original. It differs only as described.
- [x] With the proposed hooks (see Proof: a full scratch copy hit five unrelated failures,
      so the hook tests ran against the proposed hooks through `HOOKS_DIR` instead):
  - `tests/governance/test_hooks.py` passes with `--runxfail`
  - hand runs of `checks_on_stop.sh` behave as described
- [x] ruff, mypy, vulture, and the unit and governance tests pass. The `verifier` output
      goes in Proof.
- [x] Move this plan to `completed/`.

## Risks

- **In manual mode, a subagent's paid call may be denied** if a subagent's hook input has
  no `permission_mode`. The docs don't say whether it does. The hook fails closed, and
  the check is deferred to the owner's terminal.
- **The deny matches command text, as the ask rules do.** `python -c` importing `app`
  gets past it. That gap is already recorded for the ask rules.
- **The proposal copies drift** if their originals change before the owner applies them.
  The `diff`s in Proof show the intended difference at commit time.

## Proof

**The proposal's files.** Each is a full copy of its live file, and `diff` shows only the
changes this plan describes. There are seven:
- `agent_governance.md`: 147 changed lines.
- `project_governance.md`: the Stage 4 Build 7 bullet, the ask-rules note, and the
  verbatim `branch_guard.sh`. That copy is identical to the proposed hook, because it
  was replaced from it by script.
- `branch_guard.sh`, `checks_on_stop.sh`, `verifier.md`, `README.md` and the tracker
  (two rows removed).

**Hook tests.** I ran `tests/governance/test_hooks.py` with `--runxfail` and
`HOOKS_DIR`, against a copy of the live hooks with the proposed `branch_guard.sh` and
`checks_on_stop.sh` laid over them:

```text
HOOKS_DIR=$TMPDIR/hooks0023 .venv/bin/pytest -q -p no:cacheprovider --runxfail tests/governance/test_hooks.py
100 passed in 7.60s
.venv/bin/pytest -q -p no:cacheprovider --runxfail tests/governance/test_hooks.py   # live hooks
25 failed, 75 passed in 7.11s
```

The 25 that fail on the live hooks are exactly the strict-xfail paid-command cases. On
the live hooks without `--runxfail`, the result is `75 passed, 25 xfailed`.

A full scratch copy of the repo failed five SCOPE-002 tests. They failed the same way
without the proposal, so the scratch copy causes them, not this plan. The `HOOKS_DIR`
run above replaces that check.

**`checks_on_stop.sh`, proposed version, by hand:**

```text
echo '{}' | ... first run                        exit 0
echo '{}' | ... matching fingerprint, no force   exit 0 in 0s   (skipped)
echo '{"force": true}' | ... matching fingerprint exit 0 in 19s  (checks ran)
```

**Live checks before the commits** (`rm -f .claude/.checks_fingerprint`, then
`echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh`): no output,
exit 0.

`verifier` output after commit 7490ac7:

```text
1. rm -f .claude/.checks_fingerprint && echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh
   - Exit code: 0
   - Output: none
2. git status --porcelain -- app / git diff HEAD --name-only -- app
   - Exit code: 0
   - Output: none, so no scripted session
```

## Decisions

- **2026-11-23, owner, in plan mode.**
  - **Paid calls.** A hook denies paid commands unless the session is in manual mode, so
    in auto mode every paid check goes to one owner batch. Rejected options: relying on
    the `ask` prompts alone, and denying only in `bypassPermissions` and `dontAsk`.
  - **Docker** stays blocked by the sandbox. Its checks go to the owner batch, because
    the Docker socket gives host access.
  - **Process.** Plan 0023 only, with no intent or spec, on `governance-agent-purpose`.
- **2026-11-23, owner, new path.** A test file copied into `proposals/0023/` fails ruff,
  because `ruff.toml` (protected) relaxes the test rules only for `tests/**`. The owner
  approved adding `tests/governance/test_hooks.py` to `scope_paths`.
  - The new tests that need the proposed hook are marked
    `xfail(strict=True, reason='needs proposal 0023')`.
  - The apply commit removes those markers. If they're left in, strict xfail fails the
    checks.
  - Rejected options: a patch file, and adding the tests after the proposal is applied.
- **2026-11-23, facts from the Claude Code docs** (hooks and permission-modes pages):
  - PreToolUse input carries `permission_mode`: `default` (manual), `plan`,
    `acceptEdits`, `auto`, `dontAsk` or `bypassPermissions`.
  - Hooks fire inside subagents.
  - `ask` rules still prompt in auto mode.

## Owner actions

Review `proposals/0023/`, then apply it in one commit. It doesn't change the governance
hash. The `sed` removes the strict-xfail markers from the new hook tests. If any is left,
its test passes and strict xfail fails the checks.

```bash
cp -R proposals/0023/. . && rm -rf proposals/0023
sed -i '' "/reason='needs proposal 0023'/d" tests/governance/test_hooks.py
.venv/bin/pytest -q tests/governance/test_hooks.py
git add -A && git commit -m "Apply proposal 0023: agent governance lessons" \
  -m "Governance: $(git rev-parse HEAD:governance)
Plan: 0023"
```
