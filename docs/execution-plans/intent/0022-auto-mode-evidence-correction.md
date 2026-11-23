# Intent 0022: auto mode evidence correction

Author: Claude, drafted for the owner
Status: accepted
Accepted by: Thomas Wilkinson, 2026-11-23

<!-- Copy to docs/execution-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

## Problem

The repo says, as fact, that auto mode doesn't reliably raise the COST-001 paid-model
prompt: "in probe 0021, one auto-mode session prompted and another didn't." The
evidence doesn't support that.

- In probe 0021's first session (`201c5890`), `local_session --real --help` ran in the
  main session and in a subagent. The agent reported "no prompt" because the command
  returned output. The owner never said whether a prompt appeared. An agent can't see
  permission prompts: an approved command and an unprompted one return the same result.
- Every run the owner watched prompted: one in the probe's second session (auto mode),
  two on 2026-11-23 in session `ecbcd78b` (auto mode), and two on 2026-11-16 (not auto
  mode, per the activation ledger).

The wrong claim is in `agent_governance.md` (protected), the README, spec 0021 and the
tech-debt row in `docs/bootstrapper_tech_debt_tracker.md`. It contradicts
`project_governance.md` stage 4, which says an `ask` rule "prompts even in auto mode".
The owner, and agents reading these files, get a false reason for the auto-mode ban,
and the repo-wide fix (TMW-19) looks more urgent than the evidence shows.

## Proposed outcome

- Every statement about auto mode and the COST-001 prompt matches what was actually
  observed, and says who observed it.
- The auto-mode ban for the `agent_governance.md` run is either kept, with a reason
  that's true, or removed. The owner decides which.
- Agents are told that they can't see permission prompts, so they ask the owner instead
  of reporting whether one appeared.
- TMW-24 then runs from the corrected `agent_governance.md`.

## Affected users and systems

- The owner, when preparing the TMW-24 run.
- Coding agents that read `AGENTS.md`, the README and `agent_governance.md`.
- Docs: `docs/bootstrap-implementation/agent_governance.md` and `AGENTS.md` (both
  protected, changed through `proposals/0022/`), `README.md`, spec 0021,
  `docs/bootstrapper_tech_debt_tracker.md`.
- No code, governance rules or settings change.

## Constraints

- GOV-002: protected files change only through `proposals/0022/`, applied by the owner.
- SCOPE-001 and SCOPE-002: one plan, edits inside its `scope_paths`.
- COST-001: no paid model calls. Re-running the evidence uses only
  `local_session --real --help`, which exits before any model is called.
- Spec 0021 is accepted, so it gets a dated correction note, not a silent rewrite.
- Done before TMW-24, due 2026-11-29.

## Open questions

1. Keep the auto-mode ban for the run, with the reason reworded to "not shown to be
   reliable", or drop it? Claude recommends keeping it: it costs little, because the
   run stops for the owner at every step anyway.
2. Does the owner remember whether a prompt appeared in session `201c5890` for the two
   probe runs? If so, the record can say every observed run prompted.
3. Does the tech-debt row stay, reworded as an untested risk, or go? It follows from
   question 1.
