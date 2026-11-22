---
id: '0008'
rules: [SCOPE-001, SCOPE-002, GOV-002]
scope_paths:
  - README.md
  - docs/exec-plans/**
---

# Plan 0008: rewrite the README around the bootstrap's purpose

## Goal

Lead the README with why this bootstrap repo exists: consistent governance,
transparency, observability and code quality for every agentic project, so outcomes
are reliable and production ready. Explain why Google ADK was chosen. Keep the existing
operational reference below that. Documentation only, no code changes.

## Checklist

- [x] Purpose section: the problem, and the four pillars with their mechanisms.
- [x] Why Google ADK, limited to features this repo uses.
- [x] How a new project uses the bootstrap (the four setup files).
- [x] Keep the governance and code quality reference sections.

## Decisions

- The title uses `agentic_bootstrap`, the repo name the owner uses. `profile.yaml`
  still says `agentic_tools_v2`. That is a protected path, so it is left as is.
- ADK claims cover only what the repo uses: `App` and plugins, callbacks,
  `AnthropicLlm`, `DatabaseSessionService`, OpenTelemetry spans, `Workflow`
  graphs, `sub_agents` modes, the eval format and the `adk web`, `adk eval` and
  `adk deploy` commands. All of them were checked against the installed ADK source
  once the owner reinstalled `.venv`.

## Risks

- `.venv` had been deleted, and the edit hooks need `.venv/bin/python`. This session
  created an empty `.venv`. `pip install` failed in the sandbox with an SSL
  certificate error, so the owner ran it from their own terminal.

## Owner actions

- Review the README wording, and decide whether `profile.yaml`'s `project` should
  become `agentic_bootstrap`.
