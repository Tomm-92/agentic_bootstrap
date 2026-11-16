# ADK conventions

These apply to the agent package in `app/` and its tests in `tests/unittests/`. The
project-wide rules are in the root `AGENTS.md`. Ruff and
`tests/unittests/test_adk_conventions.py` check the mechanical ones; the rest need
judgement.

## Framework

- Verify every framework API against the installed source in
  `.venv/lib/python3.14/site-packages/google/adk/` before using it. Never guess a
  class, parameter or import path.
- Prefer framework built-ins over custom code that does the same job.

## Agents

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

## Tools

- Every function tool has a type hint on each parameter and its return value.
- Its docstring has an entry for each parameter (`ToolContext` excepted) and a
  `Returns:` section.
- Tools return a dict with a `status` key rather than raising. Catch errors from
  external services, the network or files, and return them as an `error` status.
