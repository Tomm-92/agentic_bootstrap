@AGENTS.md

# Project instructions

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
  external services, the network or files. In a tool, return them as an
  `error` status dict. Never catch bare `Exception`.
- Type-hint every function's parameters and return value. Ruff's `ANN` rules
  enforce this outside `tests/`, and mypy checks the hints are right.
- Comment only the non-obvious why. No comments or docstrings that restate
  the code. Docstrings a model reads, such as tool docstrings, are the
  exception.
- No logging, prints (ruff `T20` bans `print`), commented-out code or
  backward-compatibility shims unless asked.
- Match the existing style: 2-space indent, single quotes. `ruff format`
  enforces it.
- Hooks in `.claude/settings.json` enforce part of this. After each edit,
  `ruff check --fix` and `ruff format` run on the file, and ruff reports what
  it cannot fix. Before Claude finishes a turn in which it edited files, ruff
  (lint and format), vulture (dead code), mypy (types) and the unit tests must
  pass. Fix the code rather than adding `noqa`, `type: ignore` or ignores. If
  a rule is wrong for one line, name the code and say why after it:
  `# noqa: E501 - <why>` or `# type: ignore[arg-type]  # <why>`. The Stop
  hook rejects either with no reason.

## Working rules

- Verify every framework API against the installed source in
  `.venv/lib/python3.14/site-packages/google/adk/` before using it. Never
  guess a class, parameter or import path.
- Prefer framework built-ins over custom code that does the same job.
- Unit tests never call a real model or network service: use the scripted
  fake in `tests/unittests/conftest.py`. Real-model tests go in
  `tests/integration/`, marked `@pytest.mark.integration`.

## ADK conventions

### Layout

```text
app/                    the agent package
  __init__.py           contains `from . import agent`, which ADK's loader needs
  agent.py              defines `root_agent`
output/                 generated output, excluded from lint, format and checks
tests/                  not a package: no `__init__.py` here or in subfolders
  unittests/            free tests using the fake model; conftest.py holds the fake
  integration/          real-model tests; spend credits
  governance/           rule catalogue and profile tests; also free
docs/                   project setup instructions, plans and the activation ledger
governance/             rules, profile, thresholds, allowlists and tool tiers
scripts/                local session, evidence report and activation check; not a package
ops/                    observability stack
proposals/              owner-applied changes to protected paths
```

### Agents

- The package exposes its root agent as `root_agent` in `agent.py`, and
  `__init__.py` contains `from . import agent`.
- Only the root agent sets `model`. Sub-agents inherit it.
- Every agent has a `description`. A sub-agent's description says how it differs
  from its peers, because the model routes on it.
- Each agent gets only the tools it needs.
- Use a `Workflow` graph instead of `SequentialAgent`, `ParallelAgent` or
  `LoopAgent`.
- Add an agent to `sub_agents` with `mode='single_turn'` or `mode='task'` instead
  of wrapping it in `AgentTool`.
- A delegated agent's `input_schema` carries everything it needs.
- Enforce hard rules in callbacks, not only in instructions.
- `{identifier}` placeholders in instructions match state keys that are always
  set.

### Tools

- Every function tool has a type hint on each parameter and its return value.
- Its docstring has an entry for each parameter (`ToolContext` excepted) and a
  `Returns:` section.
- Tools return a dict with a `status` key rather than raising.

### Imports

- Import `ToolContext` from `google.adk.tools.tool_context`, because
  `google.adk.tools` only re-exports it lazily and mypy rejects that.
