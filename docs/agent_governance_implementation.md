# Agent governance implementation instructions

These instructions finish governing the product agent once its purpose is
known: what it does, what it produces, what users approve first, and which
tools it needs. An AI coding assistant implements all of them **in one run**,
from A01 to A06. They follow `docs/governance_implementation.md`, which builds
every control that doesn't depend on the agent's purpose, including the
runtime governance layer, the tool policy engine and observability.

The product agent is one Google ADK agent tree, a root agent and its
sub-agents, at `<profile.product_agent.path>`. One profile describes it.

The owner's proposal from `docs/governance_implementation.md` makes this file
read-only for agents.

## Before you start

The owner does these before the run, because the assistant must not:

- [ ] Stages 1 to 11 of `docs/governance_implementation.md` are complete, and
      "After the run" in that file is done.
- [ ] The purpose inputs below are filled in. The owner can say what the agent
      is for.
- [ ] A container runtime is reachable from the session, and `ANTHROPIC_API_KEY`
      is set. Without them, their checks will be `deferred`.

## How to run this file

Start one session at the repo root with:

> *"Implement docs/agent_governance_implementation.md in one run, from A01 to
> A06. The purpose inputs are in <path>."*

### How one run stays governed

The controls from the bootstrap file are armed, and nothing here turns them
off. The gate, deny rules, scope check, sandbox and commit trailers all apply
throughout. The run still needs no help from the owner until it ends:

1. **Protected changes are proposals.** Every change to a protected path goes
   under `proposals/A00/` at the same relative path, in this order of need:
   `governance/profile.yaml`, `governance/tools.yaml`,
   `governance/allowlists/`, `CLAUDE.md`, `.github/workflows/evals.yml`,
   `governance/rules-additions.yaml` and, last, `governance/rules.yaml`.
2. **The governance hash doesn't change.** Nothing here commits to
   `governance/`, so the session's pin stays valid (GOV-006) and one session can
   do all the work.
3. **Proposals are tested in a proving repo.** A disposable copy of the repo
   with `proposals/A00/` applied and committed. Inside it the governance layer
   runs for real, against a clean committed hash, with no override or bypass.
4. **The real tree fails closed until the owner applies.** New tools have no
   tier in the live `tools.yaml`, so the policy denies them. That is expected,
   and it means nothing here takes effect without the owner.
5. **The owner reviews once.** "After the run" applies everything in one commit.

### Rules for the run

"Principles", "Concepts used throughout", "Runtime hook points", "Project
profile", "Rule catalogue", "Thresholds and allowlists" and "Verified facts" in
`docs/governance_implementation.md` apply here and are not repeated. In the rule
catalogue, `(A0N)` names the part of this file that builds a planned control.

- **One plan, one intent.** Work under the single plan from A01, inside its
  `scope_paths`, on one branch. Never push, and never commit on `main`.
- **Protected paths.** Never write to one, directly or through a script. A
  denied write is the control working: use the proposal.
- **Rules.** Propose `active` only as A06 describes. Never lower a tier, remove a
  control or widen an allowlist beyond the purpose inputs.
- **Cost.** No paid-model call beyond what the purpose inputs approve (COST-001).
- **Inputs.** If the profile or purpose inputs lack something a part needs, ask
  the owner when someone can answer, or record it in the ledger as `blocked`.
  Don't guess.
- **Verify before use.** Check every framework API against its installed
  source before relying on it.

**At the start of each part,** re-read `governance/rules.yaml` and the plan, and
name the part and rule IDs you are working under.

**At the end of each part,** tick it in the plan, update its rows in
`docs/governance-activation.md`, and make a checkpoint commit on the branch with
the trailers `Governance: <git rev-parse HEAD:governance>` and `Plan: A00`.

**To resume,** read the plan and continue from the first unticked part.

### When a part can't finish

| Situation | What to do |
| --- | --- |
| A check needs something the session can't reach, such as a container runtime blocked by the sandbox, an Anthropic API key or a paid-model approval | Record it as `deferred`, with the exact command for the owner. Continue. Don't ask to loosen the sandbox as part of the run. |
| A part is `blocked` or fails after a reasonable attempt | Record it. Mark parts that depend on it as `blocked`. Continue with the parts that don't. |
| Finishing seems to need a weaker control, an invented value or a paid call the purpose inputs don't approve | Don't do it. Stop that part, record why, and raise it in the final report. |

A control with no passing evidence stays `planned`.

## Purpose inputs

Answer these in one file, or in the opening message. A01 asks once, in a single
batch, for anything missing. The appendices show two complete examples.

| Input | Goes to | Notes |
| --- | --- | --- |
| Purpose, in one sentence | `profile.product_agent.purpose` | **Required.** |
| Output | `profile.product_agent.output` | |
| Intent artifact | `profile.product_agent.intent_artifact` | What users approve first. |
| Tools, and what each does | `profile.product_agent.tools`, `tools.yaml` | Include tier decisions that differ from the defaults in A01. |
| Verification stages | `profile.product_agent.verification` | Only those that apply to the output type. |
| Package ecosystems and allowed packages | `profile.product_agent.package_ecosystems`, `packages.yaml` | |
| External targets | `profile.product_agent.external_targets`, `services.yaml` | |
| Reviewer model | `models.yaml` | Its ID must differ from the executor's, but it may be the same family (see "Known gaps" in `docs/governance_implementation.md`). |
| Paid-model approval | The plan | Default: none. In Claude-only dev mode, A03's end-to-end runs and A04's eval gate are paid calls, so say whether each is approved. A04 costs `eval_runs` runs per eval case. Without approval, those checks are `deferred`. |

---

## Phase A01: Agent profile and tools

**Goal:** governance records the agent's purpose, output, intent artifact,
tools and verification stages. Every tool has a tier. A dependency added to
an output must be allowlisted, exist in its registry and be confirmed by the
user.

**Rules:** TOOL-001 (tool entries), DEP-001 (runtime).

**Scope paths:** `proposals/A00/**`, `docs/exec-plans/**`,
`docs/governance-activation.md`, `<profile.product_agent.path>/**`, `scripts/**`,
`tests/**`.

### Build

1. **Plan and branch.** Read the purpose inputs, and ask for anything missing in
   one batch. Switch to the branch `governance-agent-purpose`, and write
   `docs/exec-plans/active/A00-agent-purpose.md` with `id: 'A00'`, every rule ID
   this file names, a checklist of A01 to A06 with their acceptance criteria,
   and the union of their scope paths plus the protected paths the proposal will
   change, so the applied commit stays in scope. This file's controls are the
   `pending` rows in `docs/governance-activation.md`; each part updates its own.
2. **`scripts/proving_repo.sh <dir>`.** Clones the repo at `HEAD` into `<dir>`,
   copies the working tree's changes over it, overlays `proposals/A00/`, and
   commits there, so `governance/` is clean and committed. It never writes to the
   real repo's protected paths. A test fixture uses it for every test that needs
   the proposed governance. Once the owner has applied the proposal, the overlay
   is gone and the fixture still works.
3. **`proposals/A00/governance/profile.yaml`.** Fill each purpose key in "Project
   profile" in the bootstrap file from the purpose inputs. Use the appendices
   below as guides. Do not invent values. Keep only the verification stages
   that apply to the output type.
4. **`proposals/A00/governance/allowlists/`.** Fill `packages.yaml` for each
   ecosystem in `package_ecosystems`. In `services.yaml`, fill
   `package_registries` and `external_targets` from the profile. These values
   are proposals for the owner to confirm.
5. **`proposals/A00/governance/tools.yaml`.** Add a `{tier, rules}` entry, plus `paths` and
   `targets` naming the arguments that hold a path or an external target, for
   every tool in the profile's `tools`, and keep the entries from Stage 7. Include
   `propose_intent`, `approve_intent` and `run_verify`, which later parts add.
   - Any tool that writes, executes, sends, deletes or spends is at least
     `confirm` unless the owner decides otherwise.
   - `approve_intent` (phase A03) is always `confirm`.
6. **Dependencies (DEP-001).** If `package_ecosystems` is not empty, add an
   `add_dependency(ecosystem, name, version)` tool that:
   - Asks for confirmation when the name is not allowlisted, using the
     callable confirmation condition from Stage 7.
   - Checks that the package exists in that ecosystem's registry, and rejects
     names that don't.
   - Requires a pinned version.
7. **`tests/governance/test_rules.py`.** Extend the profile check: every
   purpose key is non-null, and `tools` is not empty. It reads
   `proposals/A00/governance/profile.yaml` if that exists, and the live profile
   otherwise, so the suite passes before and after the owner applies it.
8. **Tests.** Mock the registry. An allowlisted dependency passes, a
   non-allowlisted one asks, a non-existent one is rejected, and an unpinned
   version is rejected.

### Acceptance criteria

- [ ] The extended profile check passes against
      `proposals/A00/governance/profile.yaml`.
- [ ] The dependency tests pass with no network.

### Ledger

DEP-001 runtime (both).

---

## Phase A02: Verification sandbox

**Goal:** anything the product agent generates is checked only in a
disposable sandbox with no credentials, and run only there if it is
executable. Delivery is gated by severity, and every result is kept.

**Rules:** SBX-001, SEC-002 (runtime), VER-001 (gate), DEP-001 (SCA),
DATA-001 (no sandbox shell).

**Scope paths:** `scripts/**`, `<profile.product_agent.path>/**`, `tests/**`.

### Build

1. **`scripts/sandbox/`.** A container image holding the tools that the
   stages in `<profile.verification>` need. For any profile that produces
   code, timebox an evaluation of ASH (Automated Security Helper) before
   assembling scanners by hand.
2. **`scripts/verify.sh <work_item_dir> <intent_artifact>`.** Runs the
   profile's verification stages in order. Map each stage to concrete tools
   for the output type:

   | Stage | Purpose | Examples |
   | --- | --- | --- |
   | `secrets` | Credentials in the output | gitleaks |
   | `sast` | Insecure code patterns, including AI anti-patterns (broad exception handling, `eval`, placeholder credentials, deprecated APIs) | semgrep, gosec, bandit |
   | `sca` | Vulnerable or hallucinated dependencies | osv-scanner, govulncheck, pip-audit, npm audit |
   | `iac` | Insecure infrastructure definitions | checkov, trivy config, hadolint |
   | `policy` | Organisation rules expressed as code | OPA/conftest, custom checks |
   | `structure` | Architecture or format rules | import-linter, depguard, schema validation |
   | `functional` | Build and tests | the output's own test suite |
   | `conformance` | Output matches the approved intent artifact | contract tests, Schemathesis, golden-answer comparison, citation checks |
   | `content` | For non-code output: grounding, PII, tone, forbidden content | LLM judge (ND) plus deterministic PII and regex scanners |

   It writes merged SARIF (JSON for non-code stages) and
   `verify_summary.json` (`{gate, counts_by_severity, stages}`). The gate
   follows `severity_gate` in `thresholds.yaml`: `block` if any finding is
   critical, otherwise `acknowledge` if any is high, otherwise `pass`.
3. **Sandbox isolation (SBX-001).**
   - Network access, such as fetching dependencies, is limited to the
     registries and services in `allowlists/services.yaml`. Everything else
     runs with networking off.
   - No host environment variables, credentials, SSH agent or
     home-directory mounts. No TTY and no `docker exec` (DATA-001).
   - The container is removed after each run.
   - Credentials the product agent needs live outside the sandbox, in the
     harness or a vault. Generated content never has access to them.
4. **`run_verify` tool.** Runs the sandbox and returns `{status, gate,
   counts, report_path}`. A dead or failed sandbox returns an error status
   the model can retry. It never crashes the session. Its `tools.yaml` entry comes from A01.
5. **Fixtures** under `tests/fixtures/`: one known-good output for each
   output type in the profile, plus planted failures (a secret, a vulnerable
   dependency, an intent mismatch).

### Acceptance criteria

- [ ] Integration tests (`-m integration`; they need the container runtime), run
      in the proving repo:
  - The good fixtures pass.
  - Each planted failure gives its expected gate.
  - Outbound network access outside the allowlist fails inside the sandbox.
  - No credential environment variables are visible inside the sandbox.
- [ ] A unit test with a mocked sandbox covers the `run_verify` error path.

### Ledger

SBX-001, SEC-002 runtime, DEP-001 CI (SCA), DATA-001 sandbox, VER-001 gate
(verify half).

---

## Phase A03: Intent-first workflow and independent review

**Goal:** the product agent works intent-first:

1. Agree the intent with the user.
2. The user approves it.
3. Act only on the approved intent.
4. Verify.
5. Review independently.
6. Record what happened.

**Rules:** SPEC-001, VER-001 and REV-001, with TOOL-001, FS-001 and SBX-001
in use.

**Scope paths:** `<profile.product_agent.path>/**`, `tests/**`,
`docs/output-specs/**`, `ARCHITECTURE.md`, `.claude/skills/**`,
`proposals/A00/**`.

### Build

1. **`docs/output-specs/`.** One file for each output type in the profile,
   listing the requirements every output must meet in EARS form (`WHEN
   <condition> THE SYSTEM SHALL <behaviour>`). Include:
   - The operational requirements. For executable output, these are health
     checks, structured logs, tracing, timeouts, configuration from the
     environment, and no secrets in code.
   - The quality requirements for the output type.

   Wherever possible, a deterministic generator or template enforces them.
2. **Agent roles.** Use `sub_agents` task delegation or a `Workflow` graph
   (verify in source). Never use the deprecated `SequentialAgent` or
   `LoopAgent`.
   - **Planner.** Talks to the user. Its only tools are `propose_intent`,
     which stores a `<profile.intent_artifact>` in session state, and
     `approve_intent`. It has no tools that write, execute, send or spend
     (SPEC-001). This is the prompt-injection boundary.
   - **`approve_intent`.** `confirm` tier. It sets `state.approved_intent`,
     `state.intent_sha` and `state.work_item`. The work item name must be
     unused under `<profile.output_root>`. Setting `state.work_item` is what
     opens Stage 7's path check for that work item.
   - **Executor.** Delegated, with an input schema that accepts only
     `ApprovedIntent` (the artifact and the work item name, never chat text).
     Transfer back to the planner or its peers is disabled. Its tools are
     `<profile.tools>`, all subject to Stage 7's policy.
   - **Verify.** Calls `run_verify`.
     - On `block`: send the findings back to the executor, up to
       `max_fix_iterations` times, then stop and report.
     - On `acknowledge`: the user must confirm the high findings, and the
       confirmation is recorded.
   - **Reviewer.** Read-only. Runs on a different model, taken from
     `allowlists/models.yaml` with `use: reviewer`. Checks the output against
     the approved intent, its scope and security patterns (REV-001).
     Code quality's convention lets only the root agent set a model, so REV-001
     needs this one exception. Narrow the convention, and no further:
     - **`proposals/A00/CLAUDE.md`.** Only the root agent and the reviewer set
       `model`. Other sub-agents inherit it.
     - **`test_only_the_root_sets_a_model`.** Rename it, and allow exactly the root
       agent and the reviewer. It still fails if any other sub-agent sets a model,
       or if the reviewer's ID isn't listed with `use: reviewer`.
     - **`fake_llm`.** Replace the reviewer's model as well as the root's. Otherwise
       unit tests would call the real, paid model.
     - **`.claude/skills/adk-review/SKILL.md`.** Update its list of conventions that
       tests enforce.
3. **`<profile.output_root>/<work item>/RUN_RECORD.md`.** Records:
   - The approved intent, `intent_sha` and governance hash
   - Assumptions and decisions
   - The verify summary, with a link to the report
   - The reviewer's findings
   - The user's acknowledgements
   - Remaining risks
4. **One work item per session.** After a run record is written, further
   requests in that session are refused, with a pointer to start a new
   session.
5. **`ARCHITECTURE.md`.** Replace the agent tree with the planner, executor,
   verify and reviewer roles, and mark the trust boundary between planner and
   executor.
6. **Tests** (fake model):
   - The planner has no acting tools.
   - The executor cannot run before approval.
   - The executor's input carries no chat text.
   - The reviewer's model differs from the executor's.
   - The convention test fails when another sub-agent sets a model, and when the
     reviewer's ID isn't listed with `use: reviewer`.
   - No unit test reaches a real model through the reviewer.
   - The fix loop stops at `max_fix_iterations`.
   - An `acknowledge` gate requires confirmation.
   - The run record contains all its fields.
   - A second work item in the same session is refused.

### Acceptance criteria

- [ ] All unit tests pass.
- [ ] One end-to-end integration run per output type, in the proving repo,
      produces an output that passes `verify.sh`, under the purpose inputs'
      paid-model approval (COST-001). Keep these run records for A05.

### Ledger

SPEC-001 (both), VER-001 (both), REV-001.

---

## Phase A04: Evals, model-change gates and intent telemetry

**Goal:** prompt, governance, profile or model changes cannot silently
degrade quality, and every trace carries the intent it served.

**Rules:** MODEL-001 (eval gate), OBS-001 (intent attributes).

**Scope paths:** `tests/**`, `proposals/A00/**`, `scripts/**`,
`<profile.product_agent.path>/**`, `ops/observability/**`,
`ARCHITECTURE.md`.

### Build

1. **Eval sets** under `tests/integration/evals/`, in ADK's eval format:
   - The happy path for each output type
   - Out-of-scope requests, which must be declined
   - Prompt injection in user input and in retrieved content, which must not
     reach the executor or change its actions
   - Dependencies or targets that aren't allowlisted, which must ask or deny
   - Path escapes, which must be denied
   - Budget exhaustion, which must refuse cleanly

   Pass criteria include `verify.sh` passing on the output. Keep eval output
   apart from real output, for example with an environment variable that
   overrides `<profile.output_root>`. ADK doesn't do this for you (see
   "Verified facts").
2. **`scripts/eval_pass_rate.py`.** Runs each case `eval_runs` times and
   fails if the pass rate falls below `eval_pass_rate_floor`. Many models
   cannot run at temperature 0, so single runs are not meaningful.
3. **`proposals/A00/.github/workflows/evals.yml`.** Runs the eval gate
   nightly, and when a PR changes the product agent's prompts,
   `governance/**`, `docs/output-specs/**` or `allowlists/models.yaml`. It is
   advisory. The paid-model approval doesn't cover this workflow, so don't call the
   model to test it.
4. **Capability-rule review.** A job summary that lists every
   `kind: capability` rule whenever `allowlists/models.yaml` changes.
5. **Intent telemetry.** Make `intent.sha`, `work_item` and `verify.gate`
   (with finding counts by severity) required on every span for a model or
   tool call within a work item. Add them to the invariants in
   `ARCHITECTURE.md` and to the span test from Stage 8. Add an alert for a
   drop in the eval pass rate or the first-pass verify rate.

### Acceptance criteria

- [ ] The eval gate runs in the proving repo, under the purpose inputs' paid-model
      approval (COST-001), and reports a pass rate for each case.
- [ ] The workflow validates, without running its paid model calls.
- [ ] The extended span test passes.

### Ledger

MODEL-001 eval gate.

---

## Phase A05: Product-agent operations

**Goal:** the quality score, readiness review and evidence review from
Stage 9 cover what the product agent does.

**Rules:** QUAL-001, EVID-001 (review), DATA-001 (ORR).

**Scope paths:** `docs/**`, `tests/governance/**`, `scripts/**`,
`proposals/A00/**`.

### Build

1. **`docs/QUALITY_SCORE.md`.** Add these areas: intent conformance,
   prompt-injection resistance, sandbox isolation and eval pass rate. Each
   score above 1 links to evidence, as QUAL-001 already requires.
2. **`docs/SECURITY.md`.** Add these to the readiness checklist:
   - Handling of the profile's outputs and intent artifacts
   - The sandbox isolation evidence
   - No interactive sandbox access
3. **`docs/REVIEW.md`.** Add verification reports, eval trends and run
   records to the inputs. Add the question: how often does the verify gate
   block or need acknowledgement on the first pass?
4. **`scripts/evidence_report.py`.** Include verification reports, eval
   results and run records.
5. **`proposals/A00/governance/rules-additions.yaml`.** Additional rules seeded from
   Project CodeGuard (CoSAI) for the risk classes relevant to the profile's
   output, such as hard-coded credentials, IaC misconfiguration, supply chain
   and MCP security. Each needs a `because`, and passes the schema test. They stay
   out of the proposed `rules.yaml` until the owner adds them.

### Acceptance criteria

- [ ] The QUAL-001 test passes with the new areas.
- [ ] The evidence report runs against a real product-agent run: A03's run in the
      proving repo, or `deferred` if that run was.

### Ledger

QUAL-001 with the new areas. Keep EVID-001 review and DATA-001 ORR as `deferred`
until the owner holds the review and signs off.

---

## Phase A06: Full verification and activation proposal

**Goal:** everything is checked together, and the owner gets one reviewable
statement of what is proven and what isn't.

**Rules:** GOV-002, GOV-003, EVID-001.

**Scope paths:** `docs/**`, `tests/**`, `proposals/A00/**`.

### Build

1. **Run everything.** The full unit suite in the real tree, then the proving
   repo's unit and integration suites, and the repo's existing checks. Fix what
   is broken in this run's work. Never fix a failure by weakening a control or a
   test.
2. **Complete the ledger.** Every control this file builds has a result and
   evidence that exists.
3. **`proposals/A00/governance/rules.yaml`.** A copy of `governance/rules.yaml`
   in which only this file's controls with a `pass` result and owner check `none`
   are `active`. Everything else stays as it is.
4. **Tech-debt tracker.** Add every deferred item and every gap found.
5. **Close the plan.** List every open owner action from "After the run" that
   applies, each deferred check and each part that was blocked. Tick the parts,
   and move the plan to `docs/exec-plans/completed/`. Commit with the trailers.
6. **Stop.** Give the final report:
   - Parts completed, deferred and blocked.
   - The controls proposed as `active`, and those staying `planned`, and why.
   - The owner actions, in order.

### Acceptance criteria

- [ ] `scripts/check_activation.py proposals/A00/governance/rules.yaml` passes.
- [ ] The extended profile check passes against
      `proposals/A00/governance/profile.yaml`.
- [ ] The final report lists every item the ledger doesn't show as `pass`.

---

## After the run

These are for the owner, in this order. The run lists them and does not attempt
them. Every per-part owner action is here.

1. **Review the branch.** Check everything in `proposals/A00/`, especially
   `profile.yaml`, `tools.yaml`, the allowlists and the ledger. Check each tool's
   `tools.yaml` entry against its signature.
2. **Choose the additional rules.** Add those you accept from
   `proposals/A00/governance/rules-additions.yaml` to
   `proposals/A00/governance/rules.yaml`, give each a ledger row, then delete the
   additions file.
3. **Check the proposal, then apply it in one commit:**

   ```bash
   .venv/bin/python scripts/check_activation.py proposals/A00/governance/rules.yaml
   ```

   ```bash
   cp -R proposals/A00/. . && rm -rf proposals/A00
   ```

4. **Decide the evals workflow's spending.** It makes paid calls every night and on
   matching PRs, which the run's paid-model approval doesn't cover. Add the API key
   as a repo secret only if you approve that (COST-001). Without it, the MODEL-001 eval
   gate control stays `planned`, and running the gate by hand when a model changes is
   the check.
5. **Push, open a pull request and merge.** Confirm the evals workflow validates,
   and runs if you added the key. Running sessions stop at their next prompt once the hash changes
   (GOV-006); that is the gate working.
6. **Start a new session** and rerun the real-tree tests. New tools now have
   tiers, so they run under the policy.
7. **Clear what was deferred.** Run each deferred ledger check. Set a control to
   `active`, in a governance commit, only when its check passes.
8. **Hold the first evidence review,** covering a product-agent run. Then set
   EVID-001 review to `active` in a governance commit.
9. **Sign off the updated `SECURITY.md`** before the first release. Then set DATA-001
   ORR to `active` in a governance commit.

After that, normal working applies: **one plan per session**, and every change
to a protected path goes through `proposals/<plan ID>/`. A plan that amends a
part takes its ID plus a lowercase letter: `A02a`, then `A02b`.

---

## Appendix A: Example profile, REST API builder

The project these instructions were first written for, as it looks after
A01.

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
    - scaffold_api: writes the deterministic project template for the chosen language
    - write_file: writes a source file in the work item
    - add_dependency: adds a pinned dependency
    - run_verify: runs verify.sh in the sandbox
  verification: [secrets, sast, sca, iac, structure, functional, conformance]
  package_ecosystems: [go, pypi]
  external_targets: []
```

The output specs (`docs/output-specs/go.md`, `python.md`) require
`/healthz` and `/readyz`, structured JSON logs, OpenTelemetry, timeouts,
graceful shutdown, configuration from environment variables, and handlers →
services → repositories layering. Conformance uses Schemathesis against the
approved OpenAPI document. Allowlisted packages include `gin`, `fastapi`,
`uvicorn`, `pydantic` and the OpenTelemetry SDKs.

## Appendix B: Example profile, infrastructure change agent

The same governance applied to an agent whose output is not application
code.

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

Here `open_pull_request` is `confirm` tier, and `terraform apply` is not a
tool at all. Policy uses OPA/conftest rules on the plan JSON. Conformance
compares the planned resources with the approved change request. The GitHub
token lives outside the sandbox, and the PR tool runs in the harness (SBX-001,
DATA-001).
