---
id: '0010'
rules: [GOV-002, GOV-003, GOV-004, GOV-006, SCOPE-001, SCOPE-002, COST-001]
scope_paths:
  - docs/exec-plans/**
  - proposals/0010/**
  - docs/codequality.md
  - README.md
  - scripts/check_scope.py
  - scripts/local_session.py
  - scripts/arm_governance.py
  - tests/unittests/**
  - tests/governance/test_check_scope.py
  - tests/governance/test_settings.py
  - .claude/skills/adk-review/**
---

# Plan 0010: split agent instructions by audience and scope, and enforce the hard rules

## Goal

Coding agents other than Claude Code stay in scope, because this is a bootstrap and
the next project may use a different agent. Three changes follow from that:

1. **Portable over Claude-only.** Everything any agent can use goes in `AGENTS.md`.
   `CLAUDE.md` becomes `@AGENTS.md` plus the few lines only Claude Code can act on.
2. **Project-wide over product-scoped.** The root files hold only what applies to the
   whole repo. ADK conventions move to `app/AGENTS.md`, which other agents read when
   they work in `app/`, and `app/CLAUDE.md` contains `@AGENTS.md` so Claude Code loads
   it on the same occasions. One copy, scoped, read by any agent.
3. **Non-negotiables are enforced, not only stated.** Close the gaps found in the
   review, and prefer agent-neutral layers (tests, git hooks, CI) over Claude hooks,
   because only Claude Code runs the latter.

## Where each piece of the current instructions goes

| Content today | Goes to |
| --- | --- |
| `AGENTS.md`: governance process, protected paths, git | Root `AGENTS.md`, unchanged apart from the protected-paths list |
| `CLAUDE.md` Code style, except the ADK tool sentence | Root `AGENTS.md` |
| `CLAUDE.md` "In a tool, return them as an `error` status dict" | `app/AGENTS.md` |
| `CLAUDE.md` Hooks paragraph | Root `CLAUDE.md`, cut to one line: fix the code, never add a bare `noqa` or `type: ignore` |
| Working rule: verify APIs against the installed ADK source | `app/AGENTS.md` |
| Working rule: unit tests use the fake model | Root `AGENTS.md`, Tests section |
| Layout tree | Root `AGENTS.md` (it describes the whole repo, not ADK) |
| ADK Agents and Tools sections | `app/AGENTS.md` |
| ADK Imports section (`ToolContext`) | Removed. A ruff banned-API entry enforces it and its message says what to do |

## Enforcement added

| Gap | Fix | Where |
| --- | --- | --- |
| `ruff.toml`, `pytest.ini`, `mypy.ini` are denied to `Edit` but writable from Bash | Add them to the sandbox `denyWrite`, the protected-paths list, CODEOWNERS and the governance workflow's protected-path report | Proposal |
| `app/AGENTS.md` and `app/CLAUDE.md` would be agent-writable | Protect them like the root files | Proposal |
| Unit tests could reach the network | Autouse fixture in `tests/unittests/conftest.py` that makes `socket.socket.connect` raise | Direct |
| Lazy `ToolContext` import | ruff `banned-api` entry for `google.adk.tools.ToolContext` | Proposal (`ruff.toml`) |
| Tools may not return a status dict | `test_tool_schemas_are_complete` asserts each tool returns a `dict` or a `TypedDict` with a `status` key | Direct |
| `tests/` must not be a package | Convention test: no `__init__.py` under `tests/` | Direct |
| SCOPE-002 has no agent-neutral control | `scripts/check_scope.py` plus a governance workflow step (details below) | Script direct, workflow by proposal |
| COST-001 paid-model runs rely on the agent asking | `ask` permission rules for `pytest -m integration` | Proposal (`settings.json`) |

### CI scope check

For each non-merge commit in the PR range:

- Read the `Plan:` trailer and load that plan's `scope_paths` from the commit's own
  tree (`git show <commit>:docs/exec-plans/...`).
- Each changed file passes if it is under `docs/exec-plans/`, matches a scope glob, or
  `proposals/<plan ID>/<file>` matches one. The last case covers the owner's commits
  that apply a proposal, such as `ee741a0`.
- Report the failures, and use `fnmatch` the same way `governance_gate.sh` does, so the
  session and CI agree on what is in scope.
- "Matches a proposal" means `proposals/<plan ID>/<file>` exists in the commit's parent
  or in the commit itself, not that it matches a glob. Otherwise a plan scoping
  `proposals/<id>/**` would let every path pass. Both trees are needed: `ee741a0`
  deleted its proposal in the commit that applied it, and `2dc89d9` added the proposal
  and applied it in one commit.

The trailer check already rejects a missing or unknown plan, so this script doesn't
check that again.

## Checklist

- [x] Confirm against the Claude Code docs that a nested `app/CLAUDE.md` loads when
      Claude reads files under `app/`, and that `@AGENTS.md` inside it resolves
      relative to `app/`. If either is false, stop and ask: the fallback is
      `.claude/rules/adk.md` with `@app/AGENTS.md` and `paths:` front matter.
      Both hold (code.claude.com/docs/en/memory, read 2026-11-16): a subdirectory
      `CLAUDE.md` loads "once Claude reads, writes, or edits another file in that
      subdirectory", and "relative paths resolve relative to the file containing the
      import".
- [x] Baseline: run ruff, vulture, mypy and the unit tests, and record the count.
      All clean; 269 passed, 1 deselected (integration), in 13.3 s.
- [x] `tests/unittests/conftest.py`: socket fixture. Prove it trips by running one
      throwaway test that opens a connection, then delete that test. A raw socket and
      an `anthropic` client call were both refused; the suite still passes 269.
- [x] `tests/unittests/test_adk_conventions.py`: status-dict assertion, the
      no-`__init__.py` test, and change the module docstring to point at
      `app/AGENTS.md`. The no-`__init__.py` check joined
      `test_agent_folders_are_laid_out_for_adk_web`, which already explains why.
      The status check accepts `dict[...]` or a TypedDict with `status`, and rejects
      a TypedDict without it and a `str`.
- [x] `scripts/check_scope.py` and `tests/governance/test_check_scope.py`. Cover: in
      scope, out of scope, plan files exempt, proposal applied by the owner, merge
      commit skipped, and several globs. 9 tests.
- [x] Run the scope check over `main`'s history since plan 0001, and record any
      failures in Result. Existing failures are information, not something to fix here.
- [x] Proposals in `proposals/0010/`, each at its real relative path:
  - [x] `AGENTS.md`: the portable content above, plus `app/AGENTS.md`, `app/CLAUDE.md`,
        `ruff.toml`, `pytest.ini` and `mypy.ini` in the protected-paths list.
  - [x] `CLAUDE.md`: `@AGENTS.md` and the Claude-only lines.
  - [x] `app/AGENTS.md` and `app/CLAUDE.md`.
  - [x] `.claude/settings.json`: the new denies and `ask` rules for every command
        that can call a paid model: `Bash(*pytest* -m integration*)`,
        `Bash(*local_session*--real*)`, `Bash(*adk run*)` and `Bash(*adk web*)`. The docs
        (code.claude.com/docs/en/permissions) confirm `ask` rules take mid-pattern
        wildcards, apply to every part of a compound command, and prompt even in auto
        mode.
  - [x] `tests/governance/test_settings.py`: expect the new protected paths. It goes
        through the proposal so it lands in the same commit as the settings, or the
        Stop hook fails in between. Shipped as `proposals/0010/test_settings.diff`:
        ruff's `tests/**` ignores don't reach a `.py` under `proposals/`, so a copy
        there fails the checks. `git apply --check` passes, and the patched file is
        ruff-clean. Against the proposed settings it passes 42; against the current
        ones, 11 fail, one per new deny, sandbox entry and `ask` rule.
  - [x] `ruff.toml`: the `ToolContext` ban. A probe showed it flags
        `from google.adk.tools import ToolContext` and not the `tool_context` import.
  - [x] `.github/CODEOWNERS` and `.github/workflows/governance.yml`: the new protected
        paths and the scope-check step. actionlint is clean.
  - [x] `governance/rules.yaml`: add the CI control to SCOPE-002, and the two new
        COST-001 controls. The rule tests pass 71 against it.
  - [x] `docs/governance-activation.md`: a ledger row for each new control.
        `check_activation.problems` finds the proposed rules and ledger consistent.
  - [x] `docs/governance_implementation.md` and
        `docs/agent_governance_implementation.md`: build steps and phase A00 write the
        new structure, so the next bootstrap doesn't recreate the old one. Also switch
        `local_session` to `--real`: the Stage 6 spec (about lines 749-751), the paid
        run (779) and its `arm_governance.py` copy (2054) gain `--real`, and the
        `--fake` examples (920, 987, 1191) drop the flag. Auto mode
        refused the agent's copy of both, as in plan 0007, so the owner copied them
        into `proposals/0010/docs/` on 2026-11-16 and the agent edited the copies.
        `governance_implementation.md`: the existing-files note, Stage 3's
        `AGENTS.md`, `CLAUDE.md` and CODEOWNERS steps, Stage 4's sandbox list,
        settings-test description and ledger, Stage 5's scope-check step, rules and
        ledger, Stage 6's `--real` flag and paid run, the `--fake` examples, Stage 11's
        deny and `ask` rules and protected-path list, the embedded catalogue, the
        `arm_governance.py` reference copy, and the tech-debt rows.
        `agent_governance_implementation.md`: A00's proposal list and the model
        convention now name `<profile.product_agent.path>/AGENTS.md`. The embedded
        catalogue has the same controls as `proposals/0010/governance/rules.yaml`.
- [x] `docs/codequality.md`: the `CLAUDE.md` code style section and the `/adk-review`
      template point at `AGENTS.md` and `app/AGENTS.md`. Also: build step 8 writes all
      four instruction files, the fake-model reference gains the network fixture, the
      convention-test reference gains the status and `tests/` checks, and the ADK ruff
      additions gain the `ToolContext` ban.
- [x] `.claude/skills/adk-review/SKILL.md`: the checklist comes from `app/AGENTS.md`,
      and the layout tree from root `AGENTS.md`. The edit went through directly.
- [x] `README.md`: an "Agent support" section saying what Claude Code gets (session
      enforcement) and what other agents get (instructions, git hooks, CI). Update the
      protected-paths list. Added as "Coding agents", with a table by control.
- [x] `docs/exec-plans/tech-debt-tracker.md`: narrow the "agents other than Claude
      Code" row to what is still not enforced for them: the governance hash per
      session, and blocking pushes and main commits before branch protection exists.
      Also added a row for the scope check's proposal and self-widening gaps.
- [x] Run ruff, vulture, mypy and the unit tests.
- [x] Commit with the trailers, and move this plan to `completed/`.

## Result

- Before: 269 passed, 1 deselected. After: 278 passed, 1 deselected (the 9 scope-check
  tests). Ruff, ruff format, vulture and mypy are clean.
- The proposal is tested where it can be before applying: the settings test patch
  applies and passes 42 against the proposed settings, the rule tests pass 71 against
  the proposed catalogue, rules and ledger are consistent, actionlint is clean, and
  the `ToolContext` ban was probed.
- The scope check over `main` (48 commits) reports one change:
  `7d58e45` (plan 0008) edited `governance/profile.yaml` directly, with no proposal,
  under a plan scoped to `README.md`. It was an owner rename of the project, so it's
  allowed, but it is exactly what the check is meant to surface. Not fixed here.

## Decisions

- Keep both `AGENTS.md` and `CLAUDE.md`. Merging them would change GOV-004 and
  GOV-006's control text, the activation ledger, CODEOWNERS, settings, tests and the
  workflow, for little gain, and would drop the portable entry point.
- Scope ADK rules with a nested `AGENTS.md`, not `.claude/rules/`, because
  `.claude/rules/` is Claude-only.
- Keep root `CLAUDE.md` with `@AGENTS.md`, although Claude Code v2.1.277+ reads
  `AGENTS.md` on its own. That native read is skipped whenever a `CLAUDE.md` or
  `CLAUDE.local.md` exists, before v2.1.277, in the first session after an upgrade, and
  when the built-in plugin is off. Governance has to load in every session, so the
  import is the reliable route. `InstructionsLoaded` hooks also fire only for imported
  files, which keeps instruction loading observable for EVID-001.
- Use `app/CLAUDE.md` with `@AGENTS.md` instead of relying on the native read of
  `app/AGENTS.md`. With a root `CLAUDE.md` present, the native read doesn't happen by
  default. Even when it does, it triggers only on the Read tool, while a nested
  `CLAUDE.md` also loads on Write and Edit.
- Don't add per-tool files (`.cursor/rules`, `.github/copilot-instructions.md`) until
  a specific agent is adopted.
- Write every protected or newly protected file as a proposal, including the two new
  `app/` files, so the agent never writes its own instructions unreviewed.
- An instruction stays when it guides how code gets written, even if a check also
  enforces it, because stating it saves a failed turn. It goes when the check's failure
  message already says everything needed (the `ToolContext` import).
- The socket fixture lives in `tests/unittests/` only. `tests/governance/` runs `git`
  in subprocesses and doesn't need it, and `tests/integration/` must reach the model.
- Block sockets with a monkeypatch rather than `pytest-socket`, so DEP-001 doesn't
  apply.
- `local_session` is fake by default and takes `--real` for the paid model, so its
  `ask` rule matches only the run that spends credits, and a forgotten flag costs
  nothing. Chosen by the owner on 2026-11-16 over prompting for every run, because
  an `ask` rule can't exclude `--fake`. `arm_governance.py paid` now passes `--real`,
  since it is the one caller that means to spend.
- New controls that only config proves (the `ask` rule), or that need a CI run that
  hasn't happened yet (the scope check), enter `rules.yaml` as `planned`, with a ledger
  row whose owner check is open. The owner activates them through the existing
  process. The network fixture is fully proven by tests, so it enters as `active`.

## Risks

- **Lazy loading.** Claude Code loads `app/CLAUDE.md` only once it reads, writes or
  edits a file under `app/`, so the ADK rules arrive with the first touch rather than
  before planning. The convention tests and `/adk-review` still catch the mechanical
  ones.
- **Uneven support for nested `AGENTS.md`.** Other tools may not all read it. The
  README section says so.
- **The socket fixture** may break ADK, the Anthropic client or asyncio internals if
  any of them connect at import or setup. The baseline run shows this straight away.
- **Proposal ordering.** `settings.json` and `test_settings.py` must land in one
  commit. Applying `rules.yaml` changes the governance hash, so GOV-006 blocks open
  sessions until they start fresh.
- **The `ask` rules** match command text. Leading wildcards cover `.venv/bin/` and
  `python -m` forms, but `-m=integration`, aliases and wrapper scripts get past them.
  It's an improvement, not a guarantee.
- **`--fake` is gone.** Anyone who still types `local_session --fake` gets an
  argparse error rather than a paid run. The completed plans and old ledger rows
  mention `--fake` as the flag used at the time, and are left as historical
  evidence.
- **The CI scope check is advisory** like the rest of `governance.yml` until required
  checks are available.
- **Proposals can launder scope.** An agent that writes `proposals/<id>/X` and `X`
  passes the check for any `X`. For protected paths, the workflow's protected-path
  report still lists `X`. For other paths, the reviewer sees a proposal that applied
  itself. Like the session gate, the check also trusts a plan's `scope_paths` as of
  the commit, so a plan that widens its own scope passes. Owner review covers both.

## Owner actions

- Review this plan before work starts. While it sits in `active/`, edits inside its
  `scope_paths` are allowed.
- Choose the branch. The current branch is `readme-getting-started`. A new branch from
  `main` keeps this PR separate.
- Copy the two setup docs into the proposal folder so the agent can edit them:
  `cp docs/governance_implementation.md docs/agent_governance_implementation.md proposals/0010/docs/`.
- After the work: review `proposals/0010/`, then apply it in one commit. The settings
  test is a patch, so it goes first and isn't copied:
  `git apply proposals/0010/test_settings.diff && rm proposals/0010/test_settings.diff && cp -R proposals/0010/. . && rm -rf proposals/0010`.
- After applying: in a new session, confirm `.venv/bin/pytest -q -m integration`
  prompts. Then, on the pull request, confirm the "Plan scope" step ran. Then activate
  both `planned` controls through the ledger.
- Start a new session after applying it, because the governance hash changes.
- Turn on branch protection for `main` when the plan allows. It makes CODEOWNERS and
  the no-direct-commits rule hold for every agent.
