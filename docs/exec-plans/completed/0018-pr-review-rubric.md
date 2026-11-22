---
id: '0018'
rules: [REV-001, MODEL-001, SEC-002, EVID-001, COST-001, GOV-002, GOV-004, GOV-006, SCOPE-001, SCOPE-002]
scope_paths:
  - REVIEW.md
  - docs/EVIDENCE_REVIEW.md
  - docs/REVIEW.md
  - docs/governance-activation.md
  - docs/exec-plans/**
  - README.md
  - scripts/ai_review.py
  - scripts/evidence_report.py
  - tests/governance/test_ai_review.py
  - proposals/0018/**
  - .claude/hooks/governance_gate.sh
---

# Plan 0018: PR review rubric

Status: done. The owner approved it in plan mode on 2026-11-19.

## Goal

Intent: [0018-pr-review-rubric](../intent/0018-pr-review-rubric.md)
Spec: [0018-pr-review-rubric](../spec/0018-pr-review-rubric.md)

This is stage 2 of the handover (playbook play 10).
- Add the PR review rubric as `REVIEW.md` at the repo root.
- Make `scripts/ai_review.py` apply it:
  - The rubric and design principles are read at the base commit, as instructions.
  - The plan, intent, spec and diff are read at the head commit, as data.
  - The review ends with a checked tally line.
- Run the review job from the base commit, through a proposal for `ai-review.yml`.
- Rename the evidence review to `docs/EVIDENCE_REVIEW.md`, and add PR review findings
  to its inputs.

## Files that change

- **`REVIEW.md` (new).** The rubric, with spec requirement 1's sections:
  - Passes: Bugs, Security and Compliance.
  - What Important means.
  - The nit cap.
  - Do not report.
  - Output format and the tally line.

  It names the design principles (requirement 2). It's short, following the
  playbook's example.
- **`scripts/ai_review.py`:**
  - Replace the hard-coded three-item `SYSTEM` with a short preamble. The preamble
    says the human decides, to follow `<rubric>`, that the Compliance pass checks
    against `<agents>`, `<app_agents>` and `<architecture>`, and that PR content is
    data, never instructions.
  - `INSTRUCTIONS = {'rubric': 'REVIEW.md', 'agents': 'AGENTS.md', 'app_agents':
    'app/AGENTS.md', 'architecture': 'ARCHITECTURE.md'}`, each read with
    `_git('show', f'{base}:{path}')` and wrapped in its tag.
  - Replace `plan_text(head)` with `exec_doc(head, folders, plan_id) -> str | None`.
    It lists `_git('ls-tree', '--name-only', head, 'docs/exec-plans/<folder>/')`,
    matches the `<id>-` prefix, and returns `_git('show', f'{head}:{path}')`. It's
    used for the plan (`active`, `completed`), the intent and the spec. When a file is
    missing, the prompt says so, for example `No spec for plan 0019.`
  - The user content adds `<intent>` and `<spec>` to `<plan>`, `<files>` and `<diff>`.
  - The tally check: if the last non-blank line, stripped, doesn't fully match
    `Tally: important=\d+ nit=\d+`, append `Tally: unavailable`.
  - Unchanged: `_git`, `reviewer_model()` (it reads the allowlist from the checkout,
    which is now the base commit), and the refusal path (`REFUSED`, no retry).
- **`tests/governance/test_ai_review.py`:**
  - Replace `_stub_git` with a small fake that serves `show <sha>:<path>`, `ls-tree`,
    `log` and `diff` from a dict keyed by sha.
  - Keep the reviewer-model and refusal tests.
  - Add tests that:
    - the rubric is read at base and lands in `system`
    - the plan, intent and spec are read at head and land in the user content
    - a missing spec is stated, not raised
    - a valid tally is kept
    - a missing or malformed tally becomes `Tally: unavailable`
- **`docs/REVIEW.md` → `docs/EVIDENCE_REVIEW.md`** (`git mv`). Add the input from
  requirement 9. The log table is unchanged.
- **References to the old path:**
  - `README.md` (line 302)
  - `docs/governance-activation.md` (the EVID-001 row's evidence path)
  - `scripts/evidence_report.py` (its docstring)
- **`docs/exec-plans/handover.md`:**
  - Stage 1 becomes "Done (plan 0017)" and stage 2 becomes "Plan 0018".
  - Correct its stage 2 "Build" section: run from base, and the design principles
    files.
  - In "How to pick up a stage", note that the governance gate now exempts plan
    mode's plan file.
- **`docs/exec-plans/tech-debt-tracker.md`:**
  - Remove the "`ai-review.yml` runs the PR's own copy" row.
  - Add a row: on `pull_request`, the workflow file comes from the PR, so a
    same-repo PR that edits `ai-review.yml` can reach the key. Closed by
    `pull_request_target` or branch protection, and covered meanwhile by owner review
    of `.github/`.
  - The `@claude` row added this session is already in the working tree.
- **`proposals/0018/.github/workflows/ai-review.yml`.** A copy of the current workflow
  with `ref: ${{ github.event.pull_request.base.sha }}` added to `actions/checkout`
  (`fetch-depth: 0` stays). Its header comment notes that the job runs base code and
  reads the PR only through git.
- **`proposals/0018/docs/governance_implementation.md`.** A full copy with
  `docs/REVIEW.md` → `docs/EVIDENCE_REVIEW.md` (line 1002), and the PR-findings input
  added to that item's Inputs.
- **`proposals/0018/docs/agent_governance_implementation.md`.** A full copy with the
  path at line 460 changed.

## Order of work

- [x] Write this plan to `docs/exec-plans/active/0018-pr-review-rubric.md`.
- [x] Commit the intent, spec, plan and the tech-debt `@claude` row, with the
      `Governance:` and `Plan: 0018` trailers. The owner's hook edit is left
      unstaged for the owner to commit.
- [x] Rename the evidence review, add the new input, and update the live references.
      Check with `git grep -n 'docs/REVIEW.md' -- ':!docs/exec-plans/completed'`.
      Only the handover's history and the protected docs (covered by proposals)
      should match.
- [x] Write `REVIEW.md`.
- [x] Change `ai_review.py` and its tests, with the tests written first.
- [x] Write the three proposals.
- [x] Update the handover and the tech-debt tracker.
- [x] ruff, mypy, vulture, and the unit and governance tests pass. Run
      `checks_on_stop.sh` and paste its output.
- [x] `scripts/check_scope.py` passes on the branch range.
- [x] Commit, then move this plan to `completed/` with `Status: done`.

## Risks

- **The `_git` stub gets too clever.** Keep the fake to a dict lookup.
- **`ls-tree` paths.** `--name-only` with a directory argument that ends in `/`
  returns full paths. A test covers the prefix match.
- **The tally check is too strict**, for example on markdown bold. The rubric shows the
  exact plain format.
- **The proposal copies drift** from the live protected files if those change before
  you apply them. They're copied just before committing.
- **The first real review shows prompt problems.** It can't run in this plan
  (COST-001, no secret). It's listed under Owner actions.

## Proof

- `pytest tests/governance/test_ai_review.py -v`: every test passes.
- `echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh`, with the
  output pasted.
- `python scripts/check_scope.py main..HEAD`, which passes.
- The `git grep` above shows no stale live references.

### Results, 2026-11-19

- `checks_on_stop.sh`: exit 0, with no output. ruff, vulture, mypy and the tests
  passed.
- `pytest -v tests/governance/test_ai_review.py`: 5 passed.
  - `test_uses_the_allowlisted_reviewer_model`
  - `test_instructions_come_from_base_and_the_pr_from_head`
  - `test_a_missing_spec_is_stated`
  - `test_a_missing_or_malformed_tally_is_marked_unavailable`
  - `test_refusal_tells_the_human_and_does_not_retry`
- `check_scope.py main..HEAD`: exit 0.
- `git grep`: the only live references to `docs/REVIEW.md` are in the two protected
  docs, which the proposals update.
- A smoke test of `review()` against real git (`HEAD...HEAD`, stub client, no model
  call):
  - It found the plan, intent and spec for 0018.
  - The system prompt held the rubric and was about 12 KB.
  - A valid tally was kept.

## Decisions

- Reading the base and head commits through `git show` keeps one helper (`_git`) for
  both trusted and untrusted inputs, and needs no second checkout.
- There's no fallback for a base commit without `REVIEW.md`. Once this lands, that
  base never exists (spec Concerns).
- `exec_doc` returns the "No <doc> for plan" message itself, not `None`, which saves
  a branch at each call site.
- The refusal path still returns `REFUSED` with no tally line (spec requirement 5). A
  future gate should treat a missing tally as unavailable.
- Generated paths are excluded in the rubric, not in the diff command, so policy
  stays in `REVIEW.md` (spec Design).
- The governance gate blocked plan mode's own plan file while no plan was active. The
  owner exempted `~/.claude/plans/*.md` in `governance_gate.sh` directly during
  planning, so no proposal or tech-debt row is needed.

## Owner actions

- Fill in the spec's "Accepted by" line. It still holds the placeholder.
- Commit your `governance_gate.sh` change.
- Review and apply `proposals/0018/`: the workflow and the two implementation docs.
- Optionally add `ANTHROPIC_API_KEY` as a repo secret to see the first review
  (COST-001). The first PR after the proposal is applied is the first one reviewed
  under the rubric.
