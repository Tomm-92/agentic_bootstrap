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
| 1 | `docs/initial_install.md` | Git, Python 3.14, Google ADK, first commit | Done |
| 2 | `docs/codequality.md` | Lint, type and test gates | Done |
| 3 | `docs/governance_implementation.md` | Every control that doesn't depend on the agent's purpose | Done |
| 4 | `docs/agent_governance_implementation.md` | Tools, sandboxed verification, intent approval, independent review and evals for your agent | **You run this** |

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

- A container runtime, such as Docker, is reachable from the session. The run
  verifies generated output in a disposable sandbox.
- `ANTHROPIC_API_KEY` is set in your environment.

Without these the run still finishes, but the checks that need them are recorded as
`deferred`, with the exact command for you to run later.

### 4. Run the agent governance implementation

Start one Claude Code session at the repo root and say:

> *"Implement docs/agent_governance_implementation.md in one run, from A01 to
> A06."*

It starts with the questions from step 2. Once you confirm your answers, it needs
nothing more from you until it ends. It:

- creates the branch `governance-agent-purpose` and the plan
  `docs/exec-plans/active/A00-agent-purpose.md`, and commits there after each part
  (A01 to A06). It never commits on `main` and never pushes.
- builds the agent's tools, sandbox, intent approval, review and evals in `app/`,
  `scripts/` and `tests/`.
- writes every change to governance files, such as `governance/profile.yaml`,
  `governance/tools.yaml` and `app/AGENTS.md`, to `proposals/A00/` instead. Agents
  can't edit those files, so you apply them.
- ends with a report listing what passed, what was deferred and what you need to do.

Until you apply the proposal, your agent's new tools are denied when it runs. That
is expected: the live `governance/tools.yaml` has no entry for them yet.

### 5. Apply the proposal

Do these yourself, on the `governance-agent-purpose` branch. The full list is in
"After the run" in `docs/agent_governance_implementation.md`.

1. **Review** everything in `proposals/A00/`, especially `governance/profile.yaml`,
   `governance/tools.yaml` and the allowlists. Check that each tool's tier matches
   what it can do.
2. **Choose the extra rules.** The run suggests new rules in
   `proposals/A00/governance/rules-additions.yaml`. Copy the ones you want into
   `proposals/A00/governance/rules.yaml`, add a row for each to
   `docs/governance-activation.md`, then delete the additions file.
3. **Check and apply** the proposal, then commit it:

   ```bash
   .venv/bin/python scripts/check_activation.py proposals/A00/governance/rules.yaml
   cp -R proposals/A00/. . && rm -rf proposals/A00
   git add -A && git commit -m "Apply proposal A00" \
     -m "Governance: $(git rev-parse HEAD:governance)" -m "Plan: A00"
   ```

4. **Decide on eval spending.** The evals workflow makes paid model calls nightly
   and on matching pull requests. Add `ANTHROPIC_API_KEY` as a repo secret only if
   you approve that cost.
5. **Push, open a pull request and merge.** Any open Claude Code session stops at
   its next prompt, because the governance hash has changed.
6. **Start a new session.** The new tools now have tiers, so they run under the
   policy.
7. **Run the deferred checks** listed in the report, and mark each control
   `active` in `docs/governance-activation.md` once its check passes.

Before your first release, also hold the first evidence review and sign off
`docs/SECURITY.md`, as items 8 and 9 of "After the run" describe.

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

**Transparency.** All work runs under an execution plan that states its intent, scope,
decisions and risks. Edits outside the plan's scope are blocked. Every commit records
the governance hash and plan ID it was made under, so any change can be traced back to
the rules and intent behind it. Runtime sessions go to a durable log that is never
summarised away. `docs/QUALITY_SCORE.md` can only claim progress with linked evidence.

**Observability.** Every model call and tool call emits OpenTelemetry spans with the
session, user, governance hash and guardrail result. When something fails, the span
says whether the cause was the model, the harness, a tool, a policy or the sandbox.
Metrics count blocked tool calls, confirmations, budget refusals and token use.
`ops/observability/` holds a local collector, Tempo, Prometheus and Grafana stack, with
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

`docs/governance-activation.md` records which controls are active. The owner activates
planned controls one at a time, as each one becomes real.

### Governance

The rules live in `governance/`, and `AGENTS.md` is the entry point for any coding
agent. See `governance/README.md` for the rule format and change process.

![Governance controls: each rule, why it exists, and where it is enforced](docs/images/governance-controls.svg)

The graphic is a snapshot of `governance/rules.yaml`, which wins if they differ.

**The gate.** No governance, no agent: a session's prompts are blocked while
`governance/` is missing, uncommitted or dirty, and once its hash differs from the
one the session started with. Edits need exactly one active plan, and must stay inside
that plan's `scope_paths`. The product agent fails closed the same way at startup.

**Protected paths.** Agents can't edit `governance/`,
`docs/governance_implementation.md`, `docs/agent_governance_implementation.md`,
`.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks/`, `.github/`,
`.githooks/`, the instruction files (`AGENTS.md`, `CLAUDE.md`, `app/AGENTS.md` and
`app/CLAUDE.md`), or the check config (`ruff.toml`, `pytest.ini` and `mypy.ini`).

**Proposals.** To change a protected path, an agent writes the new version to
`proposals/<plan ID>/` at the same relative path. The owner reviews it, copies it into
place and commits.

**Execution plans.** Each session after the bootstrap run writes a plan at
`docs/exec-plans/active/<plan ID>-<name>.md`, starting with this front matter:

```yaml
---
id: '0002'
rules: [SCOPE-001]
scope_paths:
  - app/**
---
```

The session records its work there, lists its owner actions at the end, and moves the
plan to `docs/exec-plans/completed/`. The edit gate allows plan files, so this is always
possible. "Owner actions" are for the human: a session lists them and does not attempt
them.

**Runtime.** `app/governance.py` is the governance layer. To run one session against
the durable log at `.sessions/sessions.db`. It uses a scripted model and spends
nothing unless you pass `--real`, which calls the paid model (COST-001):

```bash
.venv/bin/python -m scripts.local_session "What is the status of demo?"
```

`ops/observability/` holds the local telemetry stack, and `.venv/bin/python -m
scripts.evidence_report` summarises the evidence for `docs/REVIEW.md`.

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
  `ParallelAgent`, `LoopAgent` and `AgentTool`, and importing `ToolContext` from
  `google.adk.tools`.
- mypy.ini: strict type checks on `app`, `tests` and `scripts`. Every `type: ignore` must
  name its code, and stale ones fail.
- tests/unittests/: free tests that use a scripted fake model and fail on any
  network connection, plus ADK convention tests in `test_adk_conventions.py`.
- tests/integration/: real-model tests that spend credits. They only run with
  `.venv/bin/pytest -m integration`, and Claude Code asks you first.

Deny rules and the sandbox in .claude/settings.json stop Claude from editing the
hooks, its settings, the CI workflows, `ruff.toml`, `mypy.ini` and `pytest.ini`.
Change those yourself, by hand or through a pull request.

**Review commands.** Run these by hand, after a commit.

| Command | What it does | Source |
| --- | --- | --- |
| `/adk-review` | Checks changes against this project's ADK conventions, citing `app/AGENTS.md`, `AGENTS.md` or the installed ADK source | `.claude/skills/adk-review/SKILL.md` |
| `/simplify` | Finds duplication and needless complexity, and fixes them | Built into Claude Code |
| `/code-review low` | Finds bugs, reporting fewer, higher-confidence findings | Built into Claude Code |

**CI.** The `checks` workflow runs the Stop hook's checks on every pull request
and every push to `main`, for any agent or person. Merging needs it to pass once
it is a required status check in the branch protection rules.

**Workflow for each feature:**
1. Build the feature. The hooks keep each turn clean.
2. Commit. The reviews only look at changes since the last commit, so small
   commits keep them cheap.
3. Run `/adk-review` and `/simplify`, then `/code-review low`.
4. Commit the fixes.

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
