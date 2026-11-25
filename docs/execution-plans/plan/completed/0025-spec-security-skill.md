---
id: '0025'
rules: [GOV-002, GOV-004, GOV-006, COST-001, SEC-001, SEC-002, MODEL-001, REV-001, SCOPE-001, SCOPE-002]
scope_paths:
  - proposals/0025/**
  - scripts/ai_review.py
  - tests/governance/**
  - REVIEW.md
  - README.md
---

# Plan 0025: spec-security skill, and /intent and /spec

Status: done. The owner approved it in plan mode on 2026-11-25.

<!-- Written to docs/execution-plans/plan/active/<ID>-<name>.md when the owner approves it
in plan mode. Moved to docs/execution-plans/plan/completed/ when done. -->

## Goal

Intent: [0025-spec-security-skill](../../intent/0025-spec-security-skill.md)
Spec: [0025-spec-security-skill](../../spec/0025-spec-security-skill.md)

This is stage 5 of the handover (playbook plays 05 and 02, Linear TMW-18). The security
policy is written once, in `.claude/skills/spec-security/checklist.md`, and each stage has
one reviewer: `spec-security` for specs, and the CI review for diffs. The built-in
`/security-review` is switched off. `/intent` and `/spec` serve every change in the
project, and Claude can start them itself. `/spec` always runs `spec-security`.

## Files that change

- `proposals/0025/.claude/skills/spec-security/SKILL.md`: new. Specs only. Its
  description says diffs belong to the CI review.
- `proposals/0025/.claude/skills/spec-security/checklist.md`: new. One section per rule
  (SEC-001, SEC-002, DATA-001, DEP-001, TOOL-001, FS-001, SBX-001), each with Spec, Diff,
  "Enforced by" and "Not yet enforced" lines. Then one "Already enforced, don't report"
  list: gitleaks, pip-audit and osv-scanner (`.github/workflows/governance.yml`), Bandit
  through ruff `S`, `tests/unittests/test_tool_policy.py` and
  `tests/governance/test_observability.py`.
- `proposals/0025/.claude/skills/intent/SKILL.md` and `.../spec/SKILL.md`: new, with no
  `disable-model-invocation`. `/spec` refuses to start unless the intent has both
  acceptance lines set.
- `proposals/0025/.claude/settings.json`: the current file plus
  `"skillOverrides": {"security-review": "off"}`, and nothing else changed.
- `scripts/ai_review.py`: add `'security': '.claude/skills/spec-security/checklist.md'`
  to `INSTRUCTIONS`, and name `<security>` in `SYSTEM` as what the Security pass checks
  against.
- `tests/governance/test_ai_review.py`: the fake base commit gains the checklist, and
  `test_instructions_come_from_base_and_the_pr_from_head` asserts its text is in the
  system prompt.
- `tests/governance/test_skills.py`: new. For each `.claude/skills/*/SKILL.md`, the
  frontmatter `name` matches its folder and `description` isn't empty. Every
  `[A-Z]+-\d{3}` ID in the checklist exists in `governance/rules.yaml`, and all seven
  security rules are covered. Every backticked repo file path (one with an extension) in
  the skills and the checklist exists. `.claude/settings.json` sets `security-review` to
  `off`.
- `REVIEW.md`: the Security pass says to apply the checklist's Diff lines and keeps no
  list of its own. "Do not report" drops gitleaks, pip-audit and osv-scanner and points to
  the checklist's list.
- `docs/execution-plans/templates/spec.md`: "Policies checked" names `spec-security`.
- `README.md`: the review-commands table gains `spec-security`, `/intent` and `/spec`, and
  one line says which reviewer covers which stage and that `/security-review` is off.
- `docs/execution-plans/handover.md`: stage 5 marked done, with an "As built" note.

## Order of work

- [x] Write this plan to `docs/execution-plans/plan/active/0025-spec-security-skill.md`.
      Commit it with the intent and spec.
- [x] Write the five `proposals/0025/` files. Commit them.
- [x] **Pause for the owner:** apply `proposals/0025/`, delete it, and commit.
- [x] Commit the `test_ai_review.py` change on its own, giving the plan as the reason. Then
      commit the `ai_review.py` change. Both go in one turn, so the checks pass at the
      turn's end.
- [x] Commit `tests/governance/test_skills.py`, which is a new test.
- [x] Commit `REVIEW.md`, the spec template, the README and the handover.
- [x] ruff, mypy, vulture, and the unit and governance tests pass. The `verifier` reports
      the output.
- [x] Move this plan to `completed/`, after every other edit.

## Risks

- **The settings proposal could drop or change an existing key.** The owner's diff of
  `proposals/0025/.claude/settings.json` against the live file should show one added
  key. `tests/governance/test_settings.py` catches lost deny rules or hooks.
- **The test could land before the skills exist.** `test_skills.py` would fail. The pause
  for the owner comes first.
- **The model may not start the skills.** Skills are advisory. A fresh-session check
  covers listing only. Checking the chain is deferred (intent question 3).
- **The path check could be too broad.** Matching only paths with an extension keeps out
  `output/` and the `.venv` folder that `adk-review` cites.

## Proof

Results, 2026-11-25:
- The `verifier` ran CI's check command,
  `echo '{"force": true}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh`:
  exit code 0, no output. No `app/` change, so no scripted session.
- The scope check, `.venv/bin/python scripts/check_scope.py "579bdea..HEAD"`: exit code
  0, no output.
- `.venv/bin/pytest tests/governance/test_skills.py -q`: 11 passed.
  `tests/governance/test_ai_review.py`: 5 passed.
- Outstanding: the owner's fresh-session check below.

Planned:

- The `verifier` output after the last commit.
- `.venv/bin/pytest tests/governance/test_skills.py tests/governance/test_ai_review.py -q`.
- The owner, in a fresh session after applying: `/security-review` isn't offered, and
  `/spec-security`, `/intent` and `/spec` are.

## Decisions

- The `security-review` override is checked in a new `test_skills.py`, not in
  `test_settings.py`, so no existing test changes for it.
- The checklist covers spec and diff in one file, so `REVIEW.md` holds no security list
  (spec requirement 1).
- The path check covers only backticked paths that contain a `/` and end in a file
  extension. Bare names such as `checklist.md` (beside its skill), `__init__.py` (cited
  by `adk-review`) and `verify.sh` (planned in A02) aren't repo-root paths.

## Owner actions

- Done, 2026-11-25: the owner applied `proposals/0025/` (commit "Apply proposal 0025",
  amended to add the skills and settings after the first `git add` failed on the deleted
  proposal path).
- Open a fresh session and confirm the skills listing described under Proof.
