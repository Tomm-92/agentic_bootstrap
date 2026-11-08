# Governance implementation instructions

These instructions build governance, control and observability checks for
any agentic development project, before any product code. An AI coding
assistant implements all of them **in one run**, from Stage 1 to Stage 11.
They cover two kinds of agent:

- **Coding agents** (Claude Code, Copilot, Codex, Gemini) that develop the
  repo.
- **The product agent**: the Google ADK agent tree the project builds, a
  root agent and its sub-agents, at `<profile.product_agent.path>`. One
  profile describes it. Examples include an agent that generates code, drafts
  documents, changes infrastructure, triages tickets or answers questions
  over private data.

This file bootstraps every control that can be built before anyone knows
what the product agent will do: build-time controls for coding agents, CI,
and the runtime governance layer, tool policy and observability that will
wrap the agent. Once the agent's purpose is known,
`docs/agent_governance_implementation.md` adds the controls that depend on
it, also in one run: the agent's tools, the verification sandbox, the
intent-first workflow and evals. Until then, the controls it builds stay
`planned`.

Both files describe the project through `governance/profile.yaml`. Stage 2
fills the keys known at bootstrap, and phase A01 of the second file fills the
rest. The rules and stages refer to the profile, never to a specific product.

Put this file at `docs/governance_implementation.md` in the new repo, and the
second file at `docs/agent_governance_implementation.md`. Run this file after
`docs/initial_install.md` and `docs/codequality.md`. Both instruction files become
read-only for agents when the owner applies this run's proposal.

## How to run this file

Start one session at the repo root with:

> *"Implement docs/governance_implementation.md in one run, from Stage 1 to
> Stage 11. The run inputs are in <path>."*

### How one run stays governed

Every control is **built first and armed last**. The code quality hooks and deny
rules stay on throughout, so everything here is linted, type-checked and tested as
it is written. The governance controls don't restrict the run until they have been
built and tested, and no control is skipped:

1. **Build disarmed.** Hooks, git hooks and deny rules exist as files but are
   not wired in. Tests exercise them directly, against temporary repos.
2. **Respect the locks.** `docs/codequality.md` denies edits to
   `.claude/settings.json`, `.claude/hooks/` and `.github/workflows/`. Everything
   this run adds or changes there goes under `proposals/0001/` at the same relative
   path. Never write to those paths directly or through a script.
3. **Prove.** Each stage records its evidence for each control in a ledger.
4. **Arm and activate.** The owner reviews everything once and applies the proposal
   in one commit. The new deny rules, hooks and sandbox apply from the next session.
   Only the owner moves a control to `active`.

Until the owner merges, nothing the run produced is in effect on `main`.

### Rules for the run

The run is the one session the governance gate doesn't cover, because the gate
isn't live yet. These rules hold from the first tool call, as instructions (ND),
until the owner applies the proposal and the deterministic versions go live. The
owner's review of the whole branch is the human check on them.

- **One plan, one intent.** The whole run works under the single plan from
  Stage 1, inside its `scope_paths` (principle 7).
- **Git.** Work on the branch from Stage 1. Never commit on `main`, never push,
  never use `--no-verify`, and never set `core.hooksPath`.
- **Secrets.** Never read, print or commit `.env` files.
- **Cost.** No paid-model call beyond what the run inputs approve (COST-001).
- **Rules.** Copy the catalogue exactly. Never set a control to `active`, lower
  a tier, remove a control or widen an allowlist beyond the run inputs. Extra
  rules go under `proposals/0001/`.
- **Tests.** Never run a hook test against the real repo's `main`. Keep tests
  inside temporary repos.
- **Read the profile first.** Wherever a stage says `<profile.key>`, use that
  value from `governance/profile.yaml`.
- **Inputs.** If the profile or run inputs lack something a stage needs, ask
  the owner when someone can answer, or record it in the ledger as `blocked`.
  Don't guess.
- **Verify before use.** Check every framework API against its installed
  source, and every Claude Code hook or permission behaviour against
  https://code.claude.com/docs, before relying on it. The "Verified facts"
  section lists what has already been checked.
- **Existing files.** The repo already has code quality's hooks, `CLAUDE.md`,
  settings, CI workflow and config. Keep them and merge into them. If a stage needs
  a change to `ruff.toml`, `mypy.ini` or `pytest.ini`, put it under
  `proposals/0001/` too. Fix findings in the code, not by weakening a check.

**At the start of each stage,** re-read `governance/rules.yaml` (once it exists)
and the plan, and name the stage and rule IDs you are working under. This keeps
the rules in view through a long run (principle 8).

**At the end of each stage,** tick it in the plan, add its rows to the ledger,
and make a checkpoint commit on the branch that ends with these trailers:

```text
Governance: <git rev-parse HEAD:governance>
Plan: 0001
```

Commits made before `governance/` is on `HEAD` have no hash to record, so the
Stage 1 and Stage 2 checkpoints carry only the `Plan:` trailer. Stage 4 builds
this one exception into the check.

**To resume** after an interruption or compaction, read the plan and continue
from the first unticked stage. The plan and ledger hold the run's state, not
the conversation.

### When a stage can't finish

| Situation | What to do |
| --- | --- |
| A check needs something the run doesn't have, such as a container runtime, an Anthropic API key or a GitHub secret | Record it as `deferred`, with the exact command or action the owner needs. Continue. |
| A stage is `blocked` or fails after a reasonable attempt | Record it. Mark stages that depend on it as `blocked`. Continue with the stages that don't. |
| Finishing seems to need a weaker control, an invented value or a paid call the run inputs don't approve | Don't do it. Stop that stage, record why, and raise it in the final report. |

A control with no passing evidence stays `planned`. A run that reports what it
couldn't do has succeeded; one that hides it has not.

### Repos that are already governed

If `.claude/settings.json` already denies edits to `governance/` or these
instruction files, this file's controls are already armed. Code quality's deny
rules alone don't count. One run can't change those controls, so use one session and one
plan for each stage, starting with the first stage whose controls aren't built.
Name plans `docs/exec-plans/active/SNN-<stage name>.md`, with `id: 'SNN'`, and
amendments `S05a`, then `S05b`. Write protected files under `proposals/SNN/` at
the same relative path, test them with `HOOKS_DIR`, and list applying them as
owner actions. The owner applies each proposal before the next stage.

## Before you start

The owner does these before the run, because the assistant must not:

- [ ] `docs/initial_install.md` and `docs/codequality.md` are done, with code
      quality's owner actions complete, so `main` has both and its working tree is
      clean.
- [ ] The assumptions below hold, or are changed here first.
- [ ] Python 3.14, `jq` and `git` are installed. Install a container runtime too,
      and set `ANTHROPIC_API_KEY`, or the checks that need them will be `deferred`.
- [ ] The run inputs below are filled in.

## Run inputs

The Value column holds this project's answers. Stage 1 asks once, in a single
batch, for anything missing. Nothing here depends on the agent's purpose.

| Input | Goes to | Value | Notes |
| --- | --- | --- | --- |
| Project name | `profile.project` | `agentic_tools_v2` | |
| Agent package path | `profile.product_agent.path` | `app` | |
| Framework and pinned version | `profile.product_agent.framework` | `google-adk==2.14.0` | |
| Output folder | `profile.product_agent.output_root` | `output` | |
| Exact model IDs for planner, executor and reviewer | `models.yaml`, `services.yaml` | Planner and executor: `claude-haiku-5-5`. Reviewer: `claude-sonnet-5-5`. All use `AnthropicLlm` with the Anthropic API. | The reviewer's ID must differ, but it may be the same family (see "Known gaps"). |
| Telemetry backend | `ops/observability/`, `services.yaml` | Local stack | The local stack, or the owner's choice. |
| Paid-model approval | The plan | Approved for the Claude API, only for the Stage 6 manual run and integration tests. | Any other paid call needs new owner approval. |

---

## Stage map

Later stages depend only on earlier ones. In the rule catalogue, `(S0N)` names
the stage that builds a planned control, and `(A0N)` the phase in
`docs/agent_governance_implementation.md`.

| Stage | Builds | Earlier phase |
| --- | --- | --- |
| 1 | Run setup, inputs, plan and ledger | Run setup (new) |
| 2 | Governance data: profile, rules, thresholds, allowlists, tools | 1, 5 |
| 3 | Rule schema test and agent instructions | 1 |
| 4 | Build-time enforcement, built disarmed | 1, 2 |
| 5 | CI governance workflows | 3 |
| 6 | Runtime governance layer | 4 |
| 7 | Tool policy | 5 |
| 8 | Observability | 6 |
| 9 | Operate and improve | 7 |
| 10 | Full verification and activation proposal | Owner actions of every phase |
| 11 | Hand over for arming | 1 |

---

## Stage 1: Run setup

**Goal:** the run has its inputs, one branch, one plan and a ledger before any
governance file is written.

**Rules:** SCOPE-001, GOV-002.

### Build

1. **Inputs.** Read the run inputs, and ask for anything missing in one batch.
2. **Branch.** `git switch -c governance-bootstrap` from `main`.
3. **`docs/exec-plans/active/`, `completed/` and `tech-debt-tracker.md`.** Seed
   the tracker from "Known gaps".
4. **`docs/exec-plans/active/0001-bootstrap.md`.** The run's one plan:

   ```yaml
   ---
   id: '0001'
   rules: [<every rule ID in the catalogue>]
   scope_paths:
     - <profile.product_agent.path>/**
     - governance/**
     - docs/**
     - scripts/**
     - tests/**
     - ops/observability/**
     - proposals/0001/**
     - .claude/**
     - .github/**
     - .githooks/**
     - AGENTS.md
     - CLAUDE.md
     - README.md
     - ARCHITECTURE.md
     - .gitignore
     - pytest.ini
     - requirements-dev.txt
   ---
   ```

   Below that, record the goal, the rules, a checklist of Stages 1 to 11 with
   each stage's acceptance criteria, the inputs received, and any paid-model
   approval. Record assumptions, decisions and risks there as you go. Add
   deferred gaps to the tech-debt tracker.
5. **`docs/governance-activation.md`.** The ledger: one row for each control
   that the catalogue marks `planned`, with these columns:

   | Rule | Control | Stage | Evidence | Result | Owner check |
   | --- | --- | --- | --- | --- | --- |

   `Evidence` is a test ID, command or report path. `Result` is `pass`,
   `deferred`, `blocked` or `failed`, or `pending` for controls that
   `docs/agent_governance_implementation.md` builds. `Owner check` is what only a human can
   confirm, or `none`.
6. **Prerequisites.** Check for Python 3.14, `jq`, `git`, a container runtime
   and `ANTHROPIC_API_KEY`. Record what's missing in the plan, without printing
   the key.

### Acceptance criteria

- [ ] The session is on `governance-bootstrap`, and `main` is unchanged.
- [ ] The plan and ledger exist, and every run input is recorded.

---

## Stage 2: Governance data

**Goal:** the rules, the profile's bootstrap keys, limits, allowlists and today's
tool tiers are committed on the branch, so later stages read real values and the
runtime layer has a governance hash to check.

**Rules:** GOV-002, GOV-003, TOOL-001 (tool entries), DEP-001, MODEL-001.

**Scope paths:** `governance/**`, `requirements-dev.txt`, `pytest.ini`,
`.gitignore`.

### Build

1. **`governance/profile.yaml`.** Fill `project`, `path`, `framework` and
   `output_root` from the run inputs, using "Project profile" below as a guide.
   Leave the purpose keys null or empty; phase A01 fills them. Do not invent
   values.
2. **Governance tooling.**
   - `requirements-dev.txt` (or the project's equivalent): add
     `pytest>=9,<10` and `pyyaml>=6,<7`, and `types-PyYAML` if the repo
     type-checks.
   - The existing Python 3.14 `.venv`, with the dev requirements installed.
     Re-lock `requirements-dev.lock` as `docs/codequality.md` describes.
   - Check that `pytest.ini` collects `tests/governance/`. If it needs a change,
     put that under `proposals/0001/`.
3. **`.gitignore`.** Covers `.env`, the virtualenv, caches,
   `.claude/.session_governance/` and `<profile.output_root>/`.
4. **`governance/rules.yaml`.** Copy it exactly from "Rule catalogue" below.
5. **`governance/thresholds.yaml` and `governance/allowlists/`.** Copy them from
   "Thresholds and allowlists". Then fill them from the run inputs:
   - `models.yaml`, and `model_providers` in `services.yaml` from it.
   - `telemetry_exporters` in `services.yaml`, from the telemetry backend.

   Leave `packages.yaml` and the other service lists empty until phase A01.
   The values are proposals the owner confirms at review.
6. **`governance/tools.yaml`.** Maps every product-agent tool name to
   `{tier, rules}`, plus `paths` and `targets` naming the arguments that hold a
   path or an external target. List the tools the agent has today, which may be
   none. Any tool that writes, executes, sends, deletes or spends is at least
   `confirm` unless the owner decides otherwise. Phase A01 adds the real tools.
7. **`governance/README.md`.** Cover:
   - The owner.
   - What each file holds, including the profile.
   - That the rules in effect are those committed at `HEAD`, identified by
     the governance hash.
   - The rule format: the fields of a rule and their allowed values.
   - The change process: an agent drafts under `proposals/`, the owner
     reviews and commits, and relaxing a rule gets the most scrutiny.

### Acceptance criteria

- [ ] `governance/` is committed on the branch, so `git rev-parse
      HEAD:governance` gives a hash for every later trailer and runtime test.
- [ ] Every value traces to the run inputs or to this file.

---

## Stage 3: Schema test and agent instructions

**Goal:** the rule catalogue and profile are checked by a test, and any coding
agent is told how to work here.

**Rules:** GOV-001, GOV-002, GOV-003, GOV-006, SCOPE-001, SEC-001.

**Scope paths:** `tests/**`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `.github/**`.

### Build

1. **`tests/governance/test_rules.py`.** The rule schema test:
   - Rule IDs are unique.
   - Each rule has exactly the fields `id applies_to rule because tier kind
     controls`, with a non-empty `because`.
   - `applies_to` ⊆ {build, runtime}, `tier` ∈ {free, confirm, deny} and
     `kind` ∈ {safety, capability}.
   - Each control has exactly `type at by status`, with `type` ∈ {D, ND, H}
     and `status` ∈ {active, planned}.
   - Every `deny` rule has a D control, and every `confirm` rule an H
     control.
   - `profile.yaml` has every key in "Project profile", and `project`,
     `path`, `framework` and `output_root` are not null. Phase A01 extends
     this to the purpose keys.
   - Parametrise by rule ID.
2. **`AGENTS.md`.** The entry point for any coding agent. It points to rules
   and defines none of its own. It must state:
   - Read `governance/rules.yaml`, `governance/profile.yaml` and the single
     active plan before changing anything, and name the plan and rule IDs
     you are working under.
   - Work only within the active plan. With no active plan, or several, ask.
   - On a conflict with governance or the plan, stop and ask.
   - The protected paths (see Stage 11), and the `proposals/<plan ID>/` route
     for changing them. Never write to a protected path indirectly through a
     script or command.
   - Never push, and never commit on `main`.
   - Keep each session to one plan. Start a new session for the next plan,
     or when the governance hash changes.
   - Record assumptions, decisions and risks in the plan. Add deferred gaps
     to the tech-debt tracker.
   - The commit trailers.
3. **`CLAUDE.md`.** Starts with `@AGENTS.md`. If the file exists, add that
   line at the top and keep the rest. Governance rules are cited by ID, never
   restated.
4. **`.github/CODEOWNERS`.** Assigns `@Tomm-92` to `governance/`,
   `docs/governance_implementation.md`,
   `docs/agent_governance_implementation.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/`,
   `.github/`, `.githooks/` and every dependency manifest. Comment that it is
   dormant until branch protection exists.
5. **`README.md`.** A Governance section that explains the gate, the protected
   paths, the proposals route and the execution-plan workflow. Each session
   after the run writes a plan at `docs/exec-plans/active/<plan ID>-<name>.md`
   with the front matter from Stage 4, records its work there, lists its owner
   actions at the end, and moves it to `docs/exec-plans/completed/`. The edit
   gate allows plan files, so this is always possible. **Open sessions at the
   repo root:** Claude Code loads `.claude/settings.json` only from the folder
   it was launched in, so a session opened from a parent folder runs none of the
   hooks or deny rules. "Owner actions" are for the human: a session lists them
   and does not attempt them. Also document the setup step
   `git config core.hooksPath .githooks`.

### Acceptance criteria

- [ ] The rule catalogue and profile pass `test_rules.py`.

---

## Stage 4: Build-time enforcement, built disarmed

**Goal:** the machinery exists and is proven so that, once armed:
- The repo can't be worked on by an agent without committed governance.
- No agent can change the rules, its own hooks or settings, push, or commit
  on `main`.
- Every commit is tied to the rules and plan it was made under, edits stay
  inside the plan's declared paths, and indirect writes to protected paths are
  blocked.

**Rules:** GOV-001, GOV-002 (including the sandbox control), GOV-004, GOV-006,
SCOPE-001, SCOPE-002, EVID-001 (commit evidence).

**Scope paths:** `.githooks/**`, `tests/governance/**`, `proposals/0001/**`.

**Do not wire anything in during this stage.** Don't change `.claude/settings.json`
or `.claude/hooks/`, and don't set `core.hooksPath`. New hooks and the merged
settings go under `proposals/0001/`, where they change nothing until the owner
applies them.

### Build

1. **`proposals/0001/.claude/hooks/governance_gate.sh` and
   `proposals/0001/.claude/hooks/branch_guard.sh`.** Copy both exactly from
   "Reference scripts", then extend them as below. `chmod +x` the scripts.
   - **Gate, SessionStart:** injects the governance hash and the active
     plan. A SessionStart hook cannot block, so it only informs. It also
     pins the session to that hash in `.claude/.session_governance/`. A
     new or cleared session takes the current hash; a resumed or compacted
     one keeps its pin.
   - **Gate, UserPromptSubmit:** blocks every prompt while `governance/` is
     missing, uncommitted or dirty, and once the hash differs from the
     session's pin (GOV-006). Otherwise it restates the hash and the active
     plan with every prompt, so the rules in effect never sit only at the
     start of a long context.
   - **Gate, PreToolUse:** denies edits unless exactly one plan is active.
     Files under `docs/exec-plans/` are exempt.
   - **Branch guard:** denies `git commit` on `main`.
2. **Plan front matter.** Execution plans start with YAML front matter, as in
   Stage 1: `id`, `rules` and `scope_paths`.
3. **`governance_gate.sh` PreToolUse extension (SCOPE-002).**
   - With one active plan, deny any edit whose repo-relative path matches
     none of the plan's `scope_paths` globs. `docs/exec-plans/**` stays
     exempt.
   - Parse the front matter with `.venv/bin/python -I` and `yaml`, and match
     with `fnmatch`.
   - Deny if the front matter is missing or invalid, and give the reason.
4. **SessionStart additions.**
   - Print the Claude session ID (`session_id` from the hook input), for
     traceability.
   - Print a warning when `git config core.hooksPath` is not `.githooks`.
5. **`.githooks/commit-msg` (GOV-004).**
   - Reject a commit unless the message has a `Governance:` trailer equal to
     `git rev-parse HEAD:governance` and a `Plan:` trailer naming an existing
     plan file in `docs/exec-plans/active/` or `completed/`.
   - Allow the repo's root commit. Also accept, without a `Governance:` trailer,
     a commit whose parent has no `governance/`, because no hash exists yet. It
     still needs its `Plan:` trailer.
   - Use `git interpret-trailers --parse`.
6. **`.githooks/pre-push`.** Re-check the trailers on every commit being
   pushed, using a shared script `.githooks/check_trailers.sh <range>`.
7. **`branch_guard.sh` additions.** Deny:
   - `git commit` with `--no-verify` or `-n`
   - `git config` changes to `core.hooksPath`
   - `git -c core.hooksPath=...`
8. **Claude Code sandbox (GOV-002).** Read
   https://code.claude.com/docs/en/sandboxing. Draft the
   `.claude/settings.json` sandbox configuration that denies filesystem
   writes to every protected path for all processes, including
   `python -c "open('governance/x','w')"`. Write down any part the sandbox
   cannot cover in the tech-debt tracker.
9. **`proposals/0001/.claude/settings.json`.** The existing settings merged with
   everything in "What the settings hold" below, so they can be tested now and
   applied unchanged later. Keep every existing hook and deny rule.
10. **`tests/governance/test_hooks.py`.** Runs the hook scripts as
    subprocesses against a temporary git repo (`git init -b main`, with a
    committed `governance/rules.yaml`), with `CLAUDE_PROJECT_DIR` pointing at
    it. Read the hook folder from a `HOOKS_DIR` environment variable. Its default
    is `proposals/0001/.claude/hooks` if that folder exists, and otherwise
    `.claude/hooks`, so the suite passes during the run and after the owner
    applies the proposal, and code quality's Stop hook stays green. Cases:
    - SessionStart reports the hash and the plan.
    - A prompt is allowed when governance is clean, and its output contains
      the hash and the plan.
    - A prompt is blocked after a governance commit changes the hash, and
      allowed again after a SessionStart with `source: clear` or in a new
      session. SessionStart with `source: resume` or `compact` keeps the old
      pin.
    - A prompt is blocked, and SessionStart exits 2, when governance is
      dirty or missing.
    - Edits with 0, 1 or 2 plans give deny, allow, deny.
    - Plan files are editable with no plan.
    - The branch guard denies `git commit` and `git -C . commit` on `main`,
      and allows `git status`, and commits on another branch.
    - Scope paths: inside allowed, outside denied, missing front matter denied.
      Include this run's own plan, `0001-bootstrap.md`.
    - Each new branch-guard case.
    - `commit-msg`: missing, wrong or valid trailers; root commit; the commit
      that first adds `governance/`.
11. **`tests/governance/test_settings.py`.** Reads the settings from a
    `SETTINGS_PATH` environment variable. Its default is
    `proposals/0001/.claude/settings.json` if that file exists, and otherwise
    `.claude/settings.json`. It checks that every protected path has a deny rule
    and a sandbox `denyWrite` entry, that every hook refers to a script that exists
    in the proposal or in `.claude/hooks/`, and that code quality's hooks and deny
    rules are still there.

### Acceptance criteria

- [ ] `pytest tests/governance` passes, and the repo's existing checks
      still pass.
- [ ] All `test_hooks.py` cases pass.
- [ ] `test_settings.py` passes against the proposed settings.
- [ ] A test proves an indirect write to `governance/` is blocked under the
      proposed sandbox settings, or a tech-debt entry explains why it can't
      be.
- [ ] `git diff main -- .claude/settings.json .claude/hooks .github/workflows`
      prints nothing.

### Ledger

GOV-002 sandbox, GOV-004 commit-msg, SCOPE-002 PreToolUse, EVID-001 trailers.

---

## Stage 5: CI governance workflows (advisory)

**Goal:** every pull request gets governance, secrets and dependency
signals, each reported as its own job, and an independent AI pre-review.
Correctness checks (lint, types, tests) belong in their own workflow,
outside this file.

**Rules:** GOV-004 (CI), SEC-002 (CI), DEP-001 (CI), REV-001 (applied to
PRs).

**Scope paths:** `proposals/0001/**`, `.github/**`, `scripts/**`, `README.md`.

### Build

`proposals/0001/.github/workflows/governance.yml`, triggered on `pull_request` and
on push to `main`, with separate jobs:

1. **`governance`:**
   - The rule and profile schema tests.
   - `.githooks/check_trailers.sh` over the PR's commits.
   - A job summary listing every changed protected path, so the reviewer
     sees governance changes explicitly.
   - A diff of every dependency manifest and of `governance/allowlists/`,
     listed as DEP-001 items for review.
2. **`secrets`:** gitleaks over the PR diff, with SARIF output.
3. **`dependencies`:** a vulnerability audit for each package ecosystem the
   repo itself uses (for example `pip-audit`, `npm audit`, `govulncheck`),
   plus `osv-scanner`. SARIF or JSON output.

`proposals/0001/.github/workflows/ai-review.yml`: an LLM pre-review of each PR, on a different
model ID from the one that wrote the code. It may be the same family (see "Known
gaps"). It checks plan compliance, files changed outside the plan's `scope_paths`,
and security patterns that SAST misses. It posts findings only; the human decides
the merge. The paid-model approval doesn't cover this workflow, so don't call the
model to test it.

Upload all reports as artifacts and keep them for `retention_days`. Every
job is advisory: on GitHub Free with a private repo, required status checks
are unavailable.

### Acceptance criteria

- [ ] Both workflows pass `actionlint`, or are otherwise validated locally.
- [ ] Each job's command runs successfully locally, apart from `ai-review.yml`'s
      paid model call.

### Ledger

GOV-004 CI, SEC-002 CI, DEP-001 CI. Record each as `deferred` with this owner
check: the jobs run on the test PR in "After the run".

---

## Stage 6: Runtime governance layer

**Goal:** the product agent cannot run without committed governance. Every
session event carries the governance hash, the rules are re-injected on every
model call, and sessions stop at their token budget. None of this depends on
what the agent does.

**Rules:** GOV-005, COST-001 (runtime), MODEL-001 (allowlist test), EVID-001
(session log).

**Scope paths:** `<profile.product_agent.path>/**`, `tests/**`,
`ARCHITECTURE.md`.

### Build

1. **Product agent.** If `<profile.product_agent.path>` has no agent yet,
   create a root agent there with no tools. Keep any agent that already
   exists. Either way, its model is an `AnthropicLlm` with an exact ID from
   `governance/allowlists/models.yaml`, held in one shared variable. The
   approval covers only the Claude API, so don't run the integration tests until
   this replaces the placeholder's `gemini-3.5-flash`.
2. **Governance layer.** One component, attached globally at the hook points
   in "Runtime hook points": `GovernancePlugin(BasePlugin)`, attached with
   `App(plugins=[...])`.
   - **At startup:** read the hash with `git rev-parse HEAD:governance`.
     Refuse to start if it is missing or `governance/` is dirty (fail
     closed). Load `rules.yaml`, `thresholds.yaml` and `profile.yaml`.

     A deployment without git must bake the hash in at build time. Record
     how in the plan.
   - **Before a run:** re-read the hash. If it differs, halt with a refusal.
     Put the hash in session state.
   - **On each event:** stamp the governance hash on the event.
   - **Before a model call:**
     - If the session's token count is at or over `session_token_budget`,
       return a refusal.
     - Otherwise, append the runtime rules (those whose `applies_to`
       contains `runtime`, with their `id`, `rule` and `because`) to the
       system instruction.
   - **After a model call:** add the call's token usage to the session
     counter. Treat missing usage as an error, never as zero.
3. **Session store.** A durable session log is the evidence record (EVID-001).
   Turn off any compaction or summarisation that would rewrite stored
   events. `DatabaseSessionService` needs ADK's `db` extra. Add it to
   `requirements.txt`, with a version range, and re-lock.
4. **`ARCHITECTURE.md`.** Describe:
   - The agent tree as it stands (phase A03 of
     `docs/agent_governance_implementation.md` replaces it)
   - The trust boundaries: user input, retrieved content, model output,
     produced output
   - Where each runtime rule is enforced
   - The "Telemetry invariants" heading that Stage 8 fills in
5. **Tests.** Use a fake model with scripted responses and no real calls. Point
   the fail-closed cases at a temporary repo, because the real `governance/` is
   committed by now:
   - Startup fails when governance is missing or dirty.
   - The run halts on a hash change.
   - Every event carries the hash.
   - The runtime rules appear in the model request.
   - The session is refused once it is over budget.
   - A missing token count is an error.
   - Every configured model ID is in `allowlists/models.yaml` (MODEL-001).
   - The agent loads the way ADK's runner loads it.

### Acceptance criteria

- [ ] All tests pass with no real model calls.
- [ ] One manual run against `claude-haiku-5-5` works, under the run inputs'
      paid-model approval (COST-001).

### Ledger

GOV-005, COST-001 runtime, MODEL-001 allowlist test, EVID-001 session log.

---

## Stage 7: Tool policy enforcement

**Goal:** no tool runs unless governance gives it a tier, writes stay inside
the work item's folder, and external targets must be allowlisted. The policy
exists before the agent's real tools do, so every tool
added later is governed from its first call.

**Rules:** TOOL-001, FS-001.

**Scope paths:** `<profile.product_agent.path>/**`, `tests/**`.

### Build

1. **Before-tool policy**, in the governance layer:
   - **TOOL-001:** a tool missing from `tools.yaml`, or a `deny`-tier tool,
     returns an error result. Never raise.
   - **FS-001:** every path argument must resolve, after following
     symlinks, inside `<profile.output_root>/<state.work_item>/`. Otherwise
     deny. Until an intent is approved (phase A03), `state.work_item` is
     unset, so every path is denied.
   - **External actions:** every target outside the filesystem (URL, API,
     recipient, cloud resource) must be in `allowlists/services.yaml`.
     Otherwise deny.
   - **Logging:** append every decision (`tool`, `tier`, `result` ∈
     {allowed, denied, confirmed, rejected}, `rule`) to the session's
     governance log.
2. **Confirmation.** `confirm`-tier tools use ADK's human-confirmation
   mechanism (`require_confirmation`), set from their tier in `tools.yaml`.
   Also support a callable condition, for tools whose need for confirmation
   depends on their arguments. Phase A01's `add_dependency` uses it.
3. **Tests.** Define fake tools in the tests and call them through the fake
   model:
   - An unknown tool is denied, and so is a `deny`-tier tool.
   - A path escape (`../`, absolute, symlink) is denied, and so is any path
     when no work item is set.
   - A path inside the work item is allowed.
   - A non-allowlisted external target is denied.
   - A `confirm` tool waits for confirmation, and a callable condition is
     honoured.
   - Decisions are logged.

### Acceptance criteria

- [ ] All tests pass, with no network in unit tests.

### Ledger

TOOL-001, FS-001.

---

## Stage 8: Observability

**Goal:** every model and tool call can be traced to a session, user, rule
set and decision, and any failure can be attributed without shell access.

**Rules:** OBS-001, DATA-001 (exporters).

**Scope paths:** `<profile.product_agent.path>/**`, `tests/**`,
`ops/observability/**`, `ARCHITECTURE.md`.

### Build

1. **Telemetry invariants**, added to `ARCHITECTURE.md`. Every span for a
   model or tool call carries:
   - `session.id`, `user.id`, `governance.sha`
   - `model.id`, input and output tokens, latency
   - `tool.name`, `tool.tier`, `guardrail.result`
   - `failure.source` ∈ {model, harness, tool, sandbox, policy} on errors

   Phase A04 adds `intent.sha`, `work_item` and `verify.gate` once the
   intent-first workflow exists.
2. **Instrumentation.** Use OpenTelemetry. Use ADK's own spans
   (`google/adk/telemetry/`) where they exist. Exporting over OTLP needs ADK's
   `otel` extra. The governance layer adds
   whatever attributes are missing. Add counters for blocked tool calls,
   confirmations (asked, approved and rejected) and budget refusals.
3. **Test.** Run a fake-model session through an in-memory span exporter and
   assert that every invariant attribute is present (OBS-001).
4. **`ops/observability/`.**
   - An OpenTelemetry Collector config, with exporters limited to the
     destinations in `allowlists/services.yaml`, and a test that checks this
     (DATA-001).
   - A local stack (for example Tempo, Prometheus, Loki and Grafana via
     docker-compose), or the owner's chosen backend.
   - A dashboard.
   - Alert rules for:
     - A rise in blocked tool calls
     - An approval rate near 100% (consent fatigue)
     - Token or cost spikes per session

### Acceptance criteria

- [ ] The span test passes.
- [ ] One local session, using the fake model because the paid-model approval
      doesn't cover this stage, shows up as a complete trace in the chosen backend.

### Ledger

OBS-001, DATA-001 exporters.

---

## Stage 9: Operate and improve

**Goal:** governance gets better from evidence, on a fixed cadence, and
quality claims need proof.

**Rules:** QUAL-001, EVID-001 (review), DATA-001 (ORR).

**Scope paths:** `docs/**`, `tests/governance/**`, `scripts/**`.

### Build

1. **`docs/QUALITY_SCORE.md`.** Scores from 1 to 5 for each area:
   - Governance enforcement
   - Scope control
   - Supply chain
   - Evidence
   - Runtime governance (fail closed, rule re-injection, token budget)
   - Tool policy
   - Observability
   - Cost per session

   Phase A05 adds the areas that depend on the agent's purpose. Each score
   above 1 must link to evidence (a test, eval, report or file). Add a test
   that fails if a score above 1 has no link, or links to a path that does
   not exist (QUAL-001).
2. **`docs/SECURITY.md`.** The operational readiness review (ORR)
   checklist:
   - Data handling and the `retention_days` value
   - Redaction of secrets and personal data in sessions and traces
   - Approved services
   - Behaviour during a model-provider outage
   - Rate limits and cost caps
   - Incident response

   Phase A05 adds the sandbox and output items. The owner signs the
   checklist off before each release.
3. **`docs/REVIEW.md`.** The evidence review each sprint:
   - Inputs: coding-agent transcripts, commit trailers, product-agent
     session logs and governance logs, traces, alerts and the tech-debt
     tracker. Phase A05 adds verification reports, eval trends and run
     records.
   - Questions:
     - Which rules were escalated most?
     - Which were never triggered?
     - Which behaviours did no rule cover?
     - Is the approval rate near 100%?
   - Output: rule-change proposals under `proposals/`, applied only through
     owner PRs.
4. **`scripts/evidence_report.py`.** Summarises the available evidence for
   the review.

### Acceptance criteria

- [ ] The QUAL-001 test passes.
- [ ] The evidence report runs against real evidence: this run's commits and
      plan, and Stage 6's local session.

### Ledger

QUAL-001 as tested. EVID-001 review and DATA-001 ORR as `deferred`, with these
owner checks: hold the first review, and sign off `SECURITY.md`.

---

## Stage 10: Full verification and activation proposal

**Goal:** the whole system is checked together, and the owner gets one reviewable
statement of what is proven and what isn't.

**Rules:** GOV-002, GOV-003, EVID-001.

**Scope paths:** `docs/**`, `scripts/**`, `tests/governance/**`,
`proposals/0001/**`.

### Build

1. **Run everything.** `pytest tests/governance`, then the full suite, and the
   repo's existing checks. Fix what is broken
   in this run's work. Never fix a failure by weakening a control or a test.
2. **Complete the ledger.** Every `planned` control in the catalogue has a row,
   with evidence that exists.
3. **`scripts/check_activation.py <proposed rules.yaml>`.** Compares the proposal
   with `governance/rules.yaml`, and fails unless:
   - The only differences are `status: planned` becoming `status: active`, and
     whole new rules that the owner added, each with a ledger row.
   - Every such control has a ledger row with result `pass`, and owner check
     `none` or confirmed by the owner.
   - Every `planned` control in the catalogue has a ledger row.

   Test it: a tier change, a removed control and an unproven activation must
   each fail. `docs/agent_governance_implementation.md` reuses this script.
4. **`proposals/0001/governance/rules.yaml`.** A copy of `governance/rules.yaml`
   in which only controls with a `pass` result and owner check `none` are
   `active`. Everything else stays `planned`. This is a proposal: the run does
   not change the status of any control in `governance/rules.yaml`.
5. **Tech-debt tracker.** Add every deferred item and every gap found.
6. **Close the plan.** List every open owner action from "After the run" that
   applies, each deferred check and each stage that was blocked. Tick Stages 1 to
   11 as Stage 11 finishes, and move the plan to `docs/exec-plans/completed/`.

### Acceptance criteria

- [ ] `scripts/check_activation.py` passes against the proposal.
- [ ] `test_settings.py` still passes against the proposed settings.
- [ ] Everything, including `proposals/0001/`, is committed on the branch.

---

## Stage 11: Hand over for arming

**Goal:** the owner has one tested proposal that applies the controls to every later
session. The run doesn't arm them itself, because code quality's locks rightly stop
it from changing its own hooks and settings.

**Rules:** GOV-001, GOV-002, GOV-006, SCOPE-001, SCOPE-002, SEC-001.

**Scope paths:** `docs/exec-plans/**`.

### What the settings hold

`proposals/0001/.claude/settings.json` holds code quality's existing hooks and deny
rules, plus:

- `permissions.deny`:
  `Edit(/governance/**)`, `Edit(/docs/governance_implementation.md)`,
  `Edit(/docs/agent_governance_implementation.md)`,
  `Edit(/.claude/settings.json)`, `Edit(/.claude/settings.local.json)`,
  `Edit(/.claude/hooks/**)`, `Edit(/.github/**)`, `Edit(/.githooks/**)`,
  `Edit(/AGENTS.md)`, `Edit(/CLAUDE.md)`,
  `Read(**/.env)`, `Bash(git push:*)`. The local file needs its own rule
  because it overrides `settings.json` and can set
  `"disableAllHooks": true`.
- Hooks: SessionStart and UserPromptSubmit → `governance_gate.sh`.
  PreToolUse `Edit|Write|NotebookEdit` → `governance_gate.sh`.
  PreToolUse `Bash` → `branch_guard.sh`.
- Reference hooks as `"$CLAUDE_PROJECT_DIR"/.claude/hooks/<name>.sh`.
- The sandbox configuration from Stage 4.

### Build

1. **Check the hand-over.** Run the `test_settings.py` and `test_hooks.py` suites
   once more against the proposal, and confirm the working tree is clean.
2. **Stop.** Don't copy the proposal into place, and don't attempt anything more.
   Give the final report:
   - Stages completed, deferred and blocked.
   - The controls proposed as `active`, and those staying `planned`, and why.
   - The owner actions, in order.

**Protected paths** (the deny list above): `governance/` (including the
profile), this file, `docs/agent_governance_implementation.md`,
`.claude/settings.json`, `.claude/settings.local.json`,
`.claude/hooks/`, `.github/`, `.githooks/`, `AGENTS.md`, `CLAUDE.md`.

### Acceptance criteria

- [ ] `test_settings.py` and `test_hooks.py` pass against the proposal.
- [ ] The final report lists every item the ledger doesn't show as `pass`.

---

## After the run

These are for the owner, in this order. The run lists them and does not attempt
them. Every earlier per-phase owner action is here.

1. **Review the branch.** Check everything, especially `profile.yaml`,
   `rules.yaml`, `thresholds.yaml`, `tools.yaml`, the allowlists and the ledger.
   Check that each tool's `tools.yaml` entry matches its signature.
2. **Check and apply the proposal, on the branch.** This arms the controls and
   applies the proposed statuses:

   ```bash
   .venv/bin/python scripts/check_activation.py proposals/0001/governance/rules.yaml
   ```

   ```bash
   cp -R proposals/0001/. . && rm -rf proposals/0001
   ```

   Run the tests, whose defaults now read the applied files, and commit with the
   trailers.
3. **Add the reviewer model's API key** as a repo secret. This starts paid calls
   on every PR, which the run's paid-model approval doesn't cover, so decide it
   separately (COST-001).
4. **Push the branch and open a pull request** as the test PR. Confirm the jobs
   run, then set the GOV-004 CI, SEC-002 CI and DEP-001 CI controls to `active`
   in that PR.
5. **Merge to `main`.** Until governance is committed and clean, every prompt is
   blocked; that is the gate working.
6. **Turn on the git hooks:**

   ```bash
   git config core.hooksPath .githooks
   ```

7. **Start a new session at the repo root and confirm:**
   - The session start shows the governance hash.
   - Editing `governance/README.md` is refused.
   - `git push` is refused.
   - `git commit` on `main` is refused.
   - Editing any other file, with no active plan, is refused.
   - After you commit a change to `governance/` from outside the session,
     the session's next prompt is refused.
   - An edit outside the active plan's `scope_paths` is refused.
   - An indirect write to `governance/` from a Bash script is refused.
8. **Clear what was deferred.** Run each deferred ledger check. Set a control to
   `active`, in a governance commit, only when its check passes.
9. **Hold the first evidence review.** Then set EVID-001 review to `active`.
10. **Sign off `SECURITY.md`.** Then set DATA-001 ORR to `active`.

Then continue with `docs/agent_governance_implementation.md` once the agent's
purpose is known. Until then, normal working applies: **one plan per session**, and every change to
a protected path goes through `proposals/<plan ID>/` for the owner to apply. A
plan that amends a stage takes the stage's ID plus a lowercase letter: `S05a`,
then `S05b`.

---

## Assumptions

Change these before the run if they don't hold:

- **Governance tooling is Python 3.14 with pytest and PyYAML,** whatever
  language the product is written in. It runs the schema tests, hook tests
  and helper scripts. The product's linters, formatters and tests are out
  of scope: set them up separately. Governance code must pass whichever
  checks the repo already runs.
- **Claude Code is the main coding agent.** Its hooks and permission rules
  provide the deterministic build-time controls. `AGENTS.md` carries the
  same rules for other agents as instructions only, so for those agents the
  controls are ND, plus CI and human review.
- **Claude-only dev mode.** Every model is a Claude model, called through the
  Anthropic API. Paid Claude models are allowed with the owner's approval, recorded
  in the run inputs. No free local model is needed. The reviewer must have a
  different model ID from the planner and executor, but may be the same family;
  "Known gaps" records this to fix before production.
- **Repository:** GitHub, private, on GitHub Free, with one person (`Tomm-92`)
  authoring and reviewing. Branch protection, required checks and code-owner
  review are therefore unavailable. CI runs but is advisory, and the coding
  agent's inability to push is the merge control. See "When the repo
  changes".
- **Governance owner:** `Tomm-92`.
- **Runtime framework: Google ADK 2.14.** The product agent is one ADK
  agent tree, so one profile describes it. The runtime stages use the hook
  points in "Runtime hook points". For another framework, map them to its
  equivalents. If it has none, wrap the model and tool calls yourself.

## Principles

Each control below implements one of these. Sources are listed at the end.

1. **No governance, no agent.** If the rules are missing or unreviewed, the
   agent does not act. [JP]
2. **One canonical, versioned source.** Rules live only in `governance/`.
   Every session and commit records the hash of the rules in effect. [JP]
3. **Every rule has a reason.** "[subject] needs [constraint] because
   [consequence]". A rule without a reason is not ready to commit. [JP]
4. **Least autonomy, tiered.** Actions are `free`, `confirm` (a human
   approves each time) or `deny`. Keep `confirm` rare to avoid consent
   fatigue. [JP, AWS]
5. **Hard rules need deterministic controls.** Instructions bias the model
   and nothing more. Every `deny` rule has at least one deterministic (D)
   control; model judgement (ND) and humans (H) add to it. [AWS, HE]
6. **Agents propose, humans change rules.** No agent can edit governance,
   its own hooks or settings, or push. [JP]
7. **One intent per session.** Every session, whether a coding agent's or the
   product agent's, works on one declared and approved intent, within
   declared bounds. [JP, HE, AWS]
8. **Short sessions, rules re-confirmed.** Rules injected once fade as the
   context grows. Keep sessions short, restate the rules in effect with every
   prompt or model call, and stop a session whose rules changed after it
   started. [JP]
9. **Evidence or it didn't happen.** Transcripts, session logs, traces and
   verification results are kept, attributable and never summarised away.
   [JP, MA]
10. **Untrusted input is contained.** User input, retrieved content and model
    output are data, not instructions. The agent that talks to users cannot
    act. The agent that acts sees only the approved intent. Anything
    generated runs only in a sandbox with no credentials. [AWS, HE, MA]
11. **Correctness and compliance are separate signals.** Passing tests do not
    prove governance was followed. Each has its own check. [JP, HN]

## Concepts used throughout

| Term | Meaning |
| --- | --- |
| Tier | `free` (agent acts), `confirm` (human approves each time), `deny` (never). |
| Control type | **D** deterministic (hook, test, callback, scanner), **ND** model judgement (instruction, LLM review), **H** human. |
| Kind | `safety` (permanent) or `capability` (works around a current model's limits; review when the model changes). |
| Control status | `active` (built and working) or `planned`. Only the owner moves a control to `active`, in the change that makes it real. |
| Governance hash | `git rev-parse HEAD:governance`: the git tree hash of the committed `governance/` folder. Uncommitted rule edits are never in effect. |
| Trailers | Every commit ends with `Governance: <hash>` and `Plan: <plan ID>`. |
| Intent artifact | What a user approves before the product agent produces anything: a spec, plan, outline, query or change plan (`<profile.intent_artifact>`). |
| Work item | One approved intent, and everything produced for it. The product agent handles one work item per session. |
| Output | What the product agent produces for a work item (`<profile.output>`). It is written only under `<profile.output_root>/<work item>/`. |

## Runtime hook points

The runtime stages need these interception points. Use the framework's own
mechanism. Global plugins or middleware are best, because they cover every
agent in the system.

| Hook point | Used for | Google ADK 2.14 reference |
| --- | --- | --- |
| Before a run | Fail closed, check the governance hash, set session context | `BasePlugin.before_run_callback`; returning `types.Content` halts the run |
| On each event | Stamp the governance hash for evidence | `BasePlugin.on_event_callback`, `event.custom_metadata` |
| Before a model call | Re-inject rules, enforce the token budget | `before_model_callback`; returning an `LlmResponse` replaces the call |
| After a model call | Count tokens | `after_model_callback`, `usage_metadata` |
| Before a tool call | Tier check, path confinement, allowlists | `before_tool_callback`; returning a dict replaces the call |
| Human confirmation | `confirm`-tier tools | `FunctionTool(..., require_confirmation=bool or callable)` |
| Delegation with a schema | Executor receives only the approved intent | `sub_agents` task delegation with Pydantic `input_schema` |
| Durable session log | Evidence | `DatabaseSessionService`; event compaction off |
| Tracing | Observability | OpenTelemetry spans emitted by ADK (`google/adk/telemetry/`) |

---

## Project profile

`governance/profile.yaml` describes the project so that the generic rules and
phases can be applied to it. It is protected like the rest of `governance/`,
so a change to what the agent may produce or touch is a governance change.

Stage 2 fills the keys known at bootstrap. Phase A01 of
`docs/agent_governance_implementation.md` fills the purpose keys; its
appendices show two complete profiles.

```yaml
# Describes this project's agentic product. Rules and phases refer to these
# keys as <profile.key>. Change process: governance/README.md.
project: '<name>'
product_agent:                 # one ADK agent tree: a root agent and its sub-agents
  path: '<package of the agent, for example app>'
  framework: '<framework and pinned version, for example google-adk==2.14.0>'
  output_root: '<folder outputs are written under, for example output>'
  # Purpose keys: null or empty until phase A01.
  purpose: null                # one sentence on what the agent does for its users
  output: null                 # what it produces, for example REST API source code
  intent_artifact: null        # what users approve first, for example an OpenAPI 3 document
  tools: []                    # '<tool name>': '<what it does>'; tiers are set in tools.yaml
  verification: []             # stages from: secrets, sast, sca, iac, policy, structure, functional, conformance, content
  package_ecosystems: []       # registries the output may depend on, for example [go, pypi, npm]
  external_targets: []         # systems the agent may act on beyond files
```

## Rule catalogue

Copy this to `governance/rules.yaml` in Stage 2. In YAML inline maps
(`{...}`), **quote any value that contains a comma**. An unquoted comma
silently splits the value into extra keys; the schema test catches this.

```yaml
# Canonical rules for coding agents (build) and the product agent (runtime).
# Format and change process: governance/README.md. <profile.x> refers to
# governance/profile.yaml. A control's status moves from planned to active
# only through an owner PR, in the change that makes the control real.
# "(S0N)" names the stage in docs/governance_implementation.md, and "(A0N)"
# the phase in docs/agent_governance_implementation.md, that builds a planned
# control.
rules:
  # --- Governance itself -------------------------------------------------
  - id: GOV-001
    applies_to: [build]
    rule: A coding agent session needs committed governance before it acts on any prompt
    because: work done under missing or unreviewed rules cannot be audited against the rules that applied.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: session, by: UserPromptSubmit hook blocks prompts, status: active}
      - {type: ND, at: session, by: SessionStart hook injects the governance hash, status: active}

  - id: GOV-002
    applies_to: [build, runtime]
    rule: Governance and enforcement changes need the named owner's approval through a pull request
    because: relaxing a rule is higher risk than most features, and an agent that edits its own rules is ungoverned.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: session, by: Claude Code permission deny on protected paths, status: active}
      - {type: D, at: session, by: Claude Code permission deny on git push, status: active}
      - {type: D, at: session, by: PreToolUse hook denies git commit on main, status: active}
      - {type: D, at: session, by: Claude Code sandbox blocks indirect writes to protected paths (S04), status: planned}
      - {type: H, at: merge, by: owner review, status: active}

  - id: GOV-003
    applies_to: [build, runtime]
    rule: Every rule needs a because, a tier, a kind and at least one control
    because: a rule without a reason gets bypassed the first time it causes friction.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: commit, by: tests/governance/test_rules.py, status: active}

  - id: GOV-004
    applies_to: [build]
    rule: Every commit records the governance hash and plan ID in Governance and Plan trailers
    because: a change that cannot be tied to the rules and intent it was made under cannot be audited.
    tier: deny
    kind: safety
    controls:
      - {type: ND, at: session, by: AGENTS.md instruction, status: active}
      - {type: D, at: commit, by: .githooks/commit-msg (S04), status: planned}
      - {type: D, at: ci, by: governance workflow trailer check (S05), status: planned}

  - id: GOV-005
    applies_to: [runtime]
    rule: The product agent refuses to run without committed governance and stamps the governance hash on every session event
    because: a runtime session that cannot prove which rules it ran under is ungoverned risk.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: runtime, by: governance layer fails closed at startup and halts on hash change (S06), status: planned}

  - id: GOV-006
    applies_to: [build]
    rule: A coding agent session works only under the governance hash it started with, restated with every prompt
    because: rules injected once fade as the context grows, and a session whose rules changed partway works under rules it was never given.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: session, by: UserPromptSubmit hook restates the hash and plan and blocks on a hash change, status: active}
      - {type: ND, at: session, by: AGENTS.md instruction to start a new session per plan, status: active}

  # --- Scope -------------------------------------------------------------
  - id: SCOPE-001
    applies_to: [build]
    rule: Code edits need exactly one active execution plan in docs/exec-plans/active/
    because: an agent without one declared intent makes broader changes than anyone reviewed.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: session, by: PreToolUse hook denies edits, status: active}
      - {type: H, at: merge, by: reviewer checks the diff against the plan scope, status: active}

  - id: SCOPE-002
    applies_to: [build]
    rule: Edits stay inside the scope_paths declared by the active plan
    because: unbounded sessions produce unbounded side effects that review then has to find by hand.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: session, by: PreToolUse hook checks scope_paths (S04), status: planned}
      - {type: H, at: merge, by: reviewer checks the diff against the plan scope, status: active}

  # --- Evidence ----------------------------------------------------------
  - id: EVID-001
    applies_to: [build, runtime]
    rule: Evidence is retained and attributable for retention_days, and is never summarised away
    because: without a record of what an agent did, the only account is the agent's own explanation.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: commit, by: Governance and Plan trailers enforced by commit-msg (S04), status: planned}
      - {type: D, at: runtime, by: durable session log with compaction off (S06), status: planned}
      - {type: H, at: review, by: evidence review each sprint (S09), status: planned}

  # --- Secrets and data --------------------------------------------------
  - id: SEC-001
    applies_to: [build]
    rule: Agents never read, print or commit .env files
    because: secrets read into a session end up in transcripts, which are retained as evidence.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: session, by: Claude Code permission deny on .env, status: active}
      - {type: D, at: commit, by: .gitignore, status: active}

  - id: SEC-002
    applies_to: [build, runtime]
    rule: No hard-coded secrets reach a commit or an agent output
    because: a credential in code or output is exposed to everyone who can read it.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: ci, by: gitleaks in the governance workflow (S05), status: planned}
      - {type: D, at: runtime, by: secrets stage of verify.sh (A02), status: planned}

  - id: DATA-001
    applies_to: [runtime]
    rule: Prompts, sessions, traces and outputs go only to allowlisted services, and nobody gets interactive access to sandboxes
    because: user-supplied content may be confidential, and a shell into a sandbox bypasses every audit trail.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: ci, by: test that collector exporters match the allowlist (S08), status: planned}
      - {type: D, at: runtime, by: sandbox containers run without a TTY or exec access (A02), status: planned}
      - {type: H, at: review, by: ORR data-handling sign-off (S09), status: planned}

  # --- Dependencies, cost and models -------------------------------------
  - id: DEP-001
    applies_to: [build, runtime]
    rule: New external dependencies need explicit human approval and a version range or lockfile pin
    because: every unreviewed library is a future security and maintenance liability, and agents can hallucinate package names.
    tier: confirm
    kind: safety
    controls:
      - {type: H, at: merge, by: owner review of dependency manifests, status: active}
      - {type: D, at: runtime, by: allowlist and registry existence check (A01), status: planned}
      - {type: H, at: runtime, by: confirmation on non-allowlisted dependencies (A01), status: planned}
      - {type: D, at: ci, by: 'vulnerability audit and osv-scanner (S05, A02)', status: planned}

  - id: COST-001
    applies_to: [build, runtime]
    rule: Running an agent against a paid model needs approval, and every product-agent session has a token budget
    because: unbounded sessions spend credits nobody approved.
    tier: confirm
    kind: safety
    controls:
      - {type: H, at: session, by: coding agent asks before paid-model runs, status: active}
      - {type: D, at: runtime, by: governance layer enforces session_token_budget (S06), status: planned}

  - id: MODEL-001
    applies_to: [runtime]
    rule: Models are configured by exact model ID from the allowlist, and changing one runs the eval suite
    because: an alias or unreviewed model change silently changes behaviour that evals were calibrated against.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: commit, by: test that configured model IDs are allowlisted (S06), status: planned}
      - {type: D, at: ci, by: eval pass-rate gate on model change (A04), status: planned}

  # --- Runtime behaviour -------------------------------------------------
  - id: TOOL-001
    applies_to: [runtime]
    rule: Every product-agent tool has a tier in governance/tools.yaml, and calls to unlisted tools or targets are refused
    because: a tool or target nobody classified has whatever autonomy the model decides to give it.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: runtime, by: before-tool policy default-deny (S07), status: planned}

  - id: SPEC-001
    applies_to: [runtime]
    rule: Nothing is produced or changed until the user approves the intent artifact, and the executor receives only that approved artifact
    because: raw conversation can carry prompt injection and unbounded intent, and the approved artifact is the trust and scope boundary.
    tier: confirm
    kind: safety
    controls:
      - {type: H, at: runtime, by: confirmation on approve_intent (A03), status: planned}
      - {type: D, at: runtime, by: executor input schema accepts only ApprovedIntent (A03), status: planned}

  - id: FS-001
    applies_to: [runtime]
    rule: The product agent writes only under <profile.output_root>/<approved work item>/
    because: a write outside the approved work item can silently change another user's output or the agent itself.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: runtime, by: before-tool path check (S07), status: planned}

  - id: SBX-001
    applies_to: [runtime]
    rule: Anything the product agent generates is executed or scanned only in a sandbox with no credentials and allowlisted network only
    because: a prompt injection inside generated content can reach anything reachable from where it runs.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: runtime, by: verification sandbox container (A02), status: planned}

  - id: VER-001
    applies_to: [runtime]
    rule: An output is handed over only after verification passes the severity gate in thresholds.yaml
    because: passing tests confirm behaviour, not safety, and a critical finding shipped is an incident waiting.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: runtime, by: 'verify gate blocks delivery (A02, A03)', status: planned}
      - {type: H, at: runtime, by: user acknowledges high findings (A03), status: planned}

  - id: REV-001
    applies_to: [runtime]
    rule: The reviewer agent runs on a different model from the executor
    because: two sessions of the same model share blind spots, so self-review confirms rather than checks.
    tier: deny
    kind: capability
    controls:
      - {type: D, at: commit, by: test that reviewer and executor model IDs differ (A03), status: planned}

  # --- Observability and quality -----------------------------------------
  - id: OBS-001
    applies_to: [runtime]
    rule: Every model call and tool call emits the required telemetry attributes in ARCHITECTURE.md
    because: a failure that telemetry cannot attribute to model, harness, tool, sandbox or policy can only be debugged by guessing.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: commit, by: in-memory span exporter test (S08), status: planned}

  - id: QUAL-001
    applies_to: [build, runtime]
    rule: A score in docs/QUALITY_SCORE.md rises above 1 only with linked evidence that exists
    because: scores without evidence let people and agents declare victory early.
    tier: deny
    kind: safety
    controls:
      - {type: D, at: commit, by: test that every score above 1 links to an existing file or test (S09), status: planned}
```

## Thresholds and allowlists

Copy these in Stage 2. The values are proposals; the owner confirms them.

`governance/thresholds.yaml`:

```yaml
# Numeric limits enforced in code. Change process: governance/README.md.
session_token_budget: 200000   # COST-001: total tokens per product-agent session
max_fix_iterations: 3          # A03: executor retries after a failed verify
retention_days: 90             # EVID-001: keep transcripts, sessions, traces, reports
eval_runs: 5                   # A04: runs per eval case (temperature is often not 0)
eval_pass_rate_floor: 0.8      # A04: minimum pass rate across eval_runs
severity_gate:                 # VER-001: per-severity outcome of verification
  critical: block
  high: acknowledge
  medium: track
  low: track
```

`governance/allowlists/models.yaml`:

```yaml
# MODEL-001 and REV-001. Exact model IDs only; aliases are not allowed.
# Reviewer models must have a different ID from planner and executor models.
# They may be the same family until production (see Known gaps).
models:
  - {id: <exact model id>, use: [planner, executor], paid: true}
  - {id: <different exact model id>, use: [reviewer], paid: true}
```

`governance/allowlists/packages.yaml`:

```yaml
# DEP-001. Packages outputs may depend on without further approval, one list
# per ecosystem in <profile.package_ecosystems>.
<ecosystem>:
  - <package>
```

`governance/allowlists/services.yaml`:

```yaml
# DATA-001 and TOOL-001. The only external services that may receive prompts,
# sessions, traces or outputs, or that the agent may act on.
model_providers: []
telemetry_exporters: []
package_registries: []
external_targets: []
mcp_servers: []
```

## Reference scripts

These were tested in a previous project. Copy them in Stage 4.

`.claude/hooks/governance_gate.sh`:

```bash
#!/bin/bash
# GOV-001, GOV-006 and SCOPE-001. SessionStart can't block, so it only injects
# the governance hash and active plan, and pins the session to that hash.
# UserPromptSubmit blocks prompts while governance is missing, uncommitted or
# changed since the pin, and otherwise restates the hash and plan, because
# rules injected once fade as the context grows. PreToolUse denies edits
# unless exactly one plan is active (plan files are exempt so a plan can be
# drafted).
input=$(cat)
cd "$CLAUDE_PROJECT_DIR" || exit 0
event=$(jq -r .hook_event_name <<<"$input")
pin=.claude/.session_governance/$(jq -r .session_id <<<"$input")
mkdir -p .claude/.session_governance

if [[ ! -f governance/rules.yaml ]]; then
  problem='governance/rules.yaml is missing'
elif ! sha=$(git rev-parse -q --verify HEAD:governance); then
  problem='governance/ is not committed'
elif [[ -n $(git status --porcelain -- governance) ]]; then
  problem='governance/ has uncommitted changes'
fi
shopt -s nullglob
plans=(docs/exec-plans/active/*.md)
case ${#plans[@]} in
  0) plan='No active execution plan: code edits are blocked until one exists.' ;;
  1) plan="Active execution plan: ${plans[0]}. Read it before working." ;;
  *) plan="Several active plans (${plans[*]}): ask which applies; code edits are blocked." ;;
esac
status="Governance in effect: $sha (governance/rules.yaml). Use it in the commit trailer. $plan"

case $event in
  SessionStart)
    if [[ -n $problem ]]; then
      echo "Governance unavailable: $problem. Prompts are blocked until a human fixes and commits it." >&2
      exit 2
    fi
    # A new or cleared context starts under the current rules; a resumed or
    # compacted one keeps the rules it started with.
    source=$(jq -r .source <<<"$input")
    if [[ $source == startup || $source == clear || ! -f $pin ]]; then
      echo "$sha" >"$pin"
    fi
    if [[ $(<"$pin") == "$sha" ]]; then
      echo "$status"
    else
      echo "GOV-006: governance changed from $(<"$pin") to $sha after this session started. Prompts are blocked; start a new session, or /clear."
    fi
    ;;
  UserPromptSubmit)
    if [[ -n $problem ]]; then
      jq -n --arg r "No governance, no agent (GOV-001): $problem. Fix and commit governance/ yourself, then retry." \
        '{decision: "block", reason: $r}'
      exit 0
    fi
    # No pin yet when governance was first committed during this session.
    [[ -f $pin ]] || echo "$sha" >"$pin"
    if [[ $(<"$pin") != "$sha" ]]; then
      jq -n --arg r "GOV-006: governance changed from $(<"$pin") to $sha after this session started. Start a new session, or /clear, to work under the new rules." \
        '{decision: "block", reason: $r}'
      exit 0
    fi
    echo "$status"
    ;;
  PreToolUse)
    f=$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' <<<"$input")
    [[ $f == "$CLAUDE_PROJECT_DIR"/docs/exec-plans/* || ${#plans[@]} -eq 1 ]] && exit 0
    jq -n --arg r "SCOPE-001: edits need exactly one plan in docs/exec-plans/active/ (found ${#plans[@]}). Draft or choose one first." \
      '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
    ;;
esac
```

`.claude/hooks/branch_guard.sh`:

```bash
#!/bin/bash
# GOV-002. The owner's review is the only merge control, so the agent must
# never commit straight to main. Matches `git commit` and `git -C <dir> commit`
# anywhere in a compound command.
input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
[[ $cmd =~ git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+commit ]] || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
[[ $(git branch --show-current) == main ]] || exit 0
jq -n --arg r 'GOV-002: no commits on main. Create a branch and commit there; main changes only through a PR the owner merges.' \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
```

## Verified facts

These were checked against sources during a previous project, on Python 3.12. The
project now uses 3.14, so re-check any you rely on.

- **Claude Code hooks:**
  - SessionStart stdout becomes context; it **cannot block**.
  - UserPromptSubmit blocks with `{"decision": "block", "reason": ...}`.
    Its plain stdout on exit 0 is added as context alongside the prompt.
  - Hook input always carries `session_id`. SessionStart input also has
    `source`: `startup`, `resume`, `clear`, `compact` or `fork`.
  - PreToolUse denies with `hookSpecificOutput.permissionDecision: "deny"`.
  - Stderr from a hook that exits 0 is never seen.
- **Claude Code permissions:**
  - `Edit(...)` deny rules also cover Write and Bash `sed`, `tee` and
    redirects. They do **not** cover a script that writes files itself;
    Stage 4 adds the sandbox for that.
  - `/path` in project settings is relative to the session's primary
    working directory.
- **Google ADK 2.14** (reference framework):
  - `BasePlugin.before_run_callback` returning `types.Content` halts the
    run.
  - `on_event_callback` can replace an event, and `Event` has
    `custom_metadata`.
  - `App(plugins=[...])` exists.
  - `FunctionTool` and `McpToolset` accept `require_confirmation` (a bool or
    a callable), and `McpToolset` has `tool_filter`.
  - `SequentialAgent`, `ParallelAgent` and `LoopAgent` are deprecated in favour
    of `Workflow` graphs and `sub_agents` task delegation. `AgentTool` has no
    deprecation marker in the 2.14 source; the project avoids it by convention.
  - The eval generator looks for an optional `reset_data` on the agent package.
    Don't rely on it: isolate eval output yourself.
  - A base install has no `sqlalchemy` or `mcp`. `DatabaseSessionService` needs the
    `db` extra, `McpToolset` the `mcp` extra, and OTLP export the `otel` extra.
  - `AnthropicLlm` (`google.adk.models.anthropic_llm`) calls the Anthropic API and
    needs the `anthropic` package. Pass an instance as the model: a `claude-*`
    string resolves to `Claude`, its Vertex AI subclass.
- **Models:** some models, such as `claude-haiku-5-5`, reject temperature 0,
  so report evals as pass rates over several runs.
- **LiteLLM:** use `ollama_chat/`, not `ollama/`, or tool calls can loop.

## Known gaps

Seed `docs/exec-plans/tech-debt-tracker.md` with these:

| Gap | Rule | Close by |
| --- | --- | --- |
| The bootstrap run itself isn't gated by these controls: its rules are instructions until the owner applies the proposal, and a long run works against short sessions. Code quality's locks and gates do apply. | GOV-001, GOV-002, GOV-006, SCOPE-001, SCOPE-002 | The owner reviews the whole branch before merging. Closes for later sessions when the owner applies the proposal |
| Deny rules don't stop scripts that write files themselves. | GOV-002 | Stage 4 sandbox, live once the owner applies it |
| The plan check proves a plan exists, not that edits stay in scope. | SCOPE-002 | Stage 4, live once the owner applies it |
| Commit trailers are instructions, not checks. | GOV-004 | Stages 4 and 5, live once the owner sets `core.hooksPath` |
| The prompt hook restates the governance hash and plan, not the rules' text, and nothing limits a coding session's length. | GOV-006 | Stage 9 evidence review: tighten if transcripts show drift late in sessions |
| Coding agents other than Claude Code get the rules as instructions only. | GOV-001, GOV-002, GOV-006, SCOPE-001 | CI checks (Stage 5) and owner review |
| CODEOWNERS, branch protection and required checks are unavailable on private GitHub Free with one author. | GOV-002, DEP-001 | See "When the repo changes" |
| In Claude-only dev mode the reviewer has a different model ID but may be the same family as the planner and executor, so they can share blind spots. | REV-001 | Before production: move the reviewer to a different model family and run the eval suite (MODEL-001) |
| All runtime rules are planned until the owner applies the activation proposal. | GOV-005 to QUAL-001 | Stages 6 to 10, then A01 to A06 in `docs/agent_governance_implementation.md` |

## When the repo changes

When the repo goes public, gains a second collaborator, or moves to GitHub
Pro:

1. Protect `main`: require a pull request, code-owner review and the Stage 5
   and A04 checks.
2. Make those checks blocking on `main` and advisory on other branches.
   Critical findings block; high findings need written justification.
3. Add `{type: D, at: merge, by: CODEOWNERS with branch protection, status:
   active}` to GOV-002 and DEP-001.
4. Remove the corresponding tech-debt entry.

## Sources

- **[JP]** Paul Johnston, "Agentic development best practices" (Medium).
- **[HN]** Harness, "Engineering for the agentic era: how to spec, build, test
  and operate AI systems".
- **[AWS]** AWS Security Blog, "Balancing speed and safety: a control
  framework for AI coding agents".
- **[HE]** Onaopemipo Oluborode, "Harness engineering: what I tried out"
  (Towards Dev), after OpenAI's "Harness engineering" article.
- **[MA]** Anthropic Engineering, "Scaling Managed Agents: decoupling the
  brain from the hands".
