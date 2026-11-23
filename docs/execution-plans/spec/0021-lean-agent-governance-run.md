# Spec 0021: lean agent governance run

Intent: [0021-lean-agent-governance-run](../intent/0021-lean-agent-governance-run.md)
Status: accepted
Accepted by: Tom Wilkinson, 2026-11-23

<!-- Copy to docs/execution-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

### The new file

1. `proposals/0021/docs/bootstrap-implementation/agent_governance.md` replaces the current
   file. The owner applies it. Its sections, in order:
   1. Purpose and prerequisites
   2. How to run this file
   3. Rules for the run
   4. Design session
   5. Parts A01 to A05
   6. After the run
   7. Appendices A and B
2. **Shorter text.** The new file states each fact once and points to
   `project_governance.md` or the README instead of repeating them. The target is a file
   at most 70% of today's 625 lines, with no requirement below dropped to reach it.

### The run follows the AI SDLC

3. **The design session** comes first, in its own session, and builds no code. In order:
   1. **Purpose interview.** It keeps today's interview: the purpose and the output first,
      then one input at a time with a recommendation, then a single confirmation. It adds
      one input, the **agent tree**. The interview recommends the smallest tree that meets
      the purpose, using requirement 12.
   2. **Intent A00**, written to `docs/execution-plans/intent/A00-agent-purpose.md` from the
      template. It holds the confirmed purpose inputs. The run stops until the user sets
      `Status: accepted` and `Accepted by:`.
   3. **Spec A00**, written to `docs/execution-plans/spec/A00-agent-purpose.md`. It fixes:
      - the agent tree, and each agent's tools, with their tiers
      - the verification stages, mapped to one concrete tool each
      - the eval cases and fixtures, using requirement 10
      - the file list for each part, using requirement 9

      The run stops until the user accepts it.
   4. **Plan A00**, made in plan mode on the branch `governance-agent-purpose`. Its
      `scope_paths` come from requirement 9.
   5. **First proposal.** The run writes `proposals/A00/governance/profile.yaml`,
      `governance/tools.yaml` and `governance/allowlists/*` from spec A00.
   6. **One commit** holds the intent, spec, plan and first proposal, with the
      `Plan: A00` trailer. The session then stops.
4. **The user applies the first proposal** on the branch before A01, with one command and
   a commit. "How to run this file" gives both. `scripts/check_scope.py` already passes a
   commit that applies a proposal. From then on, every part runs against live governance.
5. **The proving repo is removed.** No `scripts/proving_repo.sh` and no overlay fixture.
   Unit tests that need changed governance use the existing `governed_repo` fixture in
   `tests/unittests/conftest.py`. Integration runs use the real tree.
6. **The build session runs one subagent per part.** After the user applies the first
   proposal, the user starts one new session, the **build session**, with *"Build plan
   A00"*. The governance hash is now final for the build, so GOV-006 holds for the whole
   session. The build session is the orchestrator, and it:
   1. Runs the **hook probe** (requirement 6a) and stops if any probe fails.
   2. For each unticked part in plan A00, in order, starts one fresh `general-purpose`
      subagent. The subagent's prompt names the part, plan A00 and spec A00, and
      nothing else from the conversation. The build session waits for it to finish.
      Parts never run in parallel.
   3. Reads the subagent's report, and checks that the part is ticked, that its ledger
      rows are updated and that its checkpoint commit exists. Then it starts the next
      part.
   4. When a subagent reports that it stopped to ask, the build session asks the user,
      records the answer in plan A00's Decisions, and starts a new subagent for the same
      part. The new subagent resumes from the plan. The user's answer always comes from
      the user, never from a subagent's report.
   5. Stops after A05, or on a `failed` part, and gives the final report.

   **Each part's subagent:**
   - Re-reads `governance/rules.yaml`, plan A00 and spec A00, and builds only its part.
   - Calls the `verifier` subagent before its checkpoint commit, and puts the verifier's
     literal output in its report. Nothing runs the Stop hook's checks when a subagent
     finishes, so the verifier call replaces that check.
   - Ends by ticking the part, updating its ledger rows and making a checkpoint commit
     with the trailers.
   - Stops and reports, without guessing, when the part needs any of these:
     - a new file
     - a tier change
     - a paid call
     - an input the spec doesn't give

   **Resuming.** If the build session ends early, a new session given *"Build plan A00"*
   carries on from the first unticked part.
6a. **The hook probe** checks that the controls apply inside a subagent. A probe subagent
   tries each of these once:
   - a write outside `scope_paths`, which the SCOPE-002 hook must deny
   - a write to `governance/`, which a deny rule must refuse
   - `git push --dry-run`, which the GOV-002 hook must deny
   - `.venv/bin/python -m scripts.local_session --real --help`, which must raise the
     COST-001 permission prompt. The command only prints help, so approving the prompt
     costs nothing.

   The literal results go in plan A00's Proof. Probe 0021 on 2026-11-23 showed that the
   gate, the deny rules and the COST-001 prompt all apply inside subagents (see Design).
6b. **No auto mode.** The design session and the build session must not run in auto mode
   or `bypassPermissions` mode, because auto mode doesn't reliably prompt for ask-rule
   commands (see Design). "How to run this file" says so. The hook probe's fourth check
   fails if the session is in either mode.
7. **The final proposal** holds only what can't be applied before the build:
   - `proposals/A00/governance/rules.yaml` (activations)
   - `proposals/A00/app/AGENTS.md` (the reviewer model exception)
   - `proposals/A00/.github/workflows/evals.yml`
   - any tier change that the build needed, which needs the user's approval in that
     part's session

   The `rules-additions.yaml` file is dropped. CodeGuard-seeded rules for the profile's
   output go in `docs/agent_tech_debt_tracker.md` as one row, for the evidence review to
   consider.

### Simplest working version

8. **"Rules for the run" states these limits:**
   - Build only what spec A00 lists.
   - Build one implementation per verification stage. Don't compare tools or timebox
     evaluations. The ASH evaluation is removed.
   - Use an ADK built-in or an existing repo function before writing new code.
     `GovernancePlugin`, the tool policy and confirmation from Stage 7, `governed_repo`,
     `FakeLlm`, `scripts/evidence_report.py` and `scripts/check_activation.py` are named.
   - Add no options, parameters, configuration keys or abstraction layers that spec A00
     doesn't name.
   - Don't use a deterministic generator or template unless spec A00 lists one.
   - Record anything else that seems needed as a row in `docs/agent_tech_debt_tracker.md`,
     and don't build it. Gaps found in the bootstrap itself go in
     `docs/bootstrapper_tech_debt_tracker.md` instead (requirement 22).
   - The "Code style" section of `AGENTS.md` applies in full. The file points to it rather
     than restating it.
9. **The file list is the size budget.** Spec A00 lists, for each part, the exact files the
   part creates or changes. Plan A00's `scope_paths` is the union of those exact paths,
   plus `proposals/A00/**` and `docs/execution-plans/**`. Directory globs are allowed only
   for the fixture folders. The existing SCOPE-002 hook then denies any other file.
   - A part that needs a file not on its list stops and asks the user.
   - Only the user approves adding a path to `scope_paths`. The approval is recorded in
     the plan's Decisions.
10. **Fixed minimums.** The file states these, and spec A00 fills them in. Categories that
    don't apply to the profile are skipped, and spec A00 says why.
    - **Fixtures** (A02): one good output per output type. One planted failure for each
      gate outcome: a critical finding (`block`), a high finding (`acknowledge`) and an
      intent mismatch (conformance). Planted secrets and vulnerable dependencies count as
      those findings. They aren't extra fixtures.
    - **Eval cases** (A04): at most one per category:
      - happy path
      - out-of-scope request
      - prompt injection
      - non-allowlisted dependency or target (only when the profile has
        `package_ecosystems` or `external_targets`)
      - path escape
      - budget exhaustion

      At most 6 cases × `eval_runs`.
    - **Output specs** (A03): the operational requirements for the output type, and the
      quality requirements spec A00 names. Nothing more.
    - **Tests:** the tests each part's acceptance criteria name, and no others.
11. **Stop conditions.** A part is done when its acceptance criteria pass. Every part has
    criteria a command can check, or `deferred` with the command, as today. Nothing is
    added after they pass.

### The agent tree, for M2 and M3

12. **The roles are fixed. The tree size is chosen in the interview.** The file defines:
    - **Planner.** Exactly one. It talks to the user, and its only tools are
      `propose_intent` and `approve_intent` (SPEC-001).
    - **Executors.** One by default. Several only when spec A00 gives each one a distinct
      tool set. Each takes only `ApprovedIntent` as input, and can't transfer back.
    - **Verify.** The `run_verify` tool, called after the executors. It is not a separate
      agent.
    - **Reviewer.** Exactly one, read-only, on the reviewer model (REV-001).

    The planner, the executors and the reviewer are separate ADK agents, as M3 requires
    ("planning, acting and review split across separate agents"). M3 adds executors or
    tools to this tree without restructuring it.
13. **Every required control is built,** at the strength `rules.yaml` gives it:
    - SPEC-001, SBX-001, SEC-002 (runtime), VER-001, REV-001
    - DEP-001 (runtime, when `package_ecosystems` isn't empty)
    - DATA-001 (sandbox), TOOL-001 (entries)
    - MODEL-001 (eval gate), OBS-001 (`intent.sha`, `work_item` and `verify.gate` on every
      span within a work item)
14. **Observability is used as it is.** OBS-001's new attributes go out through the
    existing telemetry and the in-memory span test from Stage 8. A04 adds one alert to
    `observability/alerts.yaml`: a drop in the first-pass verify rate. A04 adds no new
    dashboards, exporters or collector config.

### The parts

15. The parts keep their IDs, so the `(A0N)` tags in `rules.yaml` and the ledger stay
    correct:

    | Part | Builds | Changes from today |
    | --- | --- | --- |
    | A01 | `add_dependency` (DEP-001), and the extended profile test | The profile, tools and allowlists move to the design session. The profile test reads only the live profile. No proving repo. |
    | A02 | Sandbox image, `verify.sh`, `run_verify`, fixtures | One tool per stage. No ASH evaluation. Fixtures use the minimums. |
    | A03 | The agent tree, the run record, the one-work-item rule, output specs, `ARCHITECTURE.md` | Tree from requirement 12. Output specs use the minimums. No generator unless the spec lists one. |
    | A04 | Eval cases, `eval_pass_rate.py`, `evals.yml` (in the final proposal), intent telemetry, one alert | Cases use the minimums. The capability-rule review is one job step in `evals.yml`. |
    | A05 | Today's A05 and A06 merged: records, the evidence report, the ledger, the activation proposal, closing the plan | No `rules-additions.yaml`. |
16. **Cost and deferral stay as today.** Paid calls need the purpose inputs' approval
    (COST-001). Without it, A03's end-to-end run and A04's gate are `deferred`, with the
    command recorded. "When a part can't finish" is kept.

### Other files

17. `README.md`, "Getting started" steps 2 to 5, describes the design session, the first
    proposal, the build session and its subagents, and the rule against auto mode. It
    replaces the "in one run, from A01 to A06" prompt.
18. `docs/bootstrap-implementation/initial_install.md`, line 12, gives the new start
    prompt.
19. `docs/bootstrapper_tech_debt_tracker.md`, in the row that today is line 17 of
    `docs/tech_debt_tracker.md`, reads "A01 to A05".
20. `docs/execution-plans/handover.md`, line 225, reads "A01 to A05".
21. `docs/bootstrapper_tech_debt_tracker.md` gains one row: auto mode doesn't reliably
    prompt for paid-model commands (COST-001), as found by probe 0021.

### Two tech-debt trackers

The owner added this on 2026-11-23, after intent 0021 was accepted.

22. **The tracker splits in two.**
    - **`docs/bootstrapper_tech_debt_tracker.md`** holds gaps in the bootstrap itself: the
      governance machinery, hooks, CI, the coding-agent process and the bootstrap
      instruction files. It is today's `docs/tech_debt_tracker.md`, renamed with
      `git mv`. Every existing row stays in it, because each one is a gap in the generic
      bootstrap, not in any particular agent.
    - **`docs/agent_tech_debt_tracker.md`** is new. It holds gaps specific to the agent or
      agents that `agent_governance.md` builds: their tools, output types, verification
      stages, evals, run records and anything recorded instead of built (requirement
      8). It starts with a header, a one-line description and an empty table with the
      same columns (`Gap | Rule | Close by`). It starts empty, so a fresh clone carries no
      agent's debt (TMW-15).
    - When it isn't obvious which tracker a row belongs in, the test is this: would the
      gap still exist with a different agent? If yes, it goes in the bootstrapper
      tracker. If no, it goes in the agent tracker.
23. **References point to the right tracker:**
    - `proposals/0021/AGENTS.md`, lines 22 and 121. "Add deferred gaps to" names both
      files and the test in requirement 22. The layout block lists both.
    - `proposals/0021/docs/bootstrap-implementation/project_governance.md`, lines 253 and
      2178, name `docs/bootstrapper_tech_debt_tracker.md`. Line 2192 reads "A01 to A05".
      Only those three lines change.
    - The new `agent_governance.md` names `docs/agent_tech_debt_tracker.md` wherever it
      records deferred or extra work, and the bootstrapper tracker only for gaps found in
      the bootstrap.
    - `docs/records/evidence_review.md`, line 12, lists both files.
    - `docs/execution-plans/handover.md`: its mentions of "the tech-debt tracker" mean the
      bootstrapper tracker, and the text says so.
    - `docs/bootstrap-implementation/codequality.md`, line 988, isn't protected and
      already says "if the project has one", so it doesn't change.
    - Completed plans and earlier intents and specs are history, so they don't change.
24. **`scripts/evidence_report.py`** counts each tracker separately and prints them as
    `Tech-debt entries: bootstrapper <n>, agent <n>.` A missing file counts 0. A test in
    `tests/governance/test_evidence_report.py` checks both counts, using a repo with one
    row in each.

## Design

**The new file's run, end to end:**

```text
Session 1 (design):  interview → intent A00 ⏸ accept → spec A00 ⏸ accept
                     → plan mode → plan A00 ⏸ approve → first proposal → commit
Owner:               apply first proposal (profile, tools, allowlists) → commit
Session 2 (build):   hook probe → subagent A01 → A02 → A03 → A04 → A05
                     (each: build → verifier → checkpoint commit → report;
                      stop-and-ask goes back through the build session to the user)
Owner:               After the run: apply final proposal → PR → merge
```

**Why subagents.** Each part starts with a clean context, which saves tokens. The build
session holds only each part's short report. The user starts two sessions instead of six.

**Probe 0021 (2026-11-23).** It ran in this repo's session, in auto mode, with no active
plan. Inside a `general-purpose` subagent:
- A Write to `app/` was denied by the PreToolUse hook (`SCOPE-001: edits need exactly one
  plan…`).
- Writes to `governance/` and `AGENTS.md` were refused by the deny rules (`File is in a
  directory that is denied by your permission settings`).
- `git push --dry-run` was denied by the hook (`GOV-002: agents never push`).
- `local_session --real --help` ran without a prompt. It ran without a prompt in the main
  session too.

The owner then ran the same command through a subagent in a second session, also in auto
mode. That time **the prompt appeared, and the owner approved it.** So a subagent can
raise the COST-001 prompt. Auto mode, though, prompted in one session and not in the
other, so under auto mode the ask rule is a judgement call, not a deterministic control.
Requirement 6b bans auto mode for the run, and the hook probe checks for the prompt at the
start of every build session (requirement 6a). On 2026-11-16 the owner confirmed in the
activation ledger that the ask rule prompts in a session that isn't in auto mode.

**Why the verifier is called in each part.** The Stop hook (`checks_on_stop.sh`) fires
when the main session's turn ends, not when a subagent finishes. Without the verifier
call, a part could commit with failing checks, and the failure would show up only when
the build session stopped.

**Why the first proposal comes after the spec.** The spec already fixes the tools, tiers
and allowlists, so the user has nothing new to judge later. Applying them early removes
the proving repo, which is the largest piece of incidental machinery in today's file. It
also means no part runs with its tools denied. Each part runs in a new session, so the
hash change costs nothing under GOV-006. The product agent's `GovernancePlugin` halts
only sessions that are already running.

**Why the file list is enforced by scope.** `governance_gate.sh` and
`scripts/check_scope.py` both match `scope_paths` with `fnmatch`, so an exact path matches
only itself. Using exact paths turns the existing SCOPE-002 control into the size budget,
and needs no new code.

**Why the tree has fixed roles.** M3's milestone is "planning, acting and review split
across separate agents", and that split is these roles. Fixing them stops the agent
inventing a structure. Letting only the number of executors vary keeps one agent as the
default, and gives M3 a place to grow.

**Options rejected:**
- Keeping the proving repo, or applying in two batches. See intent 0021, open question 1.
- Merging A02 and A03, or building end to end with stubs first. See open question 2.
- A line-count or token budget. See open question 3.
- Letting spec A00 set the minimums. See open question 4.
- Renaming or renumbering A01 to A04. That needs proposals for `rules.yaml` and the
  ledger for no gain.

## Out of scope

- Running the new file. That's TMW-24.
- Changing `rules.yaml`, the thresholds, the tiers or any control. The `(A0N)` tags stay
  valid as they are.
- Any other change to `project_governance.md` or `AGENTS.md` beyond the lines in
  requirement 23.
- Moving existing tracker rows into the agent tracker. No agent has been built yet, so
  every row today is bootstrap debt.
- The hosting file (`aws_hosting_implementation.md`), M2 observability work and M3
  multi-agent features beyond requirement 12.

## Policies checked

- `governance/rules.yaml`:
  - **GOV-002:** three protected files change, all by proposal under `proposals/0021/`:
    `agent_governance.md`, `AGENTS.md` (two lines) and `project_governance.md` (three
    lines). Nothing else protected changes.
  - **SCOPE-001 and SCOPE-002:** plan 0021's scope covers:
    - `proposals/0021/**`
    - `README.md`
    - `docs/bootstrap-implementation/initial_install.md`
    - `docs/tech_debt_tracker.md` (removed by the rename)
    - `docs/bootstrapper_tech_debt_tracker.md`
    - `docs/agent_tech_debt_tracker.md`
    - `docs/records/evidence_review.md`
    - `scripts/evidence_report.py`
    - `tests/governance/test_evidence_report.py`
    - `docs/execution-plans/**`

    The new file's requirement 9 relies on the same hook.
  - **EVID-001:** the evidence review reads both trackers (requirements 23 and 24).
  - **GOV-006:** the first proposal is applied between the design session and the build
    session. Nothing in the build session commits to `governance/`, so its hash pin holds
    for every subagent.
  - **COST-001:** no paid calls in this change. The new file keeps the paid-model
    approval input and bans auto mode for the run (requirement 6b).
  - **Every control in requirement 13:** still built by the part that `rules.yaml` tags.
- `docs/records/security.md`: no data, secrets or access change. SBX-001 and DATA-001
  isolation are unchanged.
- `app/AGENTS.md`: `app/` doesn't change here. Requirement 7 keeps the narrowing of the
  reviewer model convention for the final proposal.

## Concerns

- **The user applies the first proposal before any code exists.** `tools.yaml` will list
  tools that `app/` doesn't have yet. TOOL-001 only denies calls to unlisted tools, so a
  listed tool that isn't built yet is harmless. If a later part needs a different tier,
  that means a user-approved proposal (A00a) in the middle of the run, which costs one
  session.
- **Exact-path scope is rigid.** A part with a genuine need for a new file stops and asks.
  That is the intended trade, but it means a user may be asked a few times during the run.
- **The 70% target** is a guide, not a check. The proposal's diff is the evidence.
- **Auto mode weakens a COST-001 control.** Probe 0021 showed that auto mode sometimes
  runs commands that match the paid-model ask rules without prompting: one session
  prompted and another didn't. This is wider than this change: any auto-mode session can
  make paid calls unprompted. Requirement 6b
  covers the run. The repo-wide fix, for example `disableAutoMode` in managed settings or
  a PreToolUse hook that denies paid commands unless approved, is protected work. It is
  recorded as a tech-debt row and belongs to the handover's "Auto mode policy" and
  "Managed settings" gaps (TMW-19).
- **A failed prompt probe.** If, in some build session, the hook probe shows that a
  subagent doesn't raise the COST-001 prompt, the build session refuses to run any part
  that needs a paid call. That part's check is recorded as `deferred`, with the command
  for the user to run.
- **The stop-and-ask round trip** adds a hop: subagent, then build session, then user,
  then a new subagent. A part that stops often costs a full context reload each time.
  The file list and the fixed minimums are there to keep stops rare.
