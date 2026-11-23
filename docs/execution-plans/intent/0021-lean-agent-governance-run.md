# Intent 0021: lean agent governance run

Author: Claude, drafted for the owner
Status: accepted
Accepted by: Tom Wilkinson, 2026-11-23

<!-- Copy to docs/execution-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

## Problem

Linear TMW-13. `docs/bootstrap-implementation/agent_governance.md` is the file the owner
runs to govern the product agent (README, "Getting started", step 4). As written, it
lets the coding agent that runs it add features, abstractions and work nobody asked for.
That makes the run slow, expensive in tokens and fragile, which hurts the owner. The
owner pays for the tokens, waits for the run, and then reviews everything the agent added.

How the file invites over-building:

- **One session runs all six parts.** Context and tokens build up from A01 to A06, and a
  failure late in the run puts all the earlier work at risk.
- **No agreed design before building.** The purpose interview goes straight to plan A00.
  No intent or spec settles the smallest agent that meets the purpose before code is
  written. The repo's own process requires both (README, "Development process").
- **Open-ended build items.** Some items give no point at which to stop, so the agent
  fills the gap:
  - "timebox an evaluation of ASH" (A02)
  - a sandbox image "holding the tools" (A02)
  - fixtures "for each output type" (A02)
  - eval sets across six categories (A04)
  - seeded CodeGuard rules (A05)
  - "Wherever possible, a deterministic generator or template" (A03)
- **One fixed role layout.** The file assumes a planner, an executor, a verify step and a
  reviewer. It doesn't say how a purpose that needs several agents fits that layout, so
  the agent invents its own structure.
- **Repeated text.** Parts of the file restate `project_governance.md` and the README.
  The agent reads them again in every session, which costs tokens.

## Proposed outcome

A proposed new `agent_governance.md` whose run quickly produces the simplest working
agent, or agents, with every required control. The result serves M1, and needs no
rebuild for M2 or M3.

- **The run follows the AI SDLC.**
  1. The purpose interview works with the user to agree what the agent or agents should
     do. It produces intent A00, which the user accepts.
  2. Spec A00 fixes:
     - the agent tree, whether one agent or several
     - its tools and their tiers
     - the verification stages
     - the minimal build of each control

     The user accepts the spec.
  3. The user applies a first proposal: the profile, `tools.yaml` and the allowlists
     from the spec. There is no proving repo (open question 1).
  4. Plan A00 is made in plan mode.
  5. The build runs one session per part, in five parts: A01 to A04, then A05 and A06
     merged (open question 2). Each part ends with a checkpoint commit, and the next
     session resumes from the first unticked part. Each session starts under the
     current governance hash, so GOV-006 holds.
- **"Simplest working version" is a written rule of the run.**
  - Build only what the accepted spec lists.
  - Build one implementation per stage, without evaluating alternatives.
  - Reuse ADK built-ins and the scripts, plugins and tests from `project_governance.md`
    before writing new code.
  - Add no options, configuration or abstraction beyond the spec.
  - Record anything else the agent thinks is needed in the tech-debt tracker, and don't
    build it.
- **Every part has limits.**
  - Each build item states a concrete minimum (open question 4).
  - Spec A00 lists the files each part may create or change (open question 3).
  - Acceptance criteria are the stop condition: when they pass, the part is done.
- **Every required control is still built:**
  - SPEC-001
  - SBX-001
  - SEC-002 (runtime)
  - VER-001
  - REV-001
  - DEP-001 (runtime)
  - DATA-001 (sandbox)
  - TOOL-001 (tool entries)
  - MODEL-001 (eval gate)
  - OBS-001 (intent attributes)

  OBS-001's attributes go out through the existing telemetry, so the observability stack
  sees them in M2.
- **The roles map onto an agent tree.** The file says how the planner, executor, verify
  and reviewer roles apply when the user wants several agents. M3 then extends the tree
  rather than rebuilding it.
- **Shorter text.** The file points to `project_governance.md` and the README instead of
  repeating them.

## Affected users and systems

- **The owner:** applies proposal 0021. Then, in the run, answers the interview,
  accepts intent A00 and spec A00, applies the first A00 proposal (profile, tools and
  allowlists), approves plan A00, and applies the final A00 proposal.
- **The coding agent that runs the file:** works under the new rules and limits.
- **`docs/bootstrap-implementation/agent_governance.md`:** protected, so it changes by
  proposal, in `proposals/0021/`.
- **`README.md`:** "Getting started" steps 2 to 5 describe the run.
- **Linear TMW-24:** runs the result. TMW-22 checks it against the new file.
- **Not affected until TMW-24 runs:** `app/`, `governance/` and the activation ledger.

## Constraints

- **GOV-002:** the new file goes in by proposal only.
- **COST-001:** no paid model calls while this change is drafted or built.
- **No weakening:** no control is weakened, no tier lowered and no ledger row dropped.
  Observability and evals stay in scope.
- **Generic:** the MVP agent's purpose isn't known yet, so the file must suit any output
  type.

## Open questions

The owner decided these on 2026-11-23. The spec turns them into requirements.

1. **The proving repo: dropped.** Once spec A00 is accepted, the user applies a small
   first proposal before the build starts: the profile, `tools.yaml` and the allowlists.
   Every part then runs against live governance. Each part already has its own session,
   so the hash change costs nothing. The final proposal still holds `rules.yaml`,
   `app/AGENTS.md` and the evals workflow, so the user still approves each control's
   activation. A later tier change needs its own small proposal (A00a).
   - Rejected: keeping the proving repo. It means an extra script, a fixture and a second
     tree, and it gives the agent the most room to over-build.
   - Rejected: applying in two batches after A01. That adds a second review point, and A01
     would still run with its new tools denied.
2. **Merging parts: only A05 and A06 merge.** Both are mostly docs and ledger work, and
   neither builds a rule control. Merging them saves one session without changing
   `rules.yaml` or the ledger's part tags.
   - Rejected: merging A02 and A03. It creates the largest session, and it needs a
     renumbering proposal.
   - Rejected: building a rough end-to-end version first and filling in the controls
     later. It rewrites the file's structure and adds stub code that gets replaced.
3. **The size budget: a file list per part.** Spec A00 names the files each part creates
   or changes. A part that needs a file not on the list stops and asks, and the plan is
   amended. This catches new modules, helpers and config, which is where most of the
   added complexity comes from.
   - Rejected: a line-count limit. The numbers would be arbitrary, and code gets squeezed
     to fit.
   - Rejected: a token budget. The agent can't see its own token count.
   - Rejected: no budget at all. Nothing would catch work beyond the minimums.
4. **Exact minimums: fixed in the file.** Categories that don't apply to the profile are
   skipped.
   - **Fixtures:** one good output per output type, plus one planted failure for each
     gate outcome (block, acknowledge and intent mismatch).
   - **Evals:** at most one case per category:
     - the happy path
     - an out-of-scope request
     - prompt injection
     - a non-allowlisted dependency or target (only when the profile has package
       ecosystems or external targets)
     - a path escape
     - budget exhaustion

     That is at most 6 cases × `eval_runs` (5), or 30 paid calls for each gate run.
   - **Output specs:** the operational requirements for the output type, plus the
     requirements spec A00 names. No generator or template unless the spec lists one.
   - Rejected: deriving the minimums from the ledger alone. With no case for the agent's
     real job, the MODEL-001 gate would measure very little.
   - Rejected: letting spec A00 decide under a ceiling. The agent would propose the list
     on every run, which is where it over-reaches.
