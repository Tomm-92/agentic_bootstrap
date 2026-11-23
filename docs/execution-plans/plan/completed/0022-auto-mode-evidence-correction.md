---
id: '0022'
rules: [GOV-002, GOV-004, COST-001, SCOPE-001, SCOPE-002]
scope_paths:
  - docs/execution-plans/**
  - proposals/0022/**
  - README.md
  - docs/bootstrapper_tech_debt_tracker.md
---

# Plan 0022: auto mode evidence correction

## Goal

Intent: [0022-auto-mode-evidence-correction](../../intent/0022-auto-mode-evidence-correction.md)
Spec: [0022-auto-mode-evidence-correction](../../spec/0022-auto-mode-evidence-correction.md)

The repo says probe 0021 saw auto mode skip the COST-001 prompt. That "no prompt" came
from the agent, which can't see prompts; every run the owner watched prompted. This
plan rewords each statement to match the evidence, keeps the auto-mode ban and the
tech-debt row, and adds an AGENTS.md line so agents ask instead of guessing. It must
land before TMW-24.

## Files that change

- `proposals/0022/docs/bootstrap-implementation/agent_governance.md`: full copy of the
  file with lines 20 to 22 reworded (spec requirement 1). Nothing else differs.
- `proposals/0022/AGENTS.md`: full copy with one line under "Things agents get wrong"
  (requirement 3).
- `README.md`: lines 73 and 74, the ban's reason (requirement 2).
- `docs/bootstrapper_tech_debt_tracker.md`: line 38's gap column (requirement 4).
- `docs/execution-plans/spec/0021-lean-agent-governance-run.md`: the correction note
  after the "Probe 0021" paragraph and a pointer under the Concerns bullet
  (requirement 5).
- This plan, intent 0022 and spec 0022.

## Order of work

- [x] Commit intent 0022, spec 0022 and this plan together on `ai_sdlc` (the commit-msg
      hook needs a `Plan:` trailer naming an existing plan).
- [x] Edit `README.md`, the tech-debt row and spec 0021. Commit.
- [x] Write `proposals/0022/` (copy each protected file, then edit the copy). Check with
      `diff` that each copy differs from its original only in the spec's lines. Commit.
- [x] `grep -rn "one auto-mode session prompted"` finds only intent 0022, spec 0022,
      plan 0021 and spec 0021's original text.
- [x] ruff, mypy, vulture, and the unit and governance tests pass (verifier subagent).
- [x] Move this plan to `completed/`. Commit.

## Risks

- The proposal copies drift from their originals if either changes before the owner
  applies them. The `diff` check in Proof shows the intended difference at commit time.
- A sentence could still overstate the evidence. Each new passage is the spec's
  accepted wording, copied verbatim.

## Proof

- Owner, 2026-11-23, session `ecbcd78b`, auto mode: both runs of
  `PYTHONPATH=. .venv/bin/python scripts/local_session.py --real --help` prompted.
- Transcript `201c5890`: the agent wrote "Step 5 ran without the COST-001 prompt"
  after seeing only the command's output; no owner message reports a missing prompt.
- `diff docs/bootstrap-implementation/agent_governance.md proposals/0022/docs/bootstrap-implementation/agent_governance.md`:

  ```text
  21,22c21,22
  <       doesn't reliably raise the paid-model prompt (COST-001). In probe 0021, one
  <       auto-mode session prompted and another didn't.
  ---
  >       hasn't been shown to raise the paid-model prompt every time (COST-001). Every run
  >       the owner watched did prompt, but too few runs have been watched to rely on it.
  ```

- `diff AGENTS.md proposals/0022/AGENTS.md`:

  ```text
  30a31,34
  > - You can't see permission prompts. A command the user approved and one that ran
  >   without a prompt return the same result. Ask the user whether a prompt appeared;
  >   never report it yourself.
  >
  ```

- `grep -rn "one auto-mode session prompted"` (excluding `.venv`, `.git`): only intent
  0022 and this plan. Plan 0021 and spec 0021 word it differently, and the protected
  original splits it across lines; the proposal replaces that text.
- Verifier: `rm -f .claude/.checks_fingerprint && echo '{}' |
  CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh` exited 0 with no output (all
  checks passed). `app/` is unchanged, so no scripted session ran. No paid calls.

## Decisions

- Keep the auto-mode ban, reworded to "not shown to be reliable" (owner, 2026-11-23).
- Keep the tech-debt row, reworded as an untested risk (owner, 2026-11-23).
- Spec 0021 gets a dated note, not a rewrite, because it is accepted.

## Owner actions

- Review and apply `proposals/0022/`:

  ```bash
  cp -R proposals/0022/. . && rm -rf proposals/0022
  git add -A && git commit -m "Apply proposal 0022" \
    -m "Governance: $(git rev-parse HEAD:governance)
  Plan: 0022"
  ```

- Run TMW-24 from a branch that contains 0021 and 0022: merge `ai_sdlc` into `main`
  first, or start the design session on `ai_sdlc`. Run it outside auto mode.
