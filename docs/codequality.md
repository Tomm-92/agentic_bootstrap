# Code quality implementation instructions

These instructions set up automatic code-quality controls for a project
developed with Claude Code including:

- A linter and formatter that fix each file as soon as Claude edits it.
- A gate that stops Claude from finishing a turn while lint, format,
  dead-code, type or unit-test checks fail.
- Lint rules aimed at concise code: no dead code, no roundabout logic, no
  blind exception handling, and size and complexity limits.
- Framework convention tests and banned deprecated APIs.
- On-demand review commands, run on small commits.

The priority throughout is **concise code that follows the framework's
conventions**. Instructions in `AGENTS.md`, which any coding agent reads,
state the rules. Deterministic checks enforce every rule they can. Reviews
handle the rules that need judgement.

Put this file at `docs/codequality.md` in the new repo.

## How to use this file

- **One Claude Code session.** Start it with: *"Implement
  docs/codequality.md."* Do the build steps in order.
- **Open the session at the repo root.** Claude Code loads
  `.claude/settings.json` only from the folder it was launched in. A session
  opened from a parent folder runs none of the hooks.
- **Ask, don't guess.** Ask the owner for anything this file marks
  `<like this>`: the source package, the language, the framework and any
  generated-output folder. Use the same folder for `output_root` in
  `docs/governance_implementation.md`.
- **Verify before use.** Check every tool flag against its installed version,
  and every hook behaviour against https://code.claude.com/docs. "Verified
  facts" lists what has already been checked.
- **Run it first.** Implement this file in a new repo straight after
  installing the framework, before other setup that adds hooks or deny
  rules. Every later file in the repo is then linted, type-checked and
  tested from its first edit.
- **Write `.claude/settings.json` last.** Once it exists, its deny rules stop
  you from editing the hooks. If the repo already denies edits to
  `.claude/settings.json` or `.claude/hooks/`, stop and ask the owner how to
  apply those files.

## Assumptions

Change these before you start if they don't hold:

- **Python 3.14** in `.venv/`, with **ruff** (lint, autofix and format),
  **vulture** (dead code), **mypy** (types) and **pytest**. For another
  language, use the equivalents in "Other languages" and keep the same
  structure.
- **Claude Code is the main coding agent, and others are supported.** Claude
  Code's hooks run the checks during a session. Other agents read
  `AGENTS.md` as instructions, so CI runs the same checks on every pull
  request.
- **The repo is on GitHub**, with Actions enabled. On another host, port the
  CI workflow to its CI system.
- **`jq` and `git` are installed**, and the repo has at least one commit.
  The hooks depend on both.
- **Dependencies are listed in `requirements.txt`.** If the project keeps
  them in `pyproject.toml` (with or without a lock file), see the
  `pyproject.toml` variant in build step 1.
- **Unit tests are free and fast.** They run at the end of every turn that
  changed files, so they must not call a paid model or a network service.

## Principles

1. **Concise code first.** Write the smallest change that does the job. Dead
   code, speculative helpers and needless guards count as defects.
2. **Deterministic checks over instructions.** Each `AGENTS.md` rule that a
   linter or test can check, a linter or test enforces. Instructions only
   nudge the model.
3. **Cheap checks run automatically, costly ones on demand.** Hooks cost no
   model usage, so they run on every edit and every turn. Real-model tests
   and multi-reviewer reviews run only when asked.
4. **Fix the code, not the check.** No `noqa`, ignores or weakened config,
   unless the rule is wrong for that line. When it is, a comment says why.
5. **Never loop forever.** A failing gate blocks once, then reports to the
   human.
6. **Reviews only look at small diffs.** Commit after each feature so reviews
   stay cheap and focused.
7. **Reviews cite evidence.** Each finding cites the rule it breaks, either a
   `AGENTS.md` line or installed framework source. Findings without
   evidence are dropped.

## Controls

| Control | When it runs | Type | Cost |
| --- | --- | --- | --- |
| `AGENTS.md` code style, checks and test rules | Every session | Instruction | Context only |
| `<agent_package>/AGENTS.md` framework conventions | When an agent first works in the package | Instruction | Context only |
| `lint_on_edit.sh`: autofix and format, then report what's left | After every Edit/Write of a source file | Hook (deterministic) | Free |
| `checks_on_stop.sh`: lint, format, dead code, types, unit tests | When Claude tries to finish a turn that changed files | Hook (deterministic) | Free |
| Lint config: concision, complexity, security, banned APIs | Inside both hooks | Deterministic | Free |
| Framework convention tests | Inside the Stop hook (unit tests) | Deterministic | Free |
| Unit tests refuse network connections | Inside the Stop hook (unit tests) | Deterministic | Free |
| Integration tests and evals against the real model | `pytest -m integration`, by hand | Deterministic | Spends credits |
| `/<framework>-review`: project conventions | By hand, after a commit | Model judgement | One reviewer |
| `/simplify`: duplication and complexity, with fixes | By hand, after a commit | Model judgement | Four reviewers |
| `/code-review low`: bugs | By hand, after a commit | Model judgement | Low |
| Suppression reason check: every `noqa` and `type: ignore` names its codes and says why | Inside the Stop hook | Deterministic | Free |
| CI: the Stop hook's checks, for any agent or person | Every pull request and push to the main branch | Deterministic | Free (Actions minutes) |
| Deny rules on hooks, settings, CI workflows, `ruff.toml`, `mypy.ini` and `pytest.ini` | Always | Deterministic | Free |

## Build

1. **Dependencies.** Give every runtime dependency in `requirements.txt` a
   version range that allows patch and minor updates but not the next major
   (for example `google-adk>=2.13,<3`), so an unplanned breaking release
   can't arrive. Create `requirements-dev.txt` with `-r requirements.txt` and
   version ranges for the tools:

   ```text
   -r requirements.txt
   mypy>=2.4,<3
   pytest>=9,<10
   pytest-asyncio>=1.4,<2   # only if the code is async
   ruff>=0.17,<0.18
   vulture>=2.16,<3
   ```

   Runtime dependencies go in `requirements.txt` and test or lint tools in
   `requirements-dev.txt`. Create `.venv` and install
   `requirements-dev.txt`. Check the versions are current, then lock what
   you installed with
   `.venv/bin/pip freeze > requirements-dev.lock`. Commit the lock file: CI
   installs from it, so CI and local runs use the same versions. Re-lock
   whenever a range changes.

   **`pyproject.toml` variant.** If the project keeps its dependencies in
   `pyproject.toml`, don't create `requirements-dev.txt`:
   - Put the runtime ranges in `[project] dependencies` and the tool ranges
     in `[project.optional-dependencies] dev`.
   - Add a build setup so `pip install -e '.[dev]'` works, and name the
     source package explicitly. Hatchling only finds a package named like
     the project, so it can't find `<source package>` on its own. Use
     hatchling rather than setuptools: setuptools writes a
     `<project>.egg-info/` folder into the repo root on every editable
     install.

     ```toml
     [build-system]
     requires = ["hatchling>=1.33,<2"]
     build-backend = "hatchling.build"

     [tool.hatch.build.targets.wheel]
     packages = ["<source package>"]
     ```

   - Install with `.venv/bin/pip install -e '.[dev]'`. Pin the result with
     `.venv/bin/pip freeze --exclude-editable > requirements-dev.lock`, next
     to any existing runtime lock file. A fresh setup is then
     `pip install -r requirements-dev.lock -e '.[dev]'`.

2. **`ruff.toml`.** Copy it from "Reference files". Set `target-version`,
   `extend-exclude` (generated output) and `per-file-ignores` for this
   project. `target-version` must be the lowest Python the project
   supports: if `pyproject.toml` has `requires-python = ">=3.11"`, use
   `"py311"` or raise `requires-python`, otherwise the `UP` autofixes can
   write syntax the oldest supported version can't run. Merge the
   framework's entries from "Framework add-ons" into the existing
   `per-file-ignores` and `banned-api` tables, not as new copies of those
   tables. Set `indent-width` and `[format] quote-style` to the project's
   existing style. Run `.venv/bin/ruff check .` and fix every finding in
   existing code, then run `.venv/bin/ruff format .` and review the diff
   before going further.

3. **`pytest.ini`.** Copy it from "Reference files". It skips integration
   tests unless `-m integration` is passed. Make sure at least one unit test
   exists: `pytest` exits with code 5 when it collects no tests, and the Stop
   hook would block every turn.

4. **`mypy.ini`.** Copy it from "Reference files". Once `tests/` exists
   (step 6), run `.venv/bin/mypy` and fix every error in existing code. Most errors in framework code are real:
   a value that can be `None`, or a hint that disagrees with the code. Check
   for the library's own hints before adding a `# type: ignore[code]  # <why>`.

5. **Dead code baseline.** Run
   `.venv/bin/vulture <source package> tests --min-confidence 80`. Delete
   what it finds. If a finding is a false positive, such as a framework
   callback found by name, ask the owner before adding a whitelist file.

6. **Unit tests and convention tests.** If the source package doesn't exist
   yet, create a minimal placeholder first, so the tests have something real
   to check. For ADK, that is `<agent_package>/__init__.py` with
   `from . import agent`, and `agent.py` with a `root_agent` that has a
   model, a description and one fully documented function tool. Tell the
   owner it's a stand-in to replace. Under `tests/unittests/`:
   - Replace any paid model or external service with a scripted fake, so
     the tests are free and repeatable. Add an autouse fixture that makes
     socket connections fail, so a missed fake fails the test instead of
     spending credits.
   - Turn each mechanically checkable convention from
     `<agent_package>/AGENTS.md` into a test. See "Framework add-ons" for the ADK set. The review skill then
     skips those conventions.
   - Put real-model tests under `tests/integration/`, marked
     `@pytest.mark.integration`.
   - Don't add `__init__.py` to `tests/` or its subfolders. Tests then
     import shared helpers with `from conftest import ...`, and ADK doesn't
     list `tests` as an agent.

7. **`.gitignore`.** Add `.venv/`, `__pycache__/`, `.ruff_cache/`,
   `.mypy_cache/`, `.pytest_cache/`, `.env` and
   `.claude/.checks_fingerprint`. Any unignored file the checks or the
   install create changes the Stop hook's fingerprint (see "Verified facts").

8. **Instruction files.** Put each rule where every coding agent can read
   it, scoped to where it applies. Copy the sections from "Instruction
   files" in "Reference files":
   - `AGENTS.md`: the "Code style", "Checks" and "Tests" sections, and a
     project layout tree. Create the file if it doesn't exist.
   - `<agent_package>/AGENTS.md`: the "Framework" section, then the
     framework conventions (models, tools and so on). Every convention must
     be checkable by reading the code.
   - `CLAUDE.md`: `@AGENTS.md` and the Claude Code lines.
   - `<agent_package>/CLAUDE.md`: only `@AGENTS.md`. Claude Code resolves
     the import against the file's own folder, and loads the file when it
     first reads or edits a file in the package.

9. **`.claude/hooks/lint_on_edit.sh` and `.claude/hooks/checks_on_stop.sh`.**
   Copy them from "Reference scripts". Fill in the variables at the top of
   `checks_on_stop.sh`, then `chmod +x` both.

10. **`.claude/skills/<framework>-review/SKILL.md`.** Copy the template from
   "Reference files" and fill in the framework, the source location and the
   list of conventions already enforced by tests.

11. **`.github/workflows/checks.yml`.** Copy it from "Reference files".
    Change the install line if the project uses the `pyproject.toml`
    variant, and the branch name if it isn't `main`. Check the action
    versions are current.

12. **`README.md`.** Add a "Code quality" section that covers:
    - what the hooks do;
    - what the lint rules and tests cover;
    - the review commands table;
    - the per-feature workflow;
    - that CI runs the same checks on every pull request;
    - setup, and how to run the checks by hand.

    Use the structure from "README section" below.

13. **`.claude/settings.json`, last.** Merge in the fragment from
    "Reference files". If the file already exists, keep its existing hooks
    and deny rules.

### Acceptance criteria

- [ ] `.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
      `.venv/bin/vulture <source package> tests --min-confidence 80`,
      `.venv/bin/mypy` and `.venv/bin/pytest` all pass.
- [ ] With a function that returns a `float` where its hint says `int`, the
      Stop hook exits 2 with the mypy error. With
      `# type: ignore[return-value]` it exits 2 asking for a reason; with
      `# type: ignore[return-value]  # <why>` it passes. A tool hinted
      `-> dict` fails mypy with `type-arg`.
- [ ] With a source file that ruff would reformat, the Stop hook exits 2
      naming the file, and `lint_on_edit.sh` on that file reformats it.
- [ ] Piping `{"tool_input":{"file_path":"$PWD/<file>.py"}}` into
      `lint_on_edit.sh` (with `CLAUDE_PROJECT_DIR=$PWD`) exits 0 for a clean
      file. For a file containing `import os` and a call to an undefined
      name, it removes the import and exits 2 with the remaining finding.
- [ ] Piping `{"stop_hook_active":false}` into `checks_on_stop.sh` exits 0
      on a clean tree. With a failing test it exits 2 with the failure on
      stderr. A second run with `{"stop_hook_active":true}` prints a
      `systemMessage` and exits 0.
- [ ] Each convention test fails when its convention is broken. Break each
      one temporarily to check, then revert.
- [ ] With a source file containing `import os  # noqa: F401`, the Stop hook
      exits 2 and names the line. With `# noqa: F401 - <why>` it passes.
- [ ] In a fresh clone (no `.claude/.checks_fingerprint`), the workflow's
      last command, `echo '{}' | CLAUDE_PROJECT_DIR=$PWD
      .claude/hooks/checks_on_stop.sh`, exits 0. With a failing test it
      exits 2.
- [ ] With an `app/.ruff.toml` that sets `select = []`, `lint_on_edit.sh`
      still removes an unused import. Delete the file afterwards.

### Owner actions

1. Review and commit everything.
2. Push, and check the `checks` workflow passes. Then make it a required
   status check in the main branch's protection rules (or a ruleset), so
   no agent or person can merge a pull request that fails it.
3. Start a **new** session at the repo root and confirm:
   - Editing a Python file with an unused import gets autofixed.
   - A turn that breaks a test is blocked once, then reported to you.
   - Editing `.claude/hooks/lint_on_edit.sh`, `ruff.toml` or `pytest.ini`,
     or creating `.claude/settings.local.json`, is refused.

## Per-feature workflow

Put this in the README:

1. Build the feature. The hooks keep each turn clean.
2. Commit. The reviews only look at changes since the last commit, so small
   commits keep them cheap.
3. Run `/<framework>-review` and `/simplify`, then `/code-review low`.
4. Commit the fixes.

Run integration tests with `.venv/bin/pytest -m integration` before merging
anything that changes model-facing behaviour.

## Reference files

### `ruff.toml`

```toml
line-length = 100
target-version = "py314"
indent-width = <indent width>
extend-exclude = ["<generated output folder>"]   # or remove

[format]
quote-style = "<single or double>"
exclude = ["*.md"]   # ruff formats Python blocks in Markdown; docs keep their own samples

[lint]
select = [
    "E", "F", "W", "I", "B", "UP",
    "SIM", "RET", "PIE", "C4",   # needlessly roundabout code
    "ERA",                       # commented-out code
    "ARG",                       # unused arguments
    "BLE", "TRY",                # blind or over-wide exception handling
    "C90", "PLR",                # complexity and size limits
    "TID251",                    # banned APIs, listed below
    "PGH004", "RUF100",          # noqa must name codes, and stale ones go
    "ANN",                       # type hints on every function
    "T20",                       # print(); AGENTS.md bans prints
    "S",                         # security (Bandit)
]
ignore = [
    "TRY003",    # a custom exception class per message is more code, not less
]

[lint.mccabe]
max-complexity = 8

[lint.pylint]
max-args = 5
max-statements = 30

[lint.per-file-ignores]
"tests/**" = ["PLR2004", "ANN", "S101"]   # literal expected values and asserts are how tests check; annotating tests and fixtures adds noise
# "<package>/prompt.py" = ["E501"]   # long model-facing prose, if any

# Deprecated or discouraged framework APIs, each with the replacement.
[lint.flake8-tidy-imports.banned-api]
# "<module.Symbol>".msg = "<why, and what to use instead>"
```

### `pytest.ini`

```ini
[pytest]
testpaths = tests
pythonpath = .
markers =
    integration: calls a real model and spends credits; run with -m integration
addopts = -m "not integration"
asyncio_default_fixture_loop_scope = function
```

Drop the last line if `pytest-asyncio` isn't used.

### `mypy.ini`

```ini
[mypy]
files = <source package>, tests
strict = True
# ruff's ANN requires hints outside tests; tests stay unhinted, so don't require them here.
disallow_untyped_defs = False
disallow_incomplete_defs = False
disallow_untyped_calls = False
# Tests are exempt from ruff's ANN, so check inside functions without hints too.
check_untyped_defs = True
# Like ruff's PGH004 and RUF100 for noqa: ignores name their codes, and stale ones fail.
enable_error_code = ignore-without-code
warn_unused_ignores = True
```

### Instruction files

Sections for `AGENTS.md`:

```markdown
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
- Match the existing style: <indent width>, <quote style>. `ruff format`
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
  They spend credits, so ask before running them.
```

Section for `<agent_package>/AGENTS.md`, before the framework conventions:

```markdown
## Framework

- Verify every framework API against the installed source in
  `<.venv/lib/python3.14/site-packages/<framework>/>` before using it. Never
  guess a class, parameter or import path.
- Prefer framework built-ins over custom code that does the same job.
```

Claude Code lines for `CLAUDE.md`, after `@AGENTS.md`:

```markdown
# Claude Code

- Hooks in `.claude/settings.json` run the checks in AGENTS.md for you. After each
  edit, ruff fixes and formats the file and reports what it can't fix. A turn that
  edited files can't end while a check fails. When a hook blocks, fix the code.
- `<agent_package>/CLAUDE.md` loads the framework conventions when you first read or
  edit a file under `<agent_package>/`.
- `/<framework>-review` checks changes against `<agent_package>/AGENTS.md` and the
  installed framework source.
```

### `.claude/settings.json` fragment

```json
{
  "permissions": {
    "deny": [
      "Edit(/.claude/settings.json)",
      "Edit(/.claude/settings.local.json)",
      "Edit(/.claude/hooks/**)",
      "Edit(/ruff.toml)",
      "Edit(/pytest.ini)",
      "Edit(/mypy.ini)",
      "Edit(/.github/workflows/**)",
      "Read(**/.env)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/lint_on_edit.sh",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/checks_on_stop.sh",
            "timeout": 300,
            "statusMessage": "Running lint, format, dead-code, type and tests"
          }
        ]
      }
    ]
  }
}
```

The deny rules stop Claude from switching off its own checks, or weakening
the lint, type and test config or CI workflow they run with. The hooks pass
`--config ruff.toml`, so a new nested `ruff.toml`, `.ruff.toml` or
`[tool.ruff]` table can't override it either. The local file needs its own
rule: `.claude/settings.local.json` overrides `.claude/settings.json` and
can set `"disableAllHooks": true`. Change hooks and settings yourself, by
hand or through a pull request.

### Review skill template: `.claude/skills/<framework>-review/SKILL.md`

```markdown
---
name: <framework>-review
description: Review changed code and project structure against this project's <framework> conventions and the installed <framework> source. Use when the user asks for a <framework> review or runs /<framework>-review.
argument-hint: "[file or folder to review; default: uncommitted changes]"
---

Review the changes for alignment with <framework> conventions. Report
findings; do not edit files unless the user asks.

Keep it cheap: work in this session, start no subagents, and read only the
changed files plus the framework source a finding needs.

## 1. Scope

If `$ARGUMENTS` names files or folders, review those. Otherwise review
`git diff HEAD` plus untracked files from `git ls-files --others
--exclude-standard`, leaving out <generated output and test fixtures>.
If nothing is in scope, say so and stop.

## 2. Checklist

The checklist is `<agent_package>/AGENTS.md`. Read it first.

Skip what is already enforced automatically:
- ruff bans <the deprecated imports in ruff.toml>.
- <each convention test file, and what it checks>.

Focus on what needs judgement:
- <conventions that no test can check, for example: does each component get
  only the permissions or tools it needs; are hard rules enforced in code
  rather than only in prompts; does new code re-implement a built-in; are
  typed models used instead of untyped dicts>.
- Project structure: compare the repo against the layout tree in the root
  `AGENTS.md`, using `ls` and `git ls-files`, not by reading every file. Is
  each new file in the right place? Is the layout tree still accurate?

## 3. Evidence

Every finding must cite the rule it breaks: either an `AGENTS.md` or
`<agent_package>/AGENTS.md` line, or a
location in the installed <framework> source under
<path to installed source> that you have read. Check any claim about
framework behaviour against that source, not memory. Do not browse the web.
Drop any finding you cannot back with evidence.

## 4. Report

List the findings, most important first. Give each one:
- `file:line`
- the rule it breaks, with its evidence
- the fix

If a finding shows that a rule is missing from `<agent_package>/AGENTS.md`,
suggest the wording but do not add it. If the code is aligned, say so in one
line.
```

### README section

```markdown
## Code quality

Code quality is enforced by automatic checks. The priority is concise code
that follows <framework> conventions. AGENTS.md and <agent_package>/AGENTS.md
hold the rules, and the checks below enforce them.

**Automatic checks.** These run through the hooks in .claude/settings.json,
so they cost no extra usage.
- <lint-on-edit behaviour>
- <checks-on-stop behaviour, including the one-retry limit>

What the checks cover:
- ruff.toml: <rule groups and banned APIs>
- tests/unittests/: <free, fake model, convention tests>
- tests/integration/: <real-model tests; spend credits; `pytest -m integration`>

**Review commands.** <table: command, what it does, source>

**CI.** <the checks workflow runs the Stop hook's checks on every pull
request, for any agent or person; merging needs it to pass>

**Workflow for each feature:** <the four steps>

**Setup:** <install command, and the three by-hand check commands>
```

### `.github/workflows/checks.yml`

```yaml
name: checks
on:
  pull_request:
  push:
    branches: [main]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.14'
      # pyproject.toml variant: pip install -r requirements-dev.lock -e '.[dev]'
      - run: python -m venv .venv && .venv/bin/pip install -r requirements-dev.lock
      # Runs the Stop hook itself, so CI and Claude Code check the same things.
      - run: echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh
```

This holds every agent to the same checks, whatever its instructions say.
A fresh checkout has no fingerprint file and `stop_hook_active` is false, so
the hook runs every check and exits 2 on the first failure, which fails the
job. GitHub's Ubuntu runners include `jq`, `git` and `shasum`.

## Reference scripts

### `.claude/hooks/lint_on_edit.sh`

```bash
#!/bin/bash
# PostToolUse: autofix and format an edited project Python file and report what ruff can't fix.
f=$(jq -r '.tool_input.file_path // empty')
[[ "$f" == "$CLAUDE_PROJECT_DIR"/*.py && -f "$f" ]] || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
# --config stops nested ruff configs overriding ruff.toml; --force-exclude applies
# its excludes to explicit paths.
out=$(.venv/bin/ruff check --config ruff.toml --fix --force-exclude --output-format concise "$f" 2>&1)
failed=$?
# Format after fixing, since fixes can leave code unformatted.
.venv/bin/ruff format --config ruff.toml --force-exclude --quiet "$f"
if (( failed )); then
  echo "ruff found issues in $f; fix them:" >&2
  echo "$out" >&2
  exit 2
fi
```

### `.claude/hooks/checks_on_stop.sh`

```bash
#!/bin/bash
# Stop: if the working tree changed since the last check, block finishing while
# lint, format, dead-code, type or unit-test checks fail. After one blocked
# attempt, tell the user instead, and don't re-check until something changes again.
active=$(jq -r '.stop_hook_active // false')
cd "$CLAUDE_PROJECT_DIR" || exit 0
src=(<source package> tests)          # vulture targets
paths=(. ':!<generated output folder>')  # or paths=(.) if nothing is generated
saved=.claude/.checks_fingerprint
now=$({
  git diff HEAD -- "${paths[@]}"
  git ls-files -z --others --exclude-standard -- "${paths[@]}" | xargs -0 cat
} | shasum)
[[ "$now" == "$(cat "$saved" 2>/dev/null)" ]] && exit 0
fail() {
  if [[ "$active" == true ]]; then
    echo "$now" >"$saved"
    jq -n --arg m "Checks still failing ($1)" '{systemMessage: $m}'
    exit 0
  fi
  printf '%s:\n%s\n' "$1" "$2" >&2
  exit 2
}
out=$(.venv/bin/ruff check --config ruff.toml --output-format concise . 2>&1) || fail ruff "$out"
out=$(.venv/bin/ruff format --check --config ruff.toml . 2>&1) || fail 'ruff format (run .venv/bin/ruff format .)' "$out"
out=$(git grep --untracked -niE -e '#[[:space:]]*type:[[:space:]]*ignore(\[[^]]*\])?[[:space:]]*$' -e '#[[:space:]]*noqa(:[[:space:]]*[A-Z]+[0-9]+([[:space:]]*,?[[:space:]]*[A-Z]+[0-9]+)*)?[[:space:]]*$' -- "${src[@]}") &&
  fail 'noqa and type: ignore need a reason after their codes: # noqa: E501 - <why>, # type: ignore[code]  # <why>' "$out"
out=$(.venv/bin/vulture $(ls -d "${src[@]}" 2>/dev/null) --min-confidence 80 2>&1) || fail vulture "$out"
out=$(.venv/bin/mypy 2>&1) || fail mypy "$out"
out=$(.venv/bin/pytest -q -x 2>&1) || fail pytest "$(tail -30 <<<"$out")"
echo "$now" >"$saved"
```

How it behaves:
- **Fingerprint.** It hashes the diff against `HEAD` plus all untracked
  files. If nothing changed since the last passing (or reported) run, it
  exits at once, so turns without edits cost nothing.
- **First failure.** It exits 2 with the output on stderr. Claude sees the
  output and keeps working to fix it.
- **Second failure** (`stop_hook_active` is true). It saves the fingerprint
  and sends a `systemMessage` to the user instead of blocking again. It
  doesn't re-check until the tree changes.
- **Suppression reasons.** After ruff, it fails if any `noqa` or
  `type: ignore` comment in the source has nothing after its codes. Ruff's
  `PGH004` already rejects a bare `# noqa`, and `RUF100` removes stale ones;
  `mypy.ini` does the same for `type: ignore`. mypy needs the reason as a
  second comment: `# type: ignore[code]  # <why>`. The check lives in the
  hook, not a unit test, because the hook is on the deny list and tests
  aren't.
- **Order.** Cheapest first: ruff lint and format, then vulture, then mypy,
  then pytest with `-x` to stop at the first failure. The pytest output is
  trimmed to the last 30 lines.

## Framework add-ons

### Google ADK 2.x (reference implementation)

**Additions to `ruff.toml`.** ADK's agent loader needs `from . import
agent` in the agent package's `__init__.py`. ruff reports it as an unused
import (F401) and won't autofix it, so without this ignore the Stop hook
fails on every turn. Merge each entry below into the table of the same name
that `ruff.toml` already has. Don't paste the headers again: TOML rejects a
repeated table header, and ruff then won't load the file.

```toml
[lint.per-file-ignores]
"<agent_package>/__init__.py" = ["F401"]   # ADK loads the agent through this import

[lint.flake8-tidy-imports.banned-api]
"google.adk.agents.SequentialAgent".msg = "Deprecated in ADK 2.x; use a Workflow graph."
"google.adk.agents.ParallelAgent".msg = "Deprecated in ADK 2.x; use a Workflow graph."
"google.adk.agents.LoopAgent".msg = "Deprecated in ADK 2.x; use a Workflow graph."
"google.adk.agents.sequential_agent".msg = "Deprecated in ADK 2.x; use a Workflow graph."
"google.adk.agents.parallel_agent".msg = "Deprecated in ADK 2.x; use a Workflow graph."
"google.adk.agents.loop_agent".msg = "Deprecated in ADK 2.x; use a Workflow graph."
"google.adk.tools.AgentTool".msg = "Add the agent to sub_agents with mode='single_turn' or 'task'."
"google.adk.tools.agent_tool".msg = "Add the agent to sub_agents with mode='single_turn' or 'task'."
# google.adk.tools re-exports it lazily, so mypy can't resolve it there.
"google.adk.tools.ToolContext".msg = "Import ToolContext from google.adk.tools.tool_context."
```

**Fake model (`tests/unittests/conftest.py`).** Sub-agents inherit the
root's model, so one fake answers for the whole tree. The autouse fixture
fails any test that opens a connection, so a missed fake can't spend credits:

```python
import socket

import pytest
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from <agent_package> import agent


def call(name: str, **args) -> LlmResponse:
  """A model turn that calls one tool."""
  part = types.Part(function_call=types.FunctionCall(name=name, args=args))
  return LlmResponse(content=types.Content(role='model', parts=[part]))


def say(text: str) -> LlmResponse:
  """A model turn that replies with text."""
  return LlmResponse(content=types.Content(role='model', parts=[types.Part(text=text)]))


class FakeLlm(BaseLlm):
  """Returns scripted responses in order and records every request."""

  model: str = 'fake'
  script: list[LlmResponse] = []
  requests: list[LlmRequest] = []

  async def generate_content_async(self, llm_request, stream=False):
    del stream  # Required by BaseLlm's signature.
    self.requests.append(llm_request)
    if not self.script:
      raise AssertionError('The agent called the model more times than scripted.')
    yield self.script.pop(0)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
  """Unit tests are free: a real model or network call fails instead of spending credits."""

  def refuse(_sock, address, *_):
    raise AssertionError(f'Unit tests must not open network connections; tried {address}.')

  monkeypatch.setattr(socket.socket, 'connect', refuse)
  monkeypatch.setattr(socket.socket, 'connect_ex', refuse)


@pytest.fixture
def fake_llm(monkeypatch):
  """Replaces the root agent's model, and checks the test used its whole script."""
  llm = FakeLlm()
  monkeypatch.setattr(agent.root_agent, 'model', llm)
  yield llm
  assert not llm.script, f'The agent stopped before using: {llm.script}'
```

Drive it with `InMemoryRunner`, one runner and one session per test. Tests
import the helpers with `from conftest import call, say`, which works
because `tests/unittests/` has no `__init__.py`:

```python
@pytest.mark.asyncio
async def test_weather(fake_llm):
  fake_llm.script = [call('get_weather', city='Paris'), say('Sunny in Paris.')]
  runner = InMemoryRunner(agent=agent.root_agent)
  session = await runner.session_service.create_session(app_name=runner.app_name, user_id='u')
  msg = types.Content(role='user', parts=[types.Part(text='Weather in Paris?')])
  events = [e async for e in runner.run_async(user_id='u', session_id=session.id, new_message=msg)]
  reply = events[-1].content
  assert reply and reply.parts
  assert reply.parts[0].text == 'Sunny in Paris.'
```

pytest-asyncio runs in strict mode by default, so every async test needs
`@pytest.mark.asyncio`. An event's `content` and `parts` can be `None`, so
assert them before indexing, or mypy fails. To read a tool's result, use
`event.get_function_responses()`.

**Convention tests (`tests/unittests/test_adk_conventions.py`):**

```python
"""The conventions in <agent_package>/AGENTS.md that can be checked without a model."""

import inspect
import typing
from pathlib import Path

from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.tools.tool_context import ToolContext

from <agent_package> import agent

PROJECT = Path(__file__).parent.parent.parent


def _all_agents(root=agent.root_agent):
  yield root
  for sub_agent in root.sub_agents:
    yield from _all_agents(sub_agent)


def test_agent_loads():
  AgentLoader(str(PROJECT)).load_agent('<agent_package>')


def test_agent_folders_are_laid_out_for_adk_web():
  # ADK lists every top-level folder with an agent.py, a root_agent.yaml or
  # an __init__.py, so tests/ must not be a package.
  names = AgentLoader(str(PROJECT)).list_agents()
  assert names == ['<agent_package>']
  for name in names:
    assert name.isidentifier(), name
    assert 'from . import agent' in (PROJECT / name / '__init__.py').read_text()
  assert not list((PROJECT / 'tests').rglob('__init__.py'))


def test_only_the_root_sets_a_model():
  # Non-LLM agents have no model field.
  models = [a.name for a in _all_agents() if getattr(a, 'model', None)]
  assert models == [agent.root_agent.name]


def test_every_agent_has_a_description():
  assert all(a.description for a in _all_agents())


def test_tool_schemas_are_complete():
  tools = {t for a in _all_agents() for t in a.tools if inspect.isfunction(t)}
  for tool in tools:
    # eval_str resolves string annotations from `from __future__ import annotations`.
    sig = inspect.signature(tool, eval_str=True)
    params = [p for p in sig.parameters.values() if p.annotation is not ToolContext]
    doc = tool.__doc__ or ''
    assert sig.return_annotation is not inspect.Signature.empty, tool.__name__
    assert all(p.annotation is not inspect.Parameter.empty for p in params), tool.__name__
    assert 'Returns:' in doc, tool.__name__
    assert all(f'{p.name}:' in doc for p in params), tool.__name__
    # Tools report failure in a `status` key rather than raising.
    ret = sig.return_annotation
    assert typing.get_origin(ret) is dict or 'status' in typing.get_type_hints(ret), tool.__name__
```

**Review skill judgement items for ADK:** routing descriptions that say
how each sub-agent differs from its peers; delegated agents'
`input_schema` carrying everything they need; least tools per agent; tools
catching external, network and file errors as `error` statuses instead of
raising; hard rules enforced by
callbacks, not just instructions; `{identifier}` placeholders matching
state keys that are always set; built-ins used instead of custom code.

### Other languages

Keep the same three-stage structure (autofix on edit, full checks on stop,
reviews on demand) and swap the tools. Verify each tool's flags before use.

| Stage | Python | TypeScript | Go | Rust |
| --- | --- | --- | --- | --- |
| Autofix on edit | `ruff check --fix` | `eslint --fix` | `golangci-lint run --fix` | `cargo clippy --fix --allow-dirty` |
| Format on edit | `ruff format` | `prettier --write` | `gofmt -w` | `cargo fmt` |
| Type check | `mypy` | `tsc --noEmit` | compiler (`go vet` for extras) | compiler |
| Dead code | `vulture` | `knip` | `golangci-lint` (`unused`) or `deadcode` | compiler `dead_code` warnings as errors |
| Banned APIs | ruff `TID251` | `no-restricted-imports` | `depguard` or `forbidigo` | clippy `disallowed_methods` and `disallowed_types` |
| Complexity limits | ruff `C90`, `PLR` | `complexity`, `max-params`, `max-statements` | `gocyclo`, `funlen` | clippy `cognitive_complexity`, `too_many_arguments` |
| Unit tests | `pytest -q -x` | `vitest run --bail 1` | `go test ./...` | `cargo test` |

Change the file-extension test in `lint_on_edit.sh` to match, and keep the
hook to one file so it stays fast.

## Verified facts

These were checked on Python 3.12. The project now uses 3.14, so re-check any you
rely on.

These were first checked in `google-adk-dev`, then re-checked in
`agentic_dev_models` on 2026-11-03. Tool facts were tested with ruff 0.17.3,
pytest 9.2.0, ADK 2.13.0 and git. Claude Code facts were checked against
https://code.claude.com/docs (the hooks and settings pages).

- **PostToolUse exit 2:** stderr goes to Claude. The edit has already
  happened, so Claude fixes it in its next step.
- **Stop exit 2:** blocks Claude from finishing and gives it stderr.
  `stop_hook_active` is true when Claude is already continuing because of a
  Stop hook. Checking it is what prevents an endless loop. Claude Code also
  caps a Stop hook at 8 continuations in a row, but the hook shouldn't rely
  on that.
- **`systemMessage`** in a hook's JSON output is shown to the user, not
  Claude. Some events discard it, but Stop and PostToolUse don't.
- **Claude never sees stderr from a hook that exits 0.** It goes only to the
  debug log.
- **Claude Code reads `.claude/settings.json` from the session's launch
  folder** (its primary working directory), so open the session at the repo
  root. Reference scripts as `"$CLAUDE_PROJECT_DIR"/...` so they work from
  any working directory. Started in a subfolder, Claude Code still reads
  `.claude/settings.local.json` from the repo root.
- **Settings files created mid-session take effect at once.** Claude Code
  watches its settings files, including a `.claude/` folder created during
  the session. The hooks therefore start running in the session that writes
  `.claude/settings.json`, which is another reason to write it last.
- **`ruff --force-exclude`** is needed to apply `extend-exclude` to a file
  passed explicitly on the command line.
- **`pytest` exits 5 when it collects no tests**, which the Stop hook treats
  as a failure.
- **The fingerprint includes every untracked file that isn't gitignored.**
  The hook computes the fingerprint before running the checks. So if
  `__pycache__/` isn't ignored, the `.pyc` files the checks write change the
  next turn's fingerprint, and the checks run one extra time after every
  change. `.pytest_cache/` and `.ruff_cache/` write their own `.gitignore`,
  so they don't cause this, but list them anyway.
- **`git diff HEAD` fails in a repo with no commits** (exit 128). Make an
  initial commit before you enable the hooks.
- **`.claude/settings.local.json` overrides `.claude/settings.json`** and
  can add hooks or set `disableAllHooks`, so it needs its own deny rule.
- **ruff reports ADK's `from . import agent` as F401** and doesn't autofix
  it (the fix is unsafe), so the agent package's `__init__.py` needs a
  per-file ignore. Checked with ruff 0.17.3 and ADK 2.13.0.
- **Ruff picks the closest config file** to each linted file, so a nested
  `ruff.toml`, `.ruff.toml` or `pyproject.toml` with `[tool.ruff]` replaces
  the root one for its folder. `--config ruff.toml` uses that file for every
  file. Ruff ignores text after the codes in `# noqa: F401 - <why>`.
  Checked with ruff 0.17.3.
- **`ruff format` and the lint rules don't conflict** with this `select`
  list, `indent-width = 2` and `quote-style = "single"`: ruff prints no
  conflict warning. Ruff has no separate continuation indent, so call
  arguments get the same 2-space indent as blocks. Checked with ruff 0.17.3.
- **`ruff format` also formats Python blocks in Markdown files**, and skips
  blocks that don't parse, such as samples with `<placeholders>`. Without
  `exclude = ["*.md"]` under `[format]`, one unformatted sample in a doc fails
  the Stop hook and CI, and `ruff format .` rewrites the doc. `ruff check` does
  not lint Markdown. Checked with ruff 0.17.4.
- **`event.content` and `content.parts` are optional in ADK's types**, so
  `events[-1].content.parts[0].text` fails mypy with `union-attr` and `index`
  under `check_untyped_defs`. Checked with mypy 2.4.1 and ADK 2.14.0.
- **mypy was chosen over pyright, ty and Pyrefly** after a trial on this
  repo on 2026-11-04 (mypy 2.4.1, pyright 1.1.414, ty 0.0.97, Pyrefly
  1.4.0). mypy, pyright and ty each caught a misspelt `Agent` parameter, an
  attribute on a value that may be `None`, and a wrong return type; Pyrefly's
  default preset missed two of these. mypy is pure Python (pyright needs
  Node.js), and ty is not yet at 1.0. mypy takes about 3.5 s cold and 0.2 s
  with its cache.
- **`strict = True` catches what the base config misses.** On this repo
  it found a tool returning a bare `dict` (`type-arg`) and a test importing
  `ToolContext` from `google.adk.tools`, which only re-exports it lazily
  (`attr-defined`); import it from `google.adk.tools.tool_context`. Its
  untyped-def flags are switched off because ruff's `ANN` already requires
  hints outside `tests/`. Checked with mypy 2.4.1 on 2026-11-04.
- **Ruff's `S` rules** found nothing in `app/` and only `S101` (`assert`)
  in tests, so they cost one per-file ignore. Checked with ruff 0.17.3.
- **mypy skips the bodies of functions without hints** unless
  `check_untyped_defs` is set. Without it, mypy reported no errors in tests
  that had real `Optional` bugs.
- **mypy reads `# type: ignore[code] - why` as a malformed ignore**, so the
  reason must be a separate comment: `# type: ignore[code]  # why`. With
  `enable_error_code = ignore-without-code` it rejects a bare
  `# type: ignore`, and `warn_unused_ignores` rejects one that's no longer
  needed. Checked with mypy 2.4.1.
- **vulture honours `# noqa: V103`-style comments**, so the `noqa` reason
  check covers dead-code suppressions too. Checked with vulture 2.16.
- **ADK's `AgentLoader.list_agents()`** also lists top-level folders that
  only have an `__init__.py`. Folders with neither an `__init__.py` nor an
  `agent.py`, such as `docs/`, are not listed.
- **`/simplify` and `/code-review`** are built into Claude Code. They review
  changes since the last commit unless given a path. `/code-review` takes an
  effort level; `low` gives fewer, higher-confidence findings.

## Known gaps

Record these in the tech-debt tracker, if the project has one:

| Gap | Possible fix |
| --- | --- |
| A `noqa` with a reason, a `pytest.mark.skip` or a deleted test still passes the checks. | A review step, or CI that reports new suppressions and a falling test count. |
| Deny rules don't stop a script that writes files itself. | A sandbox, or CI re-running the checks. |
| Other coding agents get no feedback until CI runs, and their pull requests can edit the hooks, `ruff.toml` or the CI workflow. | A `CODEOWNERS` file covering those paths, with code-owner review required on the main branch. |
| Integration tests only run by hand. | A scheduled or pre-merge CI job, within a credit budget. |
| Reviews are on demand and can be skipped. | Make them a required step before merging, or run them in CI. |
