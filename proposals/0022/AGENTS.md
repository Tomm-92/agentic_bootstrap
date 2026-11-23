# Instructions for coding agents

This file is the entry point for any coding agent. It says how to work under the
rules in `governance/` and how code here is written. It defines no governance rules
of its own. Before working in `app/`, read `app/AGENTS.md`, which holds the agent
framework's conventions.

## Before changing anything

- Read `governance/rules.yaml`, `governance/profile.yaml`, the single active plan
  in `docs/execution-plans/plan/active/`, and the intent and spec it links to.
- Name the plan and the rule IDs you are working under.

## While working

- Work only within the active plan, inside its `scope_paths` (SCOPE-001, SCOPE-002).
  With no active plan, or several, ask.
- On a conflict with governance or the plan, stop and ask.
- Keep each session to one plan. Start a new session for the next plan, or when the
  governance hash changes (GOV-006).
- Record assumptions, decisions and risks in the plan. Add deferred gaps to
  `docs/bootstrapper_tech_debt_tracker.md`, or to `docs/agent_tech_debt_tracker.md` when
  the gap wouldn't exist with a different agent.
- Never read, print or commit `.env` files (SEC-001).
- Never set `Status: accepted` on an intent or spec. Only the owner accepts them.

## Things agents get wrong

When an agent makes the same mistake twice, propose a line for it here.

- You can't see permission prompts. A command the user approved and one that ran
  without a prompt return the same result. Ask the user whether a prompt appeared;
  never report it yourself.

## Protected paths

Never write to these, and never do so indirectly through a script or command (GOV-002):

- `governance/`, including the profile
- `docs/bootstrap-implementation/project_governance.md`
- `docs/bootstrap-implementation/agent_governance.md`
- `.claude/settings.json`, `.claude/settings.local.json` and `.claude/hooks/`
- `.github/` and `.githooks/`
- `AGENTS.md`, `CLAUDE.md`, `app/AGENTS.md` and `app/CLAUDE.md`
- `ruff.toml`, `pytest.ini` and `mypy.ini`

To change one, write the new version to `proposals/<plan ID>/` at the same relative
path. The owner reviews and applies it.

## Git

- Never push, and never commit on `main` (GOV-002).
- Never use `--no-verify`, and never change `core.hooksPath` (GOV-004).
- Every commit ends with these trailers (GOV-004):

  ```text
  Governance: <git rev-parse HEAD:governance>
  Plan: <plan ID>
  ```

## Code style

Concise code is the priority. Write the smallest change that does the job.

- Add no helpers, parameters, options or abstractions the task does not need
  now. Three similar lines beat a premature helper.
- Before adding code, check whether a framework built-in or an existing local
  function already does it.
- Delete what a change makes unused: functions, imports, constants, tests and
  prompt text.
- Do not guard against what cannot happen. Skip `try/except`, `None` checks
  and re-validation for inputs that the framework, Pydantic or the type hints
  already guarantee. Catch only specific exceptions, and only around calls to
  external services, the network or files. Never catch bare `Exception`.
- Type-hint every function's parameters and return value. Ruff's `ANN` rules
  enforce this outside `tests/`, and mypy checks the hints are right.
- Comment only the non-obvious why. No comments or docstrings that restate
  the code. Docstrings a model reads, such as tool docstrings, are the
  exception.
- No logging, prints (ruff `T20` bans `print`), commented-out code or
  backward-compatibility shims unless asked.
- Match the existing style: 2-space indent, single quotes. `ruff format`
  enforces it.

## Checks

Before you finish, and in CI on every pull request, these must pass: ruff (lint and
format), vulture (dead code), mypy (types) and the unit tests. Fix the code rather
than adding `noqa`, `type: ignore` or ignores. If a rule is wrong for one line, name
the code and say why after it: `# noqa: E501 - <why>` or
`# type: ignore[arg-type]  # <why>`. A bare one fails the checks.

## Tests

- Unit tests never call a real model or network service. Use the scripted fake in
  `tests/unittests/conftest.py`, which also refuses network connections.
- Real-model tests go in `tests/integration/`, marked `@pytest.mark.integration`.
  They spend credits, so ask before running them (COST-001).
- For a bug fix, first commit a test that reproduces the bug, marked
  `@pytest.mark.xfail(strict=True, reason='<the bug>')`. Then fix the code. The fix
  commit removes that marker, and changes nothing else in the test.
- When a test fails, assume the code is wrong. Change a test only when the active
  plan says the behaviour it checks is changing, or when you can say why the test
  itself is wrong.
- Change a test in its own commit, and give the reason in the commit message. If the
  test is a bug fix's reproducing test, stop and ask the owner instead.
- Before reporting a task done, run the checks, or ask the `verifier` subagent to,
  and paste the output into the report.

## Layout

```text
app/                    the agent package; its conventions are in app/AGENTS.md
  __init__.py           contains `from . import agent`, which ADK's loader needs
  agent.py              defines `root_agent`
output/                 generated output, excluded from lint, format and checks
tests/                  not a package: no `__init__.py` here or in subfolders
  unittests/            free tests using the fake model; conftest.py holds the fake
  integration/          real-model tests; spend credits
  governance/           rule catalogue and profile tests; also free
docs/
  bootstrap-implementation/  the instructions that built this project
  execution-plans/      intents, specs, plans, their templates and the handover
  records/              evidence review, quality score, security sign-off and activation ledger
  diagrams/             governance controls diagram
  bootstrapper_tech_debt_tracker.md  deferred gaps in the bootstrap
  agent_tech_debt_tracker.md         deferred gaps in the agent it builds
governance/             rules, profile, thresholds, allowlists and tool tiers
scripts/                local session, evidence report, activation and scope checks; not a package
observability/          local telemetry stack
proposals/              owner-applied changes to protected paths
```
