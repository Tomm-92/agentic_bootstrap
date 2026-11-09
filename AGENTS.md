# Instructions for coding agents

This file is the entry point for any coding agent. It points to rules and defines
none of its own.

## Before changing anything

- Read `governance/rules.yaml`, `governance/profile.yaml` and the single active plan
  in `docs/exec-plans/active/`.
- Name the plan and the rule IDs you are working under.

## While working

- Work only within the active plan, inside its `scope_paths` (SCOPE-001, SCOPE-002).
  With no active plan, or several, ask.
- On a conflict with governance or the plan, stop and ask.
- Keep each session to one plan. Start a new session for the next plan, or when the
  governance hash changes (GOV-006).
- Record assumptions, decisions and risks in the plan. Add deferred gaps to
  `docs/exec-plans/tech-debt-tracker.md`.
- Never read, print or commit `.env` files (SEC-001).

## Protected paths

Never write to these, and never do so indirectly through a script or command (GOV-002):

- `governance/`, including the profile
- `docs/governance_implementation.md`
- `docs/agent_governance_implementation.md`
- `.claude/settings.json`, `.claude/settings.local.json` and `.claude/hooks/`
- `.github/` and `.githooks/`
- `AGENTS.md` and `CLAUDE.md`

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
