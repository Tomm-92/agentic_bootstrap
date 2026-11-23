# Spec 0022: auto mode evidence correction

Intent: [0022-auto-mode-evidence-correction](../intent/0022-auto-mode-evidence-correction.md)
Status: accepted
Accepted by: Thomas Wilkinson, 2026-11-23

<!-- Copy to docs/execution-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

The owner settled the intent's open questions on 2026-11-23: keep the auto-mode ban,
keep the tech-debt row, and the owner doesn't remember whether session `201c5890`
prompted.

1. **`agent_governance.md`, the auto-mode prerequisite** (lines 20 to 22), through
   `proposals/0022/docs/bootstrap-implementation/agent_governance.md`. The checkbox
   stays. Its reason reads:

   > Auto mode hasn't been shown to raise the paid-model prompt every time (COST-001).
   > Every run the owner watched did prompt, but too few runs have been watched to rely
   > on it.

   Nothing else in the file changes. The hook probe already asks the user whether the
   prompt appeared (lines 228 and 229).
2. **README, prerequisites** (lines 73 and 74). The ban stays. Its reason reads:
   "Auto mode hasn't been shown to ask before paid model calls every time (COST-001)."
3. **`AGENTS.md`, "Things agents get wrong"**, through `proposals/0022/AGENTS.md`. One
   line is added under the existing sentence:

   > - You can't see permission prompts. A command the user approved and one that ran
   >   without a prompt return the same result. Ask the user whether a prompt appeared;
   >   never report it yourself.

   The probe 0021 agent made this mistake twice, once in the main session and once
   through a subagent, which meets the file's "same mistake twice" test.
4. **`docs/bootstrapper_tech_debt_tracker.md`, the auto-mode row** (line 38). The row
   stays, with the same rule and fix columns. Its gap column reads:

   > Auto mode hasn't been shown to prompt every time for commands that match the
   > paid-model ask rules. Every run the owner watched prompted (three in auto mode, two
   > not), but probe 0021's first session reported "no prompt" from the agent's side
   > only, so it isn't evidence either way. Until it's tested, treat any auto-mode
   > session as one that might make paid calls without asking.
5. **Spec 0021** gets a dated correction under its Design section's "Probe 0021"
   paragraph, and the same one-line pointer under its Concerns bullet "Auto mode weakens
   a COST-001 control". The accepted text above them is unchanged. The note reads:

   > **Correction, 2026-11-23 (plan 0022).** The "no prompt" result in the first session
   > came from the agent, which can't see permission prompts. The owner didn't observe
   > it. Every run the owner watched prompted, including three in auto mode. Requirement
   > 6b stands, because auto mode hasn't been shown to prompt every time, not because it
   > was seen to fail.
6. Plan 0021 (completed) and intent 0021 are history and don't change.

## Design

The change is wording only. Each statement is reworded from "seen to fail" to "not shown
to be reliable" and names who observed what. The ban, the hook probe, the ask rules and
the TMW-19 fix all stay as they are.

The evidence is re-checked without spending anything: in this session, the owner
confirmed that both runs of `PYTHONPATH=. .venv/bin/python scripts/local_session.py
--real --help` prompted. The plan's Proof records that, plus the transcript excerpts
behind the intent's Problem section.

Rejected:
- **Dropping the ban.** The owner chose to keep it.
- **Rewriting spec 0021 in place.** It is accepted, and its history should show what
  was believed and when.
- **Changing `project_governance.md` stage 4**, which says an ask rule "prompts even in
  auto mode". That wording states the intended behaviour, and it now matches every
  observed run, so it stays.

## Out of scope

- The repo-wide fix (`disableAutoMode` in managed settings, or a PreToolUse hook that
  denies paid commands without approval). It stays with TMW-19.
- Any paid model call, and any change to `.claude/settings.json`, hooks or governance.
- Running TMW-24.

## Policies checked

- `governance/rules.yaml`:
  - GOV-002: `agent_governance.md` and `AGENTS.md` change only through `proposals/0022/`.
  - SCOPE-001 and SCOPE-002: plan 0022's `scope_paths` list the files in requirements 1
    to 5 and the plan files.
  - COST-001: no paid calls. The control is reworded, not weakened, and the ban stays.
  - GOV-004: commits carry the `Governance:` and `Plan: 0022` trailers, on `ai_sdlc`.
- `docs/records/security.md`: no data, secrets or access change.
- `app/AGENTS.md`: `app/` doesn't change.

## Concerns

- The new wording rests on five owner-observed runs, so it can't claim auto mode always
  prompts. It says only what was seen.
- `ai_sdlc` is 33 commits ahead of `main`. TMW-24 must run from a branch that has this
  change and 0021, as noted in the plan's owner actions.
