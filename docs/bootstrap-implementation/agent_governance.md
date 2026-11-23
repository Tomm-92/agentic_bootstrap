# Agent governance implementation instructions

These instructions govern the product agent once its purpose is known. They follow
`docs/bootstrap-implementation/project_governance.md`, which built every
purpose-independent control: the runtime governance layer, the tool policy and
observability. The run agrees with the user what the agent or agents should do, then
builds the **simplest version that works** with every required control. That version
serves a first deployment, the observability stack and a later multi-agent tree without
a rebuild. The agent is one ADK tree at `<profile.product_agent.path>`, described by one
profile. Agents can't edit this file (GOV-002).

## Purpose and prerequisites

The user does these before the run, because the coding agent must not:

- [ ] Stages 1 to 11 of `project_governance.md` and its "After the run" are done.
- [ ] The user can say in a sentence each what the agent is for and what it produces.
- [ ] A container runtime is reachable from the user's terminal, and `ANTHROPIC_API_KEY`
      is set there. The Claude Code sandbox blocks the container runtime, so the session
      never runs a Docker check. Don't loosen the sandbox to allow it: the Docker socket
      gives host access. Every check that needs Docker goes to the owner batch.
- [ ] **No session of this run is in `bypassPermissions` or `dontAsk` mode.** Manual and
      auto mode are both fine.
      - `branch_guard.sh` denies every paid-model command unless `permission_mode` is
        `default`, which is manual mode (COST-001).
      - In manual mode, the `ask` rules prompt before each paid command.
      - In auto mode, every paid check is `deferred` to the owner batch.

**The owner batch** is the list of checks the session couldn't run: Docker checks, paid
checks in auto mode, and anything else `deferred`. A05's final report gives it as one
ordered block of commands for the user's terminal. "After the run" step 6 runs it.

## How to run this file

```text
Session 1, design:  interview → intent A00 ⏸ → spec A00 ⏸ → plan A00 ⏸ → first proposal → commit
User:               apply the first proposal (profile, tools, allowlists) → commit
Session 2, build:   hook check → subagent A01 → A02 → A03 → A04 → A05
User:               "After the run": apply the final proposal → owner batch → pull request → merge
```

Both sessions can run in manual or auto mode. A session in auto mode makes no paid call,
and asks the user only when a part stops.

1. **Design session.** At the repo root, say: *"Run the design session in
   docs/bootstrap-implementation/agent_governance.md."* If some purpose inputs are
   written down, add *"The purpose inputs are in <path>."*
2. **Apply the first proposal.** On `governance-agent-purpose`, run the commands below.
   The governance hash changes between sessions, so no session's pin breaks (GOV-006).

   ```bash
   cp -R proposals/A00/. . && rm -rf proposals/A00
   git add -A && git commit -m "Apply proposal A00: profile, tools and allowlists" \
     -m "Governance: $(git rev-parse HEAD:governance)
   Plan: A00"
   ```

3. **Build session.** In a new session, say: *"Build plan A00."* It runs to the end,
   and asks only when a part stops.
4. **After the run.** Do the steps at the end of this file.

**To resume,** start a new session with the same prompt. The design session continues
from the first missing or unaccepted document. The build session continues from the
first unticked part.

## Rules for the run

These sections of `project_governance.md` apply here: "Principles", "Concepts used
throughout", "Runtime hook points", "Project profile", "Rule catalogue", "Thresholds and
allowlists" and "Verified facts". In the catalogue, `(A0N)` names the part that builds a
planned control. The "Code style" section of `AGENTS.md` applies in full.

- **One plan, one branch.** Work only under plan A00, on `governance-agent-purpose`.
  Never push, and never commit on `main`.
- **Protected paths.** Never write to one, directly or through a script. Write the change
  under `proposals/A00/` at the same relative path.
- **Rules.** Propose `active` only as A05 describes. Never lower a tier, remove a control
  or widen an allowlist beyond spec A00.
- **Cost.** Make no paid-model call beyond what intent A00 approves (COST-001).
- **Inputs.** If spec A00 lacks something, ask the user. Don't guess.
- **Verify.** Check every framework API against its installed source.

### Build the simplest working version

- Build only what spec A00 lists, with one tool per verification stage. Don't compare
  tools or run evaluations.
- Reuse before writing anything new:
  - ADK built-ins
  - `GovernancePlugin` (`app/governance.py`)
  - Stage 7's tool policy and callable confirmation
  - the `governed_repo` and `FakeLlm` fixtures (`tests/unittests/conftest.py`)
  - `scripts/evidence_report.py` and `scripts/check_activation.py`
- Add no options, parameters, configuration keys, abstraction layers, generators or
  templates that spec A00 doesn't name. Write only the tests the acceptance criteria name.
- Record anything else in `docs/agent_tech_debt_tracker.md`, and don't build it. A gap in
  the bootstrap itself goes in `docs/bootstrapper_tech_debt_tracker.md`. The test: would
  the gap still exist with a different agent?
- **The file list is the budget.** Spec A00 lists the exact files each part may create or
  change. Plan A00's `scope_paths` is their union, plus `proposals/A00/**` and
  `docs/execution-plans/**`. Globs are allowed only for fixture folders. The SCOPE-002
  hook denies every other path. A part that needs another file stops and asks. Only the
  user approves a new path, and the approval goes in plan A00's Decisions.
- **A part stops when its acceptance criteria pass,** or when they're recorded as
  `deferred` with the exact command. Add nothing after that. A control with no passing
  evidence stays `planned`.

**When a part can't finish:**

- **A check needs something the session can't reach** (a sandbox-blocked container
  runtime, an API key, a paid approval, or manual mode for a paid call). Record it as
  `deferred`, with the exact command, add it to the owner batch, and continue. Don't ask
  to loosen the sandbox.
- **A part is blocked, or fails after a reasonable attempt.** Record it, and mark the
  parts that depend on it `blocked`. Continue with the rest.
- **Finishing seems to need a weaker control, an invented value or an unapproved paid
  call.** Don't do it. Stop the part, record why, and raise it in the final report.

## Design session

The design session builds no code. It creates the branch `governance-agent-purpose`.

### 1. Purpose interview

1. Ask for the purpose and the output together, in plain words. Ask nothing else until
   both are answered.
2. Take the inputs below one at a time, in order, skipping any already answered. For
   each one:
   - say what it controls
   - recommend a value from the purpose and output, using the appendices, and say why
   - offer the main alternatives
3. Show every answer in one summary, for the user to confirm or change.

A recommendation isn't an answer until the user accepts it. An unanswered input becomes
an open question, and the parts that depend on it are `blocked`.

| Input | Goes to | Recommend |
| --- | --- | --- |
| Purpose, in one sentence | `profile.product_agent.purpose` | Required, asked first. |
| Output | `profile.product_agent.output` | Required, asked first. |
| Intent artifact | `profile.product_agent.intent_artifact` | What users approve before anything is built: the output's standard description format, such as an OpenAPI document or a change request. |
| Agent tree | Spec A00 | The smallest tree that meets the purpose (see "The agent tree"). |
| Tools | `profile.product_agent.tools`, `tools.yaml` | The smallest set that produces the output. Anything that writes, executes, sends, deletes or spends is at least `confirm`. |
| Verification stages | `profile.product_agent.verification` | Only the stages in A02's table that apply, each with one tool and a reason. |
| Packages | `package_ecosystems`, `packages.yaml` | The output's registries and a short starting list, or none. |
| External targets | `external_targets`, `services.yaml` | None, unless the purpose acts on another system. |
| Reviewer model | `models.yaml` | The `use: reviewer` model. Its ID must differ from the executor's (REV-001). |
| Paid-model approval | Intent A00 | None. Ask separately about A03's end-to-end run and A04's eval gate, which costs `eval_runs` runs per case. Unapproved checks are `deferred`. An approved check still goes to the owner batch if it needs Docker, or if the session is in auto mode. |

### The agent tree

The roles are fixed. Only the number of executors varies.

- **Planner.** Exactly one. It talks to the user. Its only tools are `propose_intent` and
  `approve_intent` (SPEC-001). It is the prompt-injection boundary.
- **Executors.** One by default. Several only when spec A00 gives each one a distinct tool
  set. Each takes only `ApprovedIntent` as input, and can't transfer back.
- **Verify.** The `run_verify` tool, called after the executors. It is a tool, not an
  agent.
- **Reviewer.** Exactly one. It is read-only and runs on the reviewer model (REV-001).

They are separate ADK agents. Later work adds executors or tools to the tree without
restructuring it.

### 2. Intent A00, spec A00 and plan A00

Write each one from its template in `docs/execution-plans/templates/`. After the intent,
and again after the spec, stop until the user sets both `Status: accepted` and
`Accepted by:`.

1. **`docs/execution-plans/intent/A00-agent-purpose.md`.** The confirmed inputs, the
   paid-model approval and any open questions.
2. **`docs/execution-plans/spec/A00-agent-purpose.md`.** It fixes:
   - the tree, and each agent's tools with their tiers, `paths` and `targets`
   - each verification stage and its one tool
   - the intent artifact's fields, each marked required or optional, with the default
     for each optional one. A02's stages and A03's `propose_intent` both follow this list.
   - the fixtures, eval cases and output specs, at the minimums below, giving the reason
     for each category skipped
   - the exact files for each part, A01 to A05. A part's list also holds every test that
     reads or counts a file the part changes. Find them with `git grep -l <file name>
     tests/`. For example, A05's list names `tests/governance/test_quality_score.py`,
     whose count of quality areas rises by four.

   Its "Policies checked" names every rule ID in this file.
3. **`docs/execution-plans/plan/active/A00-agent-purpose.md`,** made in plan mode. It
   holds:
   - `id: 'A00'`
   - every rule ID in this file
   - `scope_paths`, as set out in "The file list is the budget"
   - a checklist of A01 to A05 with their acceptance criteria

   Each part updates its own `pending` rows in `docs/records/governance_activation.md`.

**The minimums:**

- **Fixtures (A02).** One good output per output type. One planted failure for each gate
  outcome: a critical finding (`block`), a high finding (`acknowledge`) and an intent
  mismatch (conformance). A planted secret or vulnerable dependency is one of these, not
  an extra fixture. The good fixture's intent artifact leaves out every optional field,
  so each stage is shown to apply its default.
- **Eval cases (A04).** At most one per category, which makes at most 6 × `eval_runs`
  runs:
  - the happy path
  - an out-of-scope request, which must be declined
  - prompt injection, which must not reach or steer an executor
  - a non-allowlisted dependency or target, which must ask or deny. This applies only
    with `package_ecosystems` or `external_targets`.
  - a path escape, which must be denied
  - budget exhaustion, which must refuse cleanly
- **Output specs (A03).** The output type's operational requirements, and the quality
  requirements that spec A00 names.

### 3. First proposal and commit

Write these from spec A00, inventing no values:

- **`proposals/A00/governance/profile.yaml`.** Every purpose key, with only the stages
  that apply.
- **`proposals/A00/governance/allowlists/`.**
  - `packages.yaml`, for each ecosystem
  - `services.yaml`, holding `package_registries` and `external_targets`
  - `models.yaml`, if the reviewer model changes
- **`proposals/A00/governance/tools.yaml`.** Stage 7's entries, plus a
  `{tier, rules, paths, targets}` entry for every tool in spec A00. These include:
  - `propose_intent`
  - `approve_intent`, which is always `confirm`
  - `run_verify`
  - `add_dependency`, when `package_ecosystems` isn't empty
  - the tools the framework adds to the tree. `GovernancePlugin` denies any tool without
    an entry, so a missing one stops A03 and costs a proposal and a new session. Check
    the installed ADK for every tool name the tree will expose. In ADK 2.14.0 these are:
    - **One entry per delegated sub-agent, named after it** (`free`). ADK wraps a
      `single_turn` sub-agent as a tool of that name (`agents/llm_agent.py:1365`,
      `tools/agent_tool.py:191`). The delegation writes nothing itself. The sub-agent's
      own tools keep their tiers.
    - **`set_model_response`** (`free`), for an agent with both `output_schema` and
      tools, on a model that doesn't declare `output_schema_and_tools`. `AnthropicLlm`
      doesn't (`flows/llm_flows/prompt/_schema.py:61-90`,
      `models/base_llm.py:97-125`). It writes only the agent's structured reply into
      state.
- **`proposals/A00/.claude/settings.json`.** The live settings, keeping every rule and
  hook, plus one `ask` rule for each paid-model command the run adds (COST-001). For
  A04's eval script, that's `Bash(*eval_pass_rate*)`. `branch_guard.sh` already denies
  `eval_pass_rate` outside manual mode, so keep that name for the script. A paid command
  with any other name also needs a `branch_guard.sh` change, through the same proposal.

Commit the intent, spec, plan and first proposal together, with the trailers
`Governance: <git rev-parse HEAD:governance>` and `Plan: A00`. Then stop, and tell the
user to apply the first proposal.

## Build session

The build session orchestrates. Each part runs in a fresh subagent with a clean
context, and the build session keeps only each part's short report.

1. **Hook check.** Don't attempt a denied action live. The auto-mode classifier rightly
   blocks a deliberate attempt to get past a control, and the tests below cover each
   one.
   - Check that the SessionStart message names the governance hash and plan A00. That
     shows the hooks load in this session.
   - Run `.venv/bin/pytest -q tests/governance/test_hooks.py
     tests/governance/test_settings.py`. These cover:
     - the SCOPE-002 and GOV-002 denials
     - the deny rules for protected paths
     - the COST-001 paid-command deny
     - the hook wiring
   - Record the output in plan A00's Proof. If any test fails, stop.
2. **Parts.** For each unticked part, in order, start one fresh `general-purpose`
   subagent. Its prompt names the part, plan A00 and spec A00, and nothing else. Run one
   part at a time.
3. **After each part:**
   - Check that the part is ticked, that its ledger rows are updated, and that
     `git log -1` is its checkpoint commit with the trailers.
   - Call the `verifier` subagent, and paste its output into plan A00's Proof.
   - On a failure, start a new subagent for the part, and give it the failure.
4. **When a part stops to ask,** ask the user, record the answer in plan A00's Decisions,
   and start a new subagent for that part. Answers come only from the user, never from a
   subagent's report.
5. **Stop** after A05, or on a `failed` part, and give the final report.

**Each part's subagent:**

1. Re-reads `governance/rules.yaml`, plan A00 and spec A00, and names the part and its
   rule IDs.
2. Builds only that part, within its file list.
3. Before committing, runs the verifier's check command and puts its output in the
   report. The Stop hook doesn't fire when a subagent ends, so this replaces it.
   `force` runs the checks even when the hook's fingerprint matches, so no hook state is
   deleted:

   ```bash
   echo '{"force": true}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh
   ```

   Run it as its own command. Commit only after it exits 0 with no output, never chained
   after it with `;`.

4. Ticks the part, updates its ledger rows, and commits with the trailers
   `Governance: <git rev-parse HEAD:governance>` and `Plan: A00`.

It stops and reports, without guessing, when the part needs any of these:
- a file that isn't on its list
- a tier change
- a paid call
- an input that spec A00 doesn't give

## Phase A01: Dependencies and the profile check

**Goal:** a dependency must be allowlisted, exist in its registry and be confirmed by the
user, and the profile must be complete.
**Rules:** TOOL-001 (tool entries), DEP-001 (runtime).

**Build:**
1. **`add_dependency(ecosystem, name, version)`**, only if `package_ecosystems` isn't
   empty.
   - It asks for confirmation when a name isn't allowlisted, using Stage 7's callable
     confirmation condition.
   - It rejects a package that isn't in the ecosystem's registry.
   - It rejects an unpinned version.
2. **`tests/governance/test_rules.py`.** The profile check also requires every purpose key
   to be non-null, and `tools` to be non-empty, in the live profile.
3. **Tests**, with the registry mocked:
   - an allowlisted dependency passes
   - a non-allowlisted one asks
   - a non-existent one is rejected
   - an unpinned version is rejected

**Acceptance criteria:**
- [ ] The extended profile check passes.
- [ ] The dependency tests pass with no network. If there are no ecosystems, the DEP-001
      runtime rows are `deferred`, with that reason.

**Ledger:** DEP-001 runtime (both rows).

## Phase A02: Verification sandbox

**Goal:** generated output is checked, and if it is executable run, only in a disposable
sandbox with no credentials. Delivery is gated by severity, and every result is kept.
**Rules:** SBX-001, SEC-002 (runtime), VER-001 (gate), DEP-001 (SCA), DATA-001 (no
sandbox shell).

**Build:**
1. **`scripts/sandbox/`.** A container image holding only the tool that spec A00 names
   for each stage:

   | Stage | Checks | Example tools |
   | --- | --- | --- |
   | `secrets` | Credentials in the output | gitleaks |
   | `sast` | Insecure code patterns, including AI anti-patterns | semgrep, gosec, bandit |
   | `sca` | Vulnerable or hallucinated dependencies | osv-scanner, pip-audit |
   | `iac` | Insecure infrastructure definitions | checkov, hadolint |
   | `policy` | Organisation rules as code | OPA/conftest |
   | `structure` | Architecture or format rules | import-linter, schema validation |
   | `functional` | Build and tests | the output's own test suite |
   | `conformance` | Output matches the approved intent artifact | contract tests, Schemathesis |
   | `content` | Non-code output: grounding, PII, tone | LLM judge (ND) plus PII and regex scanners |

2. **`scripts/verify.sh <work_item_dir> <intent_artifact>`.** Runs the stages in order,
   and writes merged SARIF (JSON for non-code stages) and `verify_summary.json`
   (`{gate, counts_by_severity, stages}`). The gate follows `severity_gate` in
   `thresholds.yaml`:
   - `block` if any finding is critical
   - otherwise `acknowledge` if any is high
   - otherwise `pass`
3. **Isolation (SBX-001, DATA-001).**
   - Network access goes only to the registries and services in
     `allowlists/services.yaml`. Everything else runs offline.
   - No host environment variables, credentials, SSH agent or home-directory mounts.
   - No TTY, and no `docker exec`.
   - The container is removed after each run.
   - Credentials the agent needs live in the harness, never in the sandbox.
4. **`run_verify` tool.** It runs the sandbox and returns `{status, gate, counts,
   report_path}`. A failed sandbox returns an error status the model can retry, and never
   crashes the session.
5. **Fixtures** under `tests/fixtures/`, at the minimums.
6. **A free unit test for each stage script** that runs on the host, without the
   container. The integration tests need Docker, so they're usually in the owner batch,
   and without these a stage has no test the session can run. Each one runs the stage
   on an intent artifact with only the required fields. Where a stage reads the
   container's paths at import, patch the read.

**Acceptance criteria:**
- [ ] Integration tests (`-m integration`, which need the container runtime) show that:
  - the good fixtures pass
  - each planted failure gives its gate
  - network access outside the allowlist fails
  - no credential variables are visible in the sandbox
- [ ] A unit test with a mocked sandbox covers the `run_verify` error path.
- [ ] Each stage script's unit test passes, including on an artifact with only its
      required fields.

**Ledger:** SBX-001, SEC-002 runtime, DEP-001 SCA, DATA-001 sandbox, VER-001 gate (verify
half).

## Phase A03: Intent-first workflow and independent review

**Goal:** the user approves the intent. The agent acts only on the approved intent,
verifies the output, has it reviewed independently and records what happened.
**Rules:** SPEC-001, VER-001, REV-001, with TOOL-001, FS-001 and SBX-001 in use.

**Build:**
1. **`docs/output-specs/<output type>.md`,** at the minimums, in EARS form (`WHEN
   <condition> THE SYSTEM SHALL <behaviour>`). For executable output, the operational
   requirements are:
   - health checks
   - structured logs
   - tracing
   - timeouts
   - configuration from the environment
   - no secrets in code
2. **The tree from spec A00,** built with `sub_agents` delegation or a `Workflow` graph,
   checked against the installed source. Never use `SequentialAgent` or `LoopAgent`,
   which are deprecated.
   - **`propose_intent`** stores a `<profile.intent_artifact>` in session state.
   - **`approve_intent`** (`confirm`) sets `state.approved_intent`, `state.intent_sha` and
     `state.work_item`. The work item name must be unused under `<profile.output_root>`.
     Setting it opens Stage 7's path check.
   - **Executors** have an input schema that accepts only `ApprovedIntent`: the artifact
     and the work item name, never chat text. Transfer back is disabled.
   - **After `run_verify`:**
     - On `block`, the findings go back to the executor, up to `max_fix_iterations`
       times, and then the agent stops and reports.
     - On `acknowledge`, the user confirms the high findings, and the confirmation is
       recorded. ADK 2.14.0 doesn't show a second `request_confirmation` made inside a
       resumed tool call, so build it like this:
       - `run_verify` returns the high findings and records them as pending.
       - The executor calls `run_verify` again. That call's own `confirm` confirmation
         lists the pending findings. An executor `after_tool_callback` sets that text
         with `tool_context.request_confirmation(hint=...)`.
       - On approval, that call sets `state.acknowledged`. It doesn't run the sandbox
         again, and it doesn't count toward the cap.
       - A rejection leaves `acknowledged` unset, so the reviewer is refused.
     - **Any write to the work item clears the gate** and the acknowledgement. The
       reviewer runs only on a gate from a `run_verify` after the last write, so code
       changed after a `pass` or an acknowledgement is verified again. The run cap
       doesn't reset.
   - **The reviewer** checks the output against the approved intent, its scope and
     security patterns. Only the root agent and the reviewer set `model`, so narrow the
     convention exactly that far:
     - `proposals/A00/<profile.product_agent.path>/AGENTS.md` states the exception.
     - Rename `test_only_the_root_sets_a_model` so it allows exactly the root and the
       reviewer. It still fails for any other sub-agent's model, and for a reviewer that
       isn't listed with `use: reviewer`.
     - `fake_llm` replaces the reviewer's model too.
     - `proposals/A00/.claude/skills/adk-review/SKILL.md` lists the new convention. The
       sandbox blocks `.claude/skills/`.
   - **Verified in ADK 2.14.0.** Check these against the installed version:
     - A resumed executor loses its injected input event. So the `intent_sha` check
       reads the args of the planner's latest call to the executor in
       `callback_context.session.events`.
     - ADK validates a `single_turn` agent's reply against its `output_schema`
       (`workflow/_llm_agent_wrapper.py`). So a callback's refusal from the reviewer
       must itself be a valid `output_schema` object, or the node fails with no reason.
     - With `output_key`, the reviewer's reply is in state in its
       `after_agent_callback`, so the run record is written there.
     - Set `disallow_transfer_to_parent` and `disallow_transfer_to_peers` on every
       sub-agent, so none gets `transfer_to_agent`.
3. **`<profile.output_root>/<work item>/RUN_RECORD.md`.** It holds:
   - the approved intent, `intent_sha` and governance hash
   - assumptions and decisions
   - the verify summary, with a link to its report
   - the reviewer's findings
   - the user's acknowledgements
   - remaining risks
4. **One work item per session.** Once a run record exists, further requests are refused,
   with a pointer to a new session.
5. **`ARCHITECTURE.md`.** Show the tree, and mark the planner–executor trust boundary.
6. **Tests** (fake model):
   - the planner has no acting tools
   - no executor runs before approval
   - an executor's input carries no chat text
   - the reviewer's model differs from the executors'
   - the convention test fails for another sub-agent's model, and for an unlisted
     reviewer
   - the fix loop stops at `max_fix_iterations`
   - `acknowledge` needs confirmation, both approved and rejected
   - a write after a `pass` or an acknowledgement closes the gate
   - the run record has every field
   - a second work item in the session is refused

**Acceptance criteria:**
- [ ] All unit tests pass.
- [ ] One end-to-end integration run per output type passes `verify.sh`, under the
      paid-model approval (COST-001). Keep the run records for A05. It needs Docker, so
      it's usually `deferred` to the owner batch.

**Ledger:** SPEC-001 (both rows), VER-001 (both rows), REV-001.

## Phase A04: Evals, model-change gates and intent telemetry

**Goal:** a prompt, governance, profile or model change can't silently degrade quality,
and every trace carries the intent it served.
**Rules:** MODEL-001 (eval gate), OBS-001 (intent attributes).

**Build:**
1. **Eval cases** under `tests/integration/evals/`, in ADK's eval format, at the minimums.
   A case passes only if `verify.sh` passes on its output. An environment variable that
   overrides `<profile.output_root>` keeps eval output apart from real output. ADK
   doesn't do this.
2. **`scripts/eval_pass_rate.py`.** Runs each case `eval_runs` times, and fails below
   `eval_pass_rate_floor`. Add its ask rule, from the first proposal, to
   `test_paid_model_runs_ask_first` in `tests/governance/test_settings.py`.
3. **`proposals/A00/.github/workflows/evals.yml`.** An advisory workflow:
   - It runs nightly, and on PRs that change the agent's prompts, `governance/**`,
     `docs/output-specs/**` or `allowlists/models.yaml`.
   - One job step lists every `kind: capability` rule when `models.yaml` changes.
   - Don't call the model to test it.
4. **Intent telemetry (OBS-001).** Every span for a model or tool call within a work item
   carries `intent.sha`, `work_item` and `verify.gate`, with finding counts by severity.
   - Use the existing telemetry. Add no exporters, collectors or dashboards.
   - Add the attributes to the invariants in `ARCHITECTURE.md`, and to Stage 8's span
     test.
   - Add one alert to `observability/alerts.yaml`, for a drop in the first-pass verify
     rate.

**Acceptance criteria:**
- [ ] The eval gate reports a pass rate for each case, under the paid-model approval
      (COST-001), or is `deferred` to the owner batch.
- [ ] The workflow passes actionlint, without running its paid calls.
- [ ] The extended span test passes.
- [ ] The eval script's ask rule is in `test_paid_model_runs_ask_first`, and passes.

**Ledger:** MODEL-001 eval gate.

## Phase A05: Operations, verification and the activation proposal

**Goal:** the quality score, readiness review and evidence review cover the agent. The
user gets one statement of what is proven and what isn't.
**Rules:** QUAL-001, EVID-001, DATA-001 (ORR), GOV-002, GOV-003.

**Build:**
1. **`docs/records/quality_score.md`.** Add these areas: intent conformance,
   prompt-injection resistance, sandbox isolation and eval pass rate. A score above 1
   links to evidence (QUAL-001).
2. **`docs/records/security.md`.** Add these to the readiness checklist:
   - the handling of outputs and intent artifacts
   - the sandbox isolation evidence
   - no interactive sandbox access
3. **`docs/records/evidence_review.md`.** Add verification reports, eval trends and run
   records to the inputs. Add the question: how often does the verify gate block, or need
   acknowledgement, on the first pass?
4. **`scripts/evidence_report.py`.** Include verification reports, eval results and run
   records.
5. **`docs/agent_tech_debt_tracker.md`.** Add one row naming the Project CodeGuard (CoSAI)
   risk classes that fit the output, as candidate rules for the evidence review.
6. **Run everything the session can run:** the unit suites and the repo's checks. The
   integration suites go to the owner batch unless the session can run them. Fix this
   run's breakage, and never weaken a control or a test.
7. **Complete the ledger.** Every control this file builds has a result, and evidence that
   exists.
8. **`proposals/A00/governance/rules.yaml`.** A copy of `governance/rules.yaml`. Only this
   file's controls with a `pass` result and owner check `none` are `active`.
9. **Close the plan:**
   - List the open "After the run" steps, the deferred checks and the blocked parts.
   - Check that every gap is in the right tracker.
   - Tick the part, move the plan to `docs/execution-plans/plan/completed/`, and commit.

**Acceptance criteria:**
- [ ] The QUAL-001 test passes with the new areas.
- [ ] The evidence report runs against A03's real run, or is `deferred` if that run was.
- [ ] `scripts/check_activation.py proposals/A00/governance/rules.yaml` passes.
- [ ] The extended profile check passes.
- [ ] The final report lists:
  - every ledger item that isn't `pass`
  - the parts completed, deferred and blocked
  - the controls proposed `active`, and why the others stay `planned`
  - the owner batch, as one block of commands in this order: the sandbox integration
    tests, the end-to-end run, the eval gate, then the evidence report against the
    end-to-end run's record
  - the user's actions, in order

**Ledger:** QUAL-001 with the new areas. DATA-001 ORR stays `deferred` until the user
signs off. The EVID-001 review is already `active` from S09 of `project_governance.md`,
so leave it `active`. `check_activation.py` refuses to move a control back to `planned`.

## After the run

For the user, in this order. The run lists these steps and doesn't attempt them.

1. **Review the branch.** Check `proposals/A00/` and the ledger, and check each tool's
   `tools.yaml` entry against its signature.
2. **Check and apply the final proposal** in one commit:

   ```bash
   .venv/bin/python scripts/check_activation.py proposals/A00/governance/rules.yaml
   cp -R proposals/A00/. . && rm -rf proposals/A00
   ```

3. **Decide the evals workflow's spending.** It makes paid calls nightly and on matching
   PRs, which the run's approval doesn't cover (COST-001). Add the API key as a repo
   secret only if you approve that spending. Without the key, the MODEL-001 eval gate
   stays `planned`, and running the gate by hand when a model changes is the check.
4. **Push, open a pull request and merge.** Confirm that the evals workflow validates.
5. **Start a new session**, and rerun the real-tree tests.
6. **Run the owner batch** from A05's final report, in your terminal, in manual mode.
   Set a control to `active`, in a governance commit, only when its check passes.
7. **Hold the first evidence review that covers an agent run.** Add the run records,
   verification reports and eval results to its inputs. The EVID-001 review is already
   `active`, so no status changes.
8. **Sign off `docs/records/security.md`** before the first release. Then set DATA-001 ORR
   to `active`.

After that, normal working applies: one plan per session, and protected changes go
through `proposals/<plan ID>/`. A plan that amends a part takes the part's ID plus a
letter, for example `A02a`.

## Appendix A: Example profile, REST API builder

One executor. Conformance runs Schemathesis against the approved OpenAPI document.

```yaml
project: api-builder
product_agent:
  path: api_chatbot
  framework: google-adk[mcp]==2.13.0 with LiteLLM
  output_root: generated_apis
  purpose: Designs REST APIs with the user and generates them in Go or Python.
  output: REST API source code (Go/Gin or Python/FastAPI)
  intent_artifact: OpenAPI 3 document
  tools:
    - scaffold_api: writes the project template for the chosen language
    - write_file: writes a source file in the work item
    - add_dependency: adds a pinned dependency
    - run_verify: runs verify.sh in the sandbox
  verification: [secrets, sast, sca, iac, structure, functional, conformance]
  package_ecosystems: [go, pypi]
  external_targets: []
```

## Appendix B: Example profile, infrastructure change agent

This agent has two executors with distinct tool sets: one writes Terraform, and one opens
the pull request (`confirm`). `terraform apply` isn't a tool. The GitHub token lives in
the harness, not the sandbox (SBX-001, DATA-001).

```yaml
project: infra-assistant
product_agent:
  path: infra_agent
  framework: google-adk==2.13.0
  output_root: proposed_changes
  purpose: Proposes Terraform changes for requested infrastructure and prepares them for review.
  output: Terraform module changes plus a plan summary
  intent_artifact: Change request (resources, environment, cost estimate, rollback plan)
  tools:
    - write_file: writes a Terraform file in the work item
    - run_verify: runs fmt, validate, plan and scanners in the sandbox
    - open_pull_request: opens a PR with the change; never applies it
  verification: [secrets, iac, policy, functional, conformance]
  package_ecosystems: [terraform]
  external_targets: [github.com/<org>/<infra repo>]
```
