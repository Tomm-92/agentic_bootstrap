# agentic_tools_v2

A Google ADK agent project. `app/` currently holds a placeholder agent, to be
replaced with the real one.

## Code quality

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
- mypy.ini: strict type checks on `app` and `tests`. Every `type: ignore` must
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
.venv/bin/vulture app tests --min-confidence 80 && .venv/bin/mypy
.venv/bin/pytest
```

Runtime dependencies go in `requirements.txt` and tools in
`requirements-dev.txt`. After changing a range, re-lock with
`.venv/bin/pip freeze > requirements-dev.lock`.
