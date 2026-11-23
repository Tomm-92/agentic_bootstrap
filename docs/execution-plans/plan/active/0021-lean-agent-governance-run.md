---
id: '0021'
rules: [GOV-002, GOV-004, GOV-006, COST-001, EVID-001, SCOPE-001, SCOPE-002]
scope_paths:
  - docs/execution-plans/**
  - proposals/0021/**
  - README.md
  - docs/bootstrap-implementation/initial_install.md
  - docs/tech_debt_tracker.md
  - docs/bootstrapper_tech_debt_tracker.md
  - docs/agent_tech_debt_tracker.md
  - docs/records/evidence_review.md
  - scripts/evidence_report.py
  - tests/governance/test_evidence_report.py
---

# Plan 0021: lean agent governance run

Status: in progress. The owner approved it in plan mode on 2026-11-23.

<!-- Written to docs/execution-plans/plan/active/<ID>-<name>.md when the owner approves it
in plan mode. Moved to docs/execution-plans/plan/completed/ when done. -->

## Goal

Intent: [0021-lean-agent-governance-run](../../intent/0021-lean-agent-governance-run.md)
Spec: [0021-lean-agent-governance-run](../../spec/0021-lean-agent-governance-run.md)

This plan is Linear TMW-13. It proposes a new `agent_governance.md` whose run stops the
coding agent adding complexity, and still builds every required control, working with
observability and growing into a multi-agent tree for M2 and M3. The run becomes:

1. A design session: purpose interview, intent A00, spec A00, plan A00, and a first
   proposal for the profile, tools and allowlists.
2. The owner applies the first proposal.
3. A build session runs one subagent per part, A01 to A05, behind a hook probe, with a
   verifier call in every part.

It also splits the tech-debt tracker into a bootstrapper tracker and an agent tracker.
Three protected files change, all by proposal in `proposals/0021/`.

## Files that change

- **`proposals/0021/docs/bootstrap-implementation/agent_governance.md` (new; spec 1–16).**
  A rewrite in the spec's section order, at most 437 lines (70% of 625):
  - **Purpose and prerequisites.** These come from today's "Before you start". They add
    a session that isn't in auto mode (6b).
  - **How to run this file.**
    - The two prompts: *"Run the design session in
      docs/bootstrap-implementation/agent_governance.md"* and *"Build plan A00"*.
    - The command that applies the first proposal (4).
    - Resuming.
  - **Rules for the run.**
    - Today's run rules, kept short, minus the proving-repo items.
    - The simplest-working-version limits (8), the file-list budget (9) and the stop
      conditions (11).
    - The tracker test (22).
    - "When a part can't finish", kept as it is.
  - **Design session (3).**
    - The interview table from today's "Purpose inputs", plus an agent tree row (12).
    - Then intent A00, spec A00 (with the spec's required contents, including the
      minimums from requirement 10), plan A00, the first proposal and one commit.
  - **Build session (6, 6a).** The orchestrator steps, the duties of each part's subagent,
    and the hook probe's four checks with their expected results.
  - **Parts A01 to A05 (15).** Each part keeps Goal, Rules, Build, Acceptance criteria and
    Ledger, with its build items cut to the spec's minimums:
    - A01: `add_dependency`, and the live-profile test.
    - A02: one tool per stage, no ASH, and the fixture minimums.
    - A03: the fixed-role tree, with verify as a tool.
    - A04: the eval minimums, intent attributes through the existing telemetry and one
      alert (14).
    - A05: today's A05 and A06 merged, without `rules-additions.yaml`.
  - **After the run.** Today's steps. Step 2 (rules additions) is dropped, and the apply
    step covers only the final proposal (7).
  - **Appendices A and B.** Kept, trimmed to the profile examples.
  - **Pointers instead of copies.** Wherever today's text restates `project_governance.md`,
    the README or `AGENTS.md`, it is replaced by a pointer (2).
- **`proposals/0021/AGENTS.md` (spec 23).** A copy of `AGENTS.md`. Lines 21–22 name both
  trackers and the test from requirement 22. The layout block at line 121 lists both
  files.
- **`proposals/0021/docs/bootstrap-implementation/project_governance.md` (spec 23).** A copy
  with three line changes: line 253 and line 2178 name
  `docs/bootstrapper_tech_debt_tracker.md`, and line 2192 reads "A01 to A05".
- **Tracker split (spec 19, 21, 22):**
  - `git mv docs/tech_debt_tracker.md docs/bootstrapper_tech_debt_tracker.md`.
  - In the renamed file, row 17 reads "A01 to A05", and one new row records auto mode's
    unreliable COST-001 prompt.
  - New `docs/agent_tech_debt_tracker.md`: a header, one line saying what belongs here,
    and an empty `Gap | Rule | Close by` table.
- **`scripts/evidence_report.py` (spec 24).** `_plans` counts both trackers and prints
  `Tech-debt entries: bootstrapper <n>, agent <n>.`, with a missing file counting 0. It
  loops over the two names inline, with no helper.
- **`tests/governance/test_evidence_report.py` (spec 24).** A new test: a repo with one row
  in each tracker reports `bootstrapper 1, agent 1`. No existing test changes.
- **`docs/records/evidence_review.md` (spec 23).** Line 12 lists both trackers.
- **`docs/execution-plans/handover.md` (spec 20, 23).**
  - Line 225 reads "A01 to A05".
  - Its mentions of "the tech-debt tracker" say "the bootstrapper tech-debt tracker".
- **`README.md` (spec 17).** "Getting started" steps 2 to 5 describe:
  - the design session
  - applying the first proposal
  - the build session and its subagents
  - no auto mode

  It also gets the two new prompts.
- **`docs/bootstrap-implementation/initial_install.md` (spec 18).** Line 12 gives the
  design-session prompt.

## Order of work

- [ ] Write this plan to `docs/execution-plans/plan/active/0021-lean-agent-governance-run.md`.
      Commit the intent, spec and plan together, with the trailers
      (`Governance: <git rev-parse HEAD:governance>`, `Plan: 0021`).
- [ ] Split the tracker:
      - `git mv`, then the row 17 edit and the auto-mode row.
      - The new agent tracker.
      - `evidence_review.md` and the handover.
      - `evidence_report.py` and its new test.

      Commit.
- [ ] Write the `AGENTS.md` and `project_governance.md` proposals (copy, then edit only the
      named lines). Check with `diff` that only those lines differ. Commit.
- [ ] Write the new `agent_governance.md` proposal. Check:
      - `wc -l` gives at most 437 lines.
      - Every spec requirement from 1 to 16 maps to a section. Record the map in Proof.

      Commit.
- [ ] Update `README.md` and `initial_install.md`. Commit.
- [ ] Ask the `verifier` subagent to run ruff, mypy, vulture, and the unit and governance
      tests. Paste its output into Proof.
- [ ] Finish every edit, then move this plan to `completed/` and commit. With no active
      plan, the gate blocks later edits.

## Risks

- **The rewrite drops something a control needs.** It would show as a missing build item
  for a `pending` ledger row. Proof gets a table of requirement → section, and a ledger
  row → part map for every `pending` row.
- **The `project_governance.md` copy drifts from the original.** `diff` must show exactly
  three changed lines.
- **The rename breaks a link.** `grep -rn tech_debt_tracker.md` outside the history
  (completed plans, and the 0018 intent and spec) must show only the new names.
- **The evidence report test is brittle in the row count.** `count('\n| ') - 2` assumes a
  header and a separator row. The new test builds the trackers in that same shape.

## Proof

Filled in while building:
- the requirement → section map
- the ledger row → part map
- the `diff` output for both copied protected files
- `wc -l` for the new file
- the `grep` for old tracker links
- the verifier's output

## Decisions

- The plan scope lists exact paths, as the new file will require of plan A00.
- The `project_governance.md` and `AGENTS.md` proposals are full copies. That is the
  repo's proposal format, and `scripts/check_scope.py` counts the files in the proposal
  folder.
- The existing tracker rows all stay in the bootstrapper tracker (spec, Out of scope).

## Owner actions

1. Review `proposals/0021/`. Diff each copied file against the live one, and read the new
   `agent_governance.md` in full.
2. Apply the proposal in one commit, which also deletes `proposals/0021/`:

   ```bash
   cp -R proposals/0021/. . && rm -rf proposals/0021
   git add -A && git commit -m "Apply proposal 0021" \
     -m "Governance: $(git rev-parse HEAD:governance)" -m "Plan: 0021"
   ```

3. TMW-24 then runs the new file. Its design session and build session must not be in
   auto mode.
