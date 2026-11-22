---
id: '0019'
rules: [GOV-002, GOV-004, GOV-006, COST-001, EVID-001, SEC-001, SCOPE-001, SCOPE-002]
scope_paths:
  - docs/exec-plans/**
  - README.md
  - proposals/0019/**
---

# Plan 0019: verifier subagent and failing test first

Status: done. The owner approved it in plan mode on 2026-11-22.

<!-- Written to docs/exec-plans/active/<ID>-<name>.md when the owner approves it in plan
mode. Moved to docs/exec-plans/completed/ when done. -->

## Goal

Intent: [0019-verifier-and-test-first](../intent/0019-verifier-and-test-first.md)
Spec: [0019-verifier-and-test-first](../spec/0019-verifier-and-test-first.md)

This is stage 3 of the handover (playbook plays 07 and 08). It does four things:
- It adds a `verifier` subagent that runs CI's check command and reports the literal
  output.
- It adds four `AGENTS.md` rules on tests: a bug fix starts with a strict `xfail`
  test, a test changes only for a stated reason and in its own commit, and a task is
  reported done with the check output.
- It lists the verifier in the README.
- It marks stage 3 done in the handover.

Both new files are blocked for agents, so they go to `proposals/0019/` for the owner
to apply. `AGENTS.md` is protected (GOV-002), and the sandbox blocks
`.claude/agents/`. That block was checked on 2026-11-22.

## Files that change

- **`proposals/0019/.claude/agents/verifier.md` (new).** This is spec requirements 1
  to 4.
  - The frontmatter has `name: verifier`, the spec's `description` word for word, and
    `tools: Bash, Read`. It sets no `model`.
  - The body is short:
    - Always run `rm -f .claude/.checks_fingerprint` and then
      `echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh`.
    - If `git status --porcelain` or `git diff HEAD --name-only` shows changes under
      `app/`, also run
      `.venv/bin/python -m scripts.local_session "What is the status of demo?"`.
    - Never pass `--real`, and never run `pytest -m integration`.
    - Report each command, its exit code and its literal output. Exit 0 with no
      output is reported as "all checks passed".
    - Don't edit, create or delete files, apart from the fingerprint. Don't fix,
      suggest fixes or retry.
- **`proposals/0019/AGENTS.md` (new).** A full copy of `AGENTS.md`, with the four
  lines from spec requirement 5 added at the end of the Tests section, word for word.
- **`README.md`.** One row in the "Review commands" table (line 359). The intro line
  becomes "Run these by hand, after a commit. Claude calls the verifier itself before
  reporting a task done." The new row is:
  - Command: ``ask for the `verifier` ``
  - What it does: "Runs the same checks as CI, plus a scripted session for `app/`
    changes, and reports the output. Never edits."
  - Source: `.claude/agents/verifier.md`
- **`docs/exec-plans/handover.md`.** This is spec requirement 10.
  - The stage 3 row becomes "Done (plan 0019)", and **Next:** names stage 4.
  - The stage 3 section gets an "As built (plan 0019)" note: the verifier runs CI's
    command, a bug fix starts with a strict `xfail`, there's no locked-test hook, and
    parallel sessions were dropped.
  - In stage 4, "It doesn't edit a failing test" is replaced with the requirement 5
    rules.
  - The next free plan ID becomes 0020.
- **`docs/exec-plans/active/0019-verifier-and-test-first.md`.** This plan, moved to
  `completed/` at the end.

These don't change: `REVIEW.md` (requirement 9), `checks_on_stop.sh`,
`.claude/settings.json`, CI, and the plan template.

## Order of work

- [x] Copy this plan to `docs/exec-plans/active/0019-verifier-and-test-first.md`.
  Commit it with the intent and spec as one commit:
  "0019: intent, spec and plan for the verifier and failing test first".
- [x] Write `proposals/0019/.claude/agents/verifier.md` and `proposals/0019/AGENTS.md`.
- [x] Edit the README table.
- [x] Update the handover.
- [x] Run the checks with the spec's command, and paste the output into Proof.
- [x] Commit: "0019: add the verifier subagent and test rules, by proposal".
- [x] Mark the plan done, fill in Decisions and Owner actions, and move it to
  `completed/`. Commit.

Every commit carries the trailers `Governance: <git rev-parse HEAD:governance>` and
`Plan: 0019`.

## Risks

- **The README describes a verifier that doesn't exist yet.** It exists only once the
  owner copies `verifier.md` into place. The owner actions say so. The gap closes when
  the proposal is applied.
- **The proposal's copy of `AGENTS.md` could drift.** If `AGENTS.md` changes before
  the owner applies the proposal, the copy undoes that change. Checked by diffing the
  proposal against the current `AGENTS.md` before committing. The only difference
  should be the four added lines.
- **The verifier might not be called.** The description makes a call likely, not
  certain. The spec's Concerns record this, and it's accepted.

## Proof

- `diff AGENTS.md proposals/0019/AGENTS.md` shows only the four added lines
  (`93a94,103`).
- The check command exits 0. Its literal output, run before the build commit:

  ```text
  $ rm -f .claude/.checks_fingerprint
  $ echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh; echo "exit $?"
  exit 0
  ```

  No output with exit 0 means ruff, ruff format, the suppression check, vulture,
  mypy and pytest all passed.
- After the owner applies the proposal, `/agents` lists `verifier`. Asking "do the
  checks pass?" makes Claude call it. This is the owner's check, because the file
  can't be put in place before then.

## Decisions

- **The verifier checks `app/` changes with two git commands.** `git status
  --porcelain -- app` catches uncommitted and untracked changes, and
  `git diff HEAD --name-only -- app` is there for clarity. Committed changes on the
  branch aren't checked. The verifier runs before a task is reported done, while the
  work is usually still uncommitted, and CI never runs `local_session`.
- **The README row says "Ask for the `verifier`"**, because the table's other rows
  are slash commands and a subagent has none.
- **The handover's stage 3 section follows stage 2's pattern.** Its build notes and
  owner decision became an "As built" list, and it now points to stage 4 as plan
  0020.

## Owner actions

- Review `proposals/0019/`, then copy `AGENTS.md` and `.claude/agents/verifier.md`
  into place and commit with the trailers. `check_scope.py` accepts this, because the
  paths are under `proposals/0019/`.
- Check that `/agents` lists the verifier, and try it once.
- Optional: change `Accepted by:` in the spec from `<2026-11-22>` to `2026-11-22`.
