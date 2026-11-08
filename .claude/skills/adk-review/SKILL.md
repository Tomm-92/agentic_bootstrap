---
name: adk-review
description: Review changed code and project structure against this project's Google ADK conventions and the installed ADK source. Use when the user asks for an ADK review or runs /adk-review.
argument-hint: "[file or folder to review; default: uncommitted changes]"
---

Review the changes for alignment with ADK conventions. Report findings; do not
edit files unless the user asks.

Keep it cheap: work in this session, start no subagents, and read only the
changed files plus the framework source a finding needs.

## 1. Scope

If `$ARGUMENTS` names files or folders, review those. Otherwise review
`git diff HEAD` plus untracked files from `git ls-files --others
--exclude-standard`, leaving out `output/`.
If nothing is in scope, say so and stop.

## 2. Checklist

The checklist is the "ADK conventions" section of CLAUDE.md. Read it first.

Skip what is already enforced automatically:
- ruff bans `SequentialAgent`, `ParallelAgent`, `LoopAgent` and `AgentTool`,
  and their modules.
- `tests/unittests/test_adk_conventions.py` checks that the agent loads, that
  the folders are laid out for `adk web` (`app` is the only agent, and its
  `__init__.py` has `from . import agent`), that only the root sets a model,
  that every agent has a description, and that every function tool has complete
  hints and a docstring covering its parameters and return value.
- mypy checks the type hints, including bare `dict` returns.

Focus on what needs judgement:
- Routing descriptions say how each sub-agent differs from its peers.
- A delegated agent's `input_schema` carries everything it needs.
- Each agent has the fewest tools it needs.
- Tools return `status` dicts instead of raising.
- Hard rules are enforced by callbacks, not just instructions.
- `{identifier}` placeholders match state keys that are always set.
- Built-ins are used instead of custom code that does the same job.
- Project structure: compare the repo against CLAUDE.md's layout tree, using
  `ls` and `git ls-files`, not by reading every file. Is each new file in the
  right place? Is the layout tree still accurate?

## 3. Evidence

Every finding must cite the rule it breaks: either a CLAUDE.md line, or a
location in the installed ADK source under
`.venv/lib/python3.14/site-packages/google/adk/` that you have read. Check any
claim about framework behaviour against that source, not memory. Do not browse
the web. Drop any finding you cannot back with evidence.

## 4. Report

List the findings, most important first. Give each one:
- `file:line`
- the rule it breaks, with its evidence
- the fix

If a finding shows that a rule is missing from CLAUDE.md, suggest the wording
but do not add it. If the code is aligned, say so in one line.
