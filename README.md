# agentic_bootstrap

The starting point for every agentic development project. A new project starts from
this repo, so it gets the same governance, transparency, observability and code
quality controls from its first commit. The goal is consistent development and
reliable, production-ready outcomes, whoever or whatever writes the code.

`app/` holds a placeholder Google ADK agent, which each project replaces with its
real one.

## Getting started

The bootstrap is built from four instruction files in `docs/`. The first three are
already applied in every clone, so you only run the fourth:

| Order | File | What it adds | In a fresh clone |
| --- | --- | --- | --- |
| 1 | `docs/bootstrap-implementation/initial_install.md` | Git, Python 3.14, Google ADK, first commit | Done |
| 2 | `docs/bootstrap-implementation/codequality.md` | Lint, type and test gates | Done |
| 3 | `docs/bootstrap-implementation/project_governance.md` | Every control that doesn't depend on the agent's purpose | Done |
| 4 | `docs/bootstrap-implementation/agent_governance.md` | Tools, sandboxed verification, intent approval, independent review and evals for your agent | **You run this** |

Getting going takes five steps: set up your clone, know what your agent is for,
check the prerequisites, run file 4, then apply what it proposes.

### 1. Set up your clone

Run:

```bash
python3.14 -m venv .venv
.venv/bin/pip install -r requirements-dev.lock
git config core.hooksPath .githooks
```

Always open Claude Code at the repo root. It loads `.claude/settings.json` only from
the folder it was launched in, so a session opened from a parent folder runs none of
the hooks or deny rules.

### 2. Know what your agent is for

You need only two answers ready, each in a sentence:

- **Purpose:** what the agent does for its users. For example, *"Designs REST APIs
  with the user and generates them in Go or Python."*
- **Output:** what it produces. For example, *"REST API source code"*.

The run asks for these first. Then it takes you through the remaining choices one at a
time. For each one it explains what the choice controls, recommends an answer based on
your purpose and output, and lets you accept it, pick another option or answer in your
own words:

| Choice | What it decides |
| --- | --- |
| Intent artifact | What your users approve before the agent builds anything, such as an OpenAPI document |
| Agent tree | How many agents do the work. The default is one planner, one executor and a reviewer |
| Tools | What the agent can do, and which actions need the user's confirmation |
| Verification | Which checks every output must pass, such as secret scanning or tests |
| Packages | Which package registries and packages the output may use |
| External systems | Any system the agent may act on beyond files, such as a GitHub repo |
| Reviewer model | The model that independently reviews the agent's work |
| Spending | Whether the run may make paid model calls to test the agent. The recommendation is no, and those checks are left for you to run later |

At the end it shows all your answers together, so you can change any of them before it
starts building. If you can't answer a choice, the run records it as an open question
and skips the parts that depend on it. It never guesses.

### 3. Check the prerequisites

- A container runtime, such as Docker, is reachable from your terminal. The run
  verifies generated output in a disposable sandbox. The Claude Code sandbox blocks
  Docker, so the session never runs those checks itself.
- `ANTHROPIC_API_KEY` is set in your environment.
- **Neither session is in `bypassPermissions` or `dontAsk` mode.** Manual and auto mode
  are both fine. `branch_guard.sh` denies paid model calls outside manual mode
  (COST-001), so an auto-mode session makes none.

The run still finishes without Docker, without the key, or in auto mode. Each check it
can't run is recorded as `deferred`, and the final report lists them all as one batch
of commands for you to run.

### 4. Run the agent governance implementation

The run takes two Claude Code sessions, with one step of yours in between.

**Design session.** Start Claude Code at the repo root and say:

> *"Run the design session in docs/bootstrap-implementation/agent_governance.md."*

It asks the questions from step 2. Then it writes three documents on the branch
`governance-agent-purpose`, and stops after each one for you:

1. **The agent's intent** (`docs/execution-plans/intent/A00-agent-purpose.md`). Set
   `Status: accepted` and `Accepted by:` when you agree with it.
2. **The spec** (`docs/execution-plans/spec/A00-agent-purpose.md`). It fixes the agent
   tree, the tools and tiers, the checks, and the exact files each part may touch.
   Accept it the same way.
3. **Plan A00,** in plan mode. Approve it as Claude leaves plan mode.

It ends with a small first proposal in `proposals/A00/` (the profile, `tools.yaml` and
the allowlists), all in one commit.

**Apply the first proposal.** Review it, then run:

```bash
cp -R proposals/A00/. . && rm -rf proposals/A00
git add -A && git commit -m "Apply proposal A00: profile, tools and allowlists" \
  -m "Governance: $(git rev-parse HEAD:governance)
Plan: A00"
```

**Build session.** Start a new session and say:

> *"Build plan A00."*

It first checks that the guardrails hold inside subagents. Approve the one permission
prompt it raises: the command only prints help text. Then it builds each part, A01 to
A05, in its own fresh subagent, and checks each part before starting the next. It
asks you something only when a part needs a file, a tier change or a paid call that
the spec didn't cover. It never commits on `main` and never pushes. It ends with a
report of what passed, what was deferred and what you need to do.

### 5. Apply the final proposal

Do these yourself, on the `governance-agent-purpose` branch. The full list is in
"After the run" in `docs/bootstrap-implementation/agent_governance.md`.

1. **Review** `proposals/A00/` and `docs/records/governance_activation.md`.
2. **Check and apply** the proposal, then commit it:

   ```bash
   .venv/bin/python scripts/check_activation.py proposals/A00/governance/rules.yaml
   cp -R proposals/A00/. . && rm -rf proposals/A00
   git add -A && git commit -m "Apply proposal A00" \
     -m "Governance: $(git rev-parse HEAD:governance)
   Plan: A00"
   ```

3. **Decide on eval spending.** The evals workflow makes paid model calls nightly
   and on matching pull requests. Add `ANTHROPIC_API_KEY` as a repo secret only if
   you approve that cost.
4. **Push, open a pull request and merge.**
5. **Start a new session,** and rerun the tests.
6. **Run the deferred checks** listed in the report, and mark each control
   `active` in `docs/records/governance_activation.md` once its check passes.

Before your first release, also hold the first evidence review and sign off
`docs/records/security.md`, as items 7 and 8 of "After the run" describe.

From then on, build your agent one change at a time, with one execution plan per
session, as described in [How it works](#how-it-works).

## Why a bootstrap repo

Coding agents write code fast. Without shared guardrails, every project picks its own
rules, checks and logging, and each one is governed differently. Some are not governed
at all. Nobody can say for sure what an agent did, which rules it followed or whether
its output is safe to ship.

This repo fixes that by making the controls part of the project's starting state. They
are in place before anything is built, so no team has to add them later. Every project
built from it has these four things.

**Governance.** The rules are written down in `governance/rules.yaml`. Each one has a
reason, a tier and at least one control that enforces it. Hooks, permission deny rules,
git hooks and CI apply them, so they do not rely on the agent following instructions.
Agents cannot edit the rules or their enforcement. Changes go through a proposal that
the owner reviews. The product agent itself fails closed without committed governance,
refuses unclassified tools and keeps to a token budget.

**Transparency.** Every change starts as an intent, which becomes a spec and then an
execution plan that states its scope, decisions and risks. The owner accepts each one
before the next is written. Edits outside the plan's scope are blocked. Every commit records
the governance hash and plan ID it was made under, so any change can be traced back to
the rules and intent behind it. Runtime sessions go to a durable log that is never
summarised away. `docs/records/quality_score.md` can only claim progress with linked evidence.

**Observability.** Every model call and tool call emits OpenTelemetry spans with the
session, user, governance hash and guardrail result. When something fails, the span
says whether the cause was the model, the harness, a tool, a policy or the sandbox.
Metrics count blocked tool calls, confirmations, budget refusals and token use.
`observability/` holds a local collector, Tempo, Prometheus and Grafana stack, with
alerts.

**Code quality.** Ruff, vulture, mypy (strict) and the unit tests run after every agent
edit, before every turn ends, and in CI on every pull request. Tests use a scripted fake
model, so they cost nothing. Real-model tests are kept separate. ADK conventions are
checked by tests and by the `/adk-review` command.

Together these turn agent-driven development into a repeatable process. Each project
starts from the same controls and leaves the same evidence. Each one reaches production
through the same gates.

## Why Google ADK

The product agent is built on Google's Agent Development Kit (ADK). It was chosen
because its extension points let governance live in the framework instead of in prompts:

- **Plugins and callbacks.** A single `GovernancePlugin` attached to the `App` sees
  every run, model call, tool call and event. It fails closed, enforces the token
  budget and tool policy, and stamps evidence. The rules are enforced in code, not only
  stated in instructions.
- **Model choice.** ADK is not tied to Gemini. This repo runs Claude through
  `AnthropicLlm`, with each model pinned by exact ID from an allowlist. A model can
  change without the agent being rewritten.
- **Durable sessions.** `DatabaseSessionService` keeps a full, queryable record of every
  session, which the evidence rules depend on.
- **Built-in telemetry.** ADK emits OpenTelemetry spans for agent and tool execution.
  The governance layer adds its own attributes to them, without a separate tracing
  setup.
- **Structured multi-agent design.** `Workflow` graphs and sub-agents with
  `mode='single_turn'` or `mode='task'` and typed `input_schema`s make the delegation
  explicit. That lets later phases separate the agent that plans from the one that
  acts, and give the reviewer its own model.
- **Evaluation.** ADK's eval format gives a standard way to write behavioural tests,
  which later phases run as a gate whenever a model changes.
- **Open source and production-ready.** ADK is maintained by Google and installed as a
  pinned, locked dependency. Its CLI covers local development (`adk web`), evals
  (`adk eval`) and deployment (`adk deploy` to Cloud Run, Agent Engine, GKE or a
  Docker image).

## How it works

`docs/records/governance_activation.md` records which controls are active. The owner activates
planned controls one at a time, as each one becomes real.

### Development process

Every change follows the committed-artifact chain from the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook):
intent, then spec, then plan, then build. Each artifact is a file, and the owner
accepts it before the next one is written.

| Artifact | Where | Accepted by | Acceptance starts |
| --- | --- | --- | --- |
| Intent | `docs/execution-plans/intent/<ID>-<name>.md` | Owner sets `Status: accepted` | Writing the spec |
| Spec | `docs/execution-plans/spec/<ID>-<name>.md` | Owner sets `Status: accepted` | Plan mode |
| Plan | `docs/execution-plans/plan/active/<ID>-<name>.md` | Owner approves the plan as Claude leaves plan mode | Building |

All three share one ID and name, and each starts from its template in
`docs/execution-plans/templates/`. The playbook names a product owner, a policy owner and
a tech lead. Here the owner plays every role. Agents draft intents and specs, but
only the owner sets `Status: accepted`.

**Small changes skip the intent and spec.** Fixes that restore documented behaviour,
doc corrections and dependency bumps start at the plan, whose Goal says
`Intent: none (<reason>)`. Everything else starts with an intent, including changes to
governance and to this process.

**One commit holds all three.** Commits need a `Plan:` trailer naming a plan in
`active/` or `completed/`, so an intent can't be committed on its own. Acceptance is
recorded in each file's header, and the intent, spec and plan are committed together.

**Not the product agent's intent artifact.** An `intent.md` here describes a change to
this repo. The product agent's intent artifact (`intent_artifact` in
`governance/profile.yaml`, SPEC-001) is what the agent's users approve before it
builds their output.

**Planning in plan mode:**

1. Start Claude Code in plan mode: `claude --permission-mode plan`, or press Shift+Tab.
2. Ask it to plan from the accepted spec, for example: *"Plan the change in
   docs/execution-plans/spec/0018-x.md."*
3. Question the plan before you accept it. Ask what could break, which step is
   riskiest, and which options it didn't take. Iterate until an engineer who never saw
   the conversation could build the change from the plan alone.
4. Approve it. Claude leaves plan mode and writes the plan to
   `docs/execution-plans/plan/active/` from the template. The edit gate exempts plan files.
   Review the file, then commit the intent, spec and plan together.
5. Build in the same session, or in a new one (GOV-006: one plan per session). When
   the build departs from the plan, update the plan in the same commit.
6. Review and commit as in [Review after each commit](#code-quality), then move the
   plan to `docs/execution-plans/plan/completed/`.

### Governance

The rules live in `governance/`, and `AGENTS.md` is the entry point for any coding
agent. See `governance/README.md` for the rule format and change process.

![Governance controls: each rule, why it exists, and where it is enforced](docs/diagrams/governance_controls.svg)

The graphic is a snapshot of `governance/rules.yaml`, which wins if they differ.

**The gate.** No governance, no agent: a session's prompts are blocked while
`governance/` is missing, uncommitted or dirty, and once its hash differs from the
one the session started with. Edits need exactly one active plan, and must stay inside
that plan's `scope_paths`. The product agent fails closed the same way at startup.

**Protected paths.** Agents can't edit `governance/`,
`docs/bootstrap-implementation/project_governance.md`, `docs/bootstrap-implementation/agent_governance.md`,
`.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks/`, `.github/`,
`.githooks/`, the instruction files (`AGENTS.md`, `CLAUDE.md`, `app/AGENTS.md` and
`app/CLAUDE.md`), or the check config (`ruff.toml`, `pytest.ini` and `mypy.ini`).

**Proposals.** To change a protected path, an agent writes the new version to
`proposals/<plan ID>/` at the same relative path. The owner reviews it, copies it into
place and commits.

**Execution plans.** Each session after the bootstrap run works under one plan at
`docs/execution-plans/plan/active/<plan ID>-<name>.md`, written from
`docs/execution-plans/templates/plan.md` as the
[development process](#development-process) describes. The gate reads its front
matter: `id`, the `rules` it works under and the `scope_paths` it may edit.

The session records its work there, lists its owner actions at the end, and moves the
plan to `docs/execution-plans/plan/completed/`. The edit gate allows plan files, so this is always
possible. "Owner actions" are for the human: a session lists them and does not attempt
them.

**Runtime.** `app/governance.py` is the governance layer. To run one session against
the durable log at `.sessions/sessions.db`. It uses a scripted model and spends
nothing unless you pass `--real`, which calls the paid model (COST-001):

```bash
.venv/bin/python -m scripts.local_session "What is the status of demo?"
```

`observability/` holds the local telemetry stack, and `.venv/bin/python -m
scripts.evidence_report` summarises the evidence for `docs/records/evidence_review.md`.

### Coding agents

Any coding agent can work here. `AGENTS.md` is the entry point, and `app/AGENTS.md`
adds the ADK conventions for work in `app/`. `CLAUDE.md` and `app/CLAUDE.md` import
them for Claude Code. Enforcement differs by agent, because only Claude Code runs
the session hooks:

| Control | Claude Code | Other agents |
| --- | --- | --- |
| Instructions | `AGENTS.md` files, through the `CLAUDE.md` imports | `AGENTS.md` files, where the tool reads nested ones |
| Lint, format, types, dead code, unit tests | Hooks on every edit and turn, then CI | CI on every pull request |
| Commit trailers | `commit-msg` hook, then CI | `commit-msg` hook, then CI |
| Plan scope | File edits outside it are blocked; CI's plan scope check reports shell writes | CI's plan scope check reports them |
| Protected paths | Blocked by deny rules and the sandbox | CI lists them for the owner's review |
| No push, no commits on `main` | Blocked by `branch_guard.sh` | Only branch protection, once enabled |
| One governance hash per session | Prompts blocked when it changes | Not enforced |

The CI checks are advisory until the repo has required status checks.

### Code quality

Code quality is enforced by automatic checks. The priority is concise code
that follows Google ADK conventions. `AGENTS.md` and `app/AGENTS.md` hold the
rules, and the checks below enforce them.

**Automatic checks.** These run through the hooks in .claude/settings.json,
so they cost no extra usage.
- After every Edit or Write of a Python file, `lint_on_edit.sh` runs
  `ruff check --fix` and `ruff format` on that file, then reports anything ruff
  can't fix to Claude.
- When Claude tries to finish a turn that changed files, `checks_on_stop.sh`
  runs ruff (lint and format), the suppression reason check, vulture, mypy and
  the unit tests. If one fails, Claude is blocked once and keeps working. If the
  retry also fails, the hook tells you instead of blocking again, and doesn't
  re-check until the files change.

What the checks cover:
- ruff.toml: formatting and common errors, needlessly roundabout code,
  commented-out code, unused arguments, blind exception handling, complexity
  and size limits, type hints, `print`, security (Bandit), and `noqa` comments
  that are bare or stale. It also bans ADK's deprecated `SequentialAgent`,
  `ParallelAgent`, `LoopAgent` and `AgentTool`.
- mypy.ini: strict type checks on `app`, `tests` and `scripts`. Every `type: ignore` must
  name its code, and stale ones fail.
- tests/unittests/: free tests that use a scripted fake model and fail on any
  network connection, plus ADK convention tests in `test_adk_conventions.py`.
- tests/integration/: real-model tests that spend credits. They only run with
  `.venv/bin/pytest -m integration`, and Claude Code asks you first.

Deny rules and the sandbox in .claude/settings.json stop Claude from editing the
hooks, its settings, the CI workflows, `ruff.toml`, `mypy.ini` and `pytest.ini`.
Change those yourself, by hand or through a pull request.

**Review commands.** Run the review commands by hand, after a commit. `/intent`, `/spec`
and `/spec-security` run earlier, before the plan. Claude calls the verifier itself
before reporting a task done.

| Command | What it does | Source |
| --- | --- | --- |
| Ask for the `verifier` | Runs the same checks as CI, plus a scripted session for `app/` changes, and reports the output. Never edits | `.claude/agents/verifier.md` |
| `/adk-review` | Checks changes against this project's ADK conventions, citing `app/AGENTS.md`, `AGENTS.md` or the installed ADK source | `.claude/skills/adk-review/SKILL.md` |
| `/intent` | Drafts a new intent from the template, under the next free ID. Claude also uses it whenever it drafts one | `.claude/skills/intent/SKILL.md` |
| `/spec` | Drafts a spec from an accepted intent and runs `/spec-security` on it. Claude also uses it whenever it drafts one | `.claude/skills/spec/SKILL.md` |
| `/spec-security` | Checks a spec, not code, against the security checklist, citing rule IDs | `.claude/skills/spec-security/SKILL.md` |
| `/simplify` | Finds duplication and needless complexity, and fixes them | Built into Claude Code |
| `/code-review low` | Finds bugs, reporting fewer, higher-confidence findings | Built into Claude Code |

**One security checklist, one reviewer per stage.** `.claude/skills/spec-security/checklist.md`
is the only list of security checks. `/spec-security` applies it to specs, and the CI
review applies it to pull requests through `REVIEW.md`. Claude Code's built-in
`/security-review` is switched off in `.claude/settings.json` (`skillOverrides`), because
it would review the same diffs without this repo's rules. The owner signs off every
change to the checklist.

**CI.** The `checks` workflow runs the Stop hook's checks on every pull request
and every push to `main`, for any agent or person. Merging needs it to pass once
it is a required status check in the branch protection rules.

**Review after each commit.** Features are planned and built as the
[development process](#development-process) describes. The hooks keep each turn
clean. Then:
1. Commit. The reviews only look at changes since the last commit, so small
   commits keep them cheap.
2. Run `/adk-review` and `/simplify`, then `/code-review low`.
3. Commit the fixes.

Run integration tests with `.venv/bin/pytest -m integration` before merging
anything that changes model-facing behaviour.

Run the checks by hand:

```bash
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/vulture app tests scripts --min-confidence 80 && .venv/bin/mypy
.venv/bin/pytest
```

Runtime dependencies go in `requirements.txt` and tools in
`requirements-dev.txt`. After changing a range, re-lock with
`.venv/bin/pip freeze > requirements-dev.lock`.
