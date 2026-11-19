---
id: '0017'
rules: [GOV-002, GOV-004, GOV-006, SCOPE-001, SCOPE-002]
scope_paths:
  - docs/exec-plans/**
  - proposals/0017/**
  - README.md
  - scripts/check_scope.py
  - tests/governance/test_check_scope.py
---

# Plan 0017: make intent → spec → plan, started in plan mode, the default process

Status: draft, awaiting owner approval.

## Goal

Make the AI-native SDLC playbook's
(https://claude.com/resources/articles/the-ai-native-sdlc-playbook) committed-artifact
chain this repo's default way of working. Every change starts as an `intent.md`. The
intent is accepted, then turned into a `spec.md`. The spec is accepted, then turned
into a `plan.md` in Claude Code's plan mode. Only then is anything built. This is
stage 1 of the six stages in the gap analysis: process docs only. Later stages add the
PR review rubric, subagents, evals, policy skills and loop closing.

This plan comes before the process it defines, so it has no intent or spec of its own.
The intent is this Goal.

## How the playbook's artifacts map to this repo

| Playbook | Here | Accepted by | Acceptance starts |
| --- | --- | --- | --- |
| `intent.md` | `docs/exec-plans/intent/<ID>-<name>.md` | Owner sets `Status: accepted` | Writing the spec |
| `spec.md` | `docs/exec-plans/spec/<ID>-<name>.md` | Owner sets `Status: accepted` | Plan mode |
| `plan.md` | `docs/exec-plans/active/<ID>-<name>.md` (unchanged) | Owner approves the plan when Claude leaves plan mode | Building |

All three share one ID and name, so plan 0018 is built from intent 0018 and spec 0018.

## Files that change

- `docs/exec-plans/templates/intent.md`: new. It has a header (Author, Status, Accepted by
  and date) and the playbook's sections: Problem, Proposed outcome, Affected users and
  systems, Constraints, Open questions.
- `docs/exec-plans/templates/spec.md`: new. It has a header (Intent link, Status,
  Accepted by and date) and these sections: Requirements, Design, Out of scope,
  Policies checked (`governance/rules.yaml`, `docs/SECURITY.md`, `app/AGENTS.md` where
  `app/` changes), and Concerns. Concerns uses the playbook's prompt: "Describe clearly
  any areas of concern, especially where you cannot satisfy contradicting policies."
- `docs/exec-plans/templates/plan.md`: new. It has the front matter the gate reads (`id`,
  `rules`, `scope_paths`), then Goal (linking the intent and spec), and the playbook's
  sections: Files that change, Order of work (a checklist), Risks, Proof. It keeps this
  repo's Decisions and Owner actions sections.
- `docs/exec-plans/intent/.gitkeep` and `docs/exec-plans/spec/.gitkeep`: new.
- `scripts/check_scope.py`: `_plan_globs` matches `docs/exec-plans/*/<ID>-*.md`. That
  pattern would also match intent and spec files, which have no front matter. Limit it
  to `active/` and `completed/`, as `ai_review.py` and `check_trailers.sh` already do.
- `tests/governance/test_check_scope.py`: add a test that an intent and a spec with the
  plan's ID don't stop the plan's scope being found.
- `README.md`:
  - Add a "Development process" section under "How it works". It describes the loop,
    who accepts each artifact, the small-change exemption, and the plan-mode steps
    (below).
  - Rewrite "Execution plans" to point to the templates.
  - Replace "Workflow for each feature" with a pointer to the new section, keeping its
    review-command steps.
  - Add intent and spec to the Transparency paragraph.
  - Say that `intent.md` (a change to this repo) is a different thing from the product
    agent's "intent artifact" (what its users approve, SPEC-001).
- `proposals/0017/AGENTS.md`: under "Before changing anything", read the active plan's
  intent and spec too. Under "While working", never set `Status: accepted` on an intent
  or spec, because only the owner accepts. Add a short "Things agents get wrong"
  section with the rule: when an agent makes the same mistake twice, propose a line for
  it there. Update the Layout line for `docs/`.
- `proposals/0017/CLAUDE.md`: start every change in plan mode, and write the approved
  plan to `docs/exec-plans/active/` from the template.
- `proposals/0017/.claude/settings.json`: add `"defaultMode": "plan"` under
  `permissions`, so every session starts in plan mode. Change nothing else.
- `docs/exec-plans/tech-debt-tracker.md`: add the gaps under Risks.

### Plan-mode steps for the README

1. Start Claude Code in plan mode: `claude --permission-mode plan`, or Shift+Tab. Once
   the settings proposal is applied, this is the default.
2. Ask it to plan from the accepted spec, for example: *"Plan the change in
   docs/exec-plans/spec/0018-x.md."*
3. Question the plan before you accept it. Ask what could break, which step is
   riskiest, and which options it didn't take. Iterate until an engineer who never saw
   the conversation could build the change from the plan alone.
4. Approve it. Claude leaves plan mode and writes the plan to
   `docs/exec-plans/active/` from the template. The edit gate exempts plan files.
   Review the file, then commit the intent, spec and plan together.
5. Build in the same session, or in a new one (GOV-006: one plan per session). When
   the build departs from the plan, update the plan in the same commit.

## Order of work

- [ ] `scripts/check_scope.py` and its test. Prove the new test fails before the fix.
- [ ] The three templates and the two `.gitkeep` files.
- [ ] `README.md`.
- [ ] The three proposals. Each copies the live file and changes only what's listed
      above. Check that `tests/governance/test_settings.py` still passes with the
      proposed `settings.json` in place, then restore the live file.
- [ ] Tech-debt entries.
- [ ] ruff, mypy, vulture, and the unit and governance tests pass.
- [ ] Move this plan to `completed/`.

## Proof

- `.venv/bin/pytest tests/governance` passes. The new scope test fails on the current
  `check_scope.py` and passes after the fix.
- `git ls-files docs/exec-plans/templates docs/exec-plans/intent docs/exec-plans/spec`
  lists the three templates and the two `.gitkeep` files.
- `diff AGENTS.md proposals/0017/AGENTS.md`, and the same for `CLAUDE.md` and
  `.claude/settings.json`, shows only the listed changes.

## Decisions

These settle the open questions from the gap analysis. The owner can overrule any of
them when approving this plan.

- **Plans keep their place.** The gate, `check_scope.py`, `check_trailers.sh` and
  `ai_review.py` all find plans in `active/` and `completed/`. Moving plans into a
  per-change folder would mean changing protected hooks for no gain. The plan file is
  the playbook's `plan.md`.
- **Intents and specs live under `docs/exec-plans/`.** The edit gate exempts that path,
  so they can be drafted before any plan exists, which is the point of an intent.
- **The first commit holds all three.** `commit-msg` and CI need a `Plan:` trailer that
  names a plan in `active/` or `completed/`. So an intent can't be committed on its own
  yet. Acceptance is recorded in each file's header (who and when), and the intent,
  spec and plan are committed together. Separate commits per gate need a change to
  `check_trailers.sh`, which is deferred to the tech-debt tracker.
- **Small changes skip the intent and spec.** That covers fixes that restore documented
  behaviour, doc corrections and dependency bumps. The plan's Goal says
  `Intent: none (<reason>)`. Everything else, including changes to governance and the
  process, starts with an intent.
- **One owner plays every role.** The playbook's product owner, policy owner and tech
  lead are all the owner here. The README says so, rather than inventing roles.
- **"Things agents get wrong" stays in `AGENTS.md`**, which is protected, so each
  addition is a proposal. That costs a little friction and keeps GOV-002 whole. It's in
  `AGENTS.md` rather than `CLAUDE.md`, so every coding agent reads it.
- **Plan mode is the default through `defaultMode: plan`.** It's the only change in the
  settings proposal, so the owner can skip it and keep the rest.
- **No skills or slash commands yet.** `/intent` and `/spec` commands belong to stage 5
  (policy skills). Templates come first.
- **`docs/REVIEW.md` stays as it is.** Renaming it belongs to stage 2, the PR review
  rubric.
- **Existing completed plans aren't rewritten** to the new sections.

## Risks

- Nothing enforces the chain. A plan can skip its intent, and an agent could set
  `Status: accepted` itself. Mitigations: the `AGENTS.md` rule, owner review, and a
  tech-debt entry for a later CI check that every new plan links an accepted intent
  and spec, or gives an exemption reason.
- Nothing checks that the plan stays in sync with the diff. The playbook suggests a
  hook. This goes in the tech-debt tracker, and `ai_review.py` already flags
  departures from the plan.
- "Intent" could be confused with the product agent's intent artifact. The README
  section names the difference.
- With `defaultMode: plan`, sessions that only need to answer a question also start in
  plan mode. Plan mode is read-only, so the only cost is pressing Shift+Tab.
- With `defaultMode: plan`, tools that start Claude Code non-interactively are
  unaffected only if they pass their own `--permission-mode`.

## Owner actions

1. Review this plan, and change or approve the decisions above.
2. After the session that builds it: review `proposals/0017/`, then apply it and commit
   with `Plan: 0017`:

   ```sh
   cp -R proposals/0017/. . && rm -rf proposals/0017
   ```

   Changing `AGENTS.md` and `CLAUDE.md` doesn't change the governance hash, so open
   sessions keep working. They pick up the new instructions only when restarted.
