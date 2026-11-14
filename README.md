# agentic_bootstrap

The starting point for every agentic development project. A new project starts from
this repo, so it gets the same governance, transparency, observability and code
quality controls from its first commit. The goal is consistent development and
reliable, production-ready outcomes, whoever or whatever writes the code.

`app/` holds a placeholder Google ADK agent, which each project replaces with its
real one.

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

## Starting a new project

A project is built from four instruction files in `docs/`. Run each one in its own
Claude Code session, opened at the repo root:

| Order | File | What it adds |
| --- | --- | --- |
| 1 | `docs/initial_install.md` | Git, Python 3.14, Google ADK, first commit |
| 2 | `docs/codequality.md` | Lint, type and test gates |
| 3 | `docs/governance_implementation.md` | Every control that doesn't depend on the agent's purpose |
| 4 | `docs/agent_governance_implementation.md` | The controls that do, once the purpose is known: tools, sandboxed verification, intent approval, independent review and evals |

`docs/governance-activation.md` records which controls are active. The owner activates
planned controls one at a time, as each one becomes real.

## How it works

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
`.githooks/`, `AGENTS.md` or `CLAUDE.md`.

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

**Open sessions at the repo root.** Claude Code loads `.claude/settings.json` only from
the folder it was launched in, so a session opened from a parent folder runs none of
the hooks or deny rules.

**Setup.** Turn on the git hooks once in each clone:

```bash
git config core.hooksPath .githooks
```

**Runtime.** `app/governance.py` is the governance layer. To run one session against
the durable log at `.sessions/sessions.db`, with `--fake` to spend nothing:

```bash
.venv/bin/python -m scripts.local_session --fake "What is the status of demo?"
```

`ops/observability/` holds the local telemetry stack, and `.venv/bin/python -m
scripts.evidence_report` summarises the evidence for `docs/REVIEW.md`.

### Code quality

Code quality is enforced by automatic checks. The priority is concise code
that follows Google ADK conventions. CLAUDE.md holds the rules, and the
checks below enforce them.

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

Open Claude Code at the repo root. A session opened from a parent folder runs
none of the hooks.

What the checks cover:
- ruff.toml: formatting and common errors, needlessly roundabout code,
  commented-out code, unused arguments, blind exception handling, complexity
  and size limits, type hints, `print`, security (Bandit), and `noqa` comments
  that are bare or stale. It also bans ADK's deprecated `SequentialAgent`,
  `ParallelAgent`, `LoopAgent` and `AgentTool`.
- mypy.ini: strict type checks on `app`, `tests` and `scripts`. Every `type: ignore` must
  name its code, and stale ones fail.
- tests/unittests/: free tests that use a scripted fake model, plus ADK
  convention tests in `test_adk_conventions.py`.
- tests/integration/: real-model tests that spend credits. They only run with
  `.venv/bin/pytest -m integration`.

Deny rules in .claude/settings.json stop Claude from editing the hooks, its
settings, the CI workflows, `ruff.toml`, `mypy.ini` and `pytest.ini`. Change those
yourself, by hand or through a pull request.

**Review commands.** Run these by hand, after a commit.

| Command | What it does | Source |
| --- | --- | --- |
| `/adk-review` | Checks changes against this project's ADK conventions, citing CLAUDE.md or the installed ADK source | `.claude/skills/adk-review/SKILL.md` |
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

**Setup:**

```bash
python3.14 -m venv .venv
.venv/bin/pip install -r requirements-dev.lock
```

Run the checks by hand:

```bash
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/vulture app tests scripts --min-confidence 80 && .venv/bin/mypy
.venv/bin/pytest
```

Runtime dependencies go in `requirements.txt` and tools in
`requirements-dev.txt`. After changing a range, re-lock with
`.venv/bin/pip freeze > requirements-dev.lock`.
