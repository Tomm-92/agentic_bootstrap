@AGENTS.md

<!-- Keep this file to what only Claude Code can act on. Everything any coding agent
can use belongs in AGENTS.md, and the ADK conventions in app/AGENTS.md. -->

# Claude Code

- Hooks in `.claude/settings.json` run the checks in AGENTS.md for you. After each
  edit, ruff fixes and formats the file and reports what it can't fix. A turn that
  edited files can't end while a check fails. When a hook blocks, fix the code.
- Start every change in plan mode. When the owner approves the plan, write it to
  `docs/execution-plans/plan/active/<ID>-<name>.md` from `docs/execution-plans/templates/plan.md`.
