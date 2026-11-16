# Handover: after applying proposal 0010

State on 2026-11-16: branch `agent-instructions-split` holds plans 0010 (`846922c`) and
0011 (`0972a68`). Nothing is pushed. The proposal in `proposals/0010/` is reviewed and
ready to apply. The plan records are in `docs/exec-plans/completed/`.

Steps 1 to 3 are yours, in your own terminal. Steps 4 and 5 need a new Claude Code
session. Delete this file in the commit for step 5.

## 1. Apply and check (you, before committing)

```sh
git apply proposals/0010/test_settings.diff && rm proposals/0010/test_settings.diff && cp -R proposals/0010/. . && rm -rf proposals/0010
```

Then check:

- `git status` shows changes to `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`,
  `.github/CODEOWNERS`, `.github/workflows/governance.yml`, `governance/rules.yaml`,
  `ruff.toml`, `docs/governance-activation.md`, `docs/governance_implementation.md`,
  `docs/agent_governance_implementation.md` and `tests/governance/test_settings.py`.
  It also shows new `app/AGENTS.md` and `app/CLAUDE.md` files, and `proposals/0010/`
  deleted.
- `.venv/bin/ruff check --config ruff.toml . && .venv/bin/mypy && .venv/bin/pytest -q`
  passes, with **289 passed, 1 deselected**. That's 278 plus 11 new settings cases,
  because `test_settings.py` grows from 31 cases to 42.

If something is wrong, nothing is committed yet: `git restore . && git clean -fd app`
puts the branch back.

## 2. Commit (you)

Commit everything on `agent-instructions-split` with these trailers:

```text
Governance: eb9b3e99684e8e00cefc93f7934a56cb71ece2ec
Plan: 0010
```

The `Governance:` trailer is the **parent's** hash, even though this commit changes
`governance/`. `commit-msg` checks against `HEAD`, which is still the old governance.
`Plan: 0010` makes the CI scope check pass, because every applied file had a copy
in `proposals/0010/`.

## 3. Push and open the pull request (you)

```sh
git push -u origin agent-instructions-split
```

Then open the PR against `main`. On the PR, the `governance` workflow should show a
**Plan scope** step that passes. That's the evidence for activating the SCOPE-002
CI control in step 5. Don't merge yet.

## 4. Verify in a new Claude Code session

Start a new session at the repo root. Any open session is blocked, because the
governance hash changed (GOV-006). Then:

- **Instructions load.** `/context all` lists `CLAUDE.md` and `AGENTS.md` under
  Memory files. After Claude reads a file under `app/`, it also lists `app/CLAUDE.md`
  and `app/AGENTS.md`.
- **The `ask` rule prompts for paid runs only.** Ask Claude to run each of these, and
  **decline** the prompts, so nothing is spent:
  - `.venv/bin/pytest -q -m integration`: prompts.
  - `.venv/bin/python -m scripts.local_session --real hi`: prompts.
  - `.venv/bin/python -m scripts.local_session hi`: runs without a prompt, with the
    scripted reply "Demo is a placeholder project."
- **The new protected paths hold.** An Edit of `app/AGENTS.md` is denied, and
  `touch ruff.toml` through Bash fails under the sandbox.

Note which checks passed and the date. Step 5 needs both.

## 5. Activate the two planned controls (new session, then you)

Two controls are in `rules.yaml` as `planned`, waiting on the checks above:

| Rule | Control | Evidence |
| --- | --- | --- |
| COST-001 | Claude Code permission ask on paid-model commands (S04) | Step 4's prompt checks |
| SCOPE-002 | governance workflow scope check (S05) | Step 3's Plan scope step |

In the new session, ask Claude to draft plan `0012`, with
`scope_paths: [docs/exec-plans/**, docs/governance-activation.md, proposals/0012/**]`,
that:

- Rewrites each control's owner check in `docs/governance-activation.md` to
  `Confirmed by the owner, <date>`, adding what you saw.
- Writes `proposals/0012/governance/rules.yaml`, with only those two statuses moved
  from `planned` to `active`.
- Runs `.venv/bin/python scripts/check_activation.py proposals/0012/governance/rules.yaml`,
  which must print "The proposal passes."
- Deletes this handover file.

Then you apply `proposals/0012/` and commit with `Plan: 0012`. That changes the
governance hash again, so start another new session afterwards.

## 6. Merge, then protect `main` (you)

Review the PR, including the protected-path list in the workflow summary, and merge.
Then, when the plan allows, turn on branch protection for `main`. It's the one control
that stops pushes and direct commits for every coding agent, and it switches
CODEOWNERS on.

## For reference

- `local_session` is now fake by default. `--fake` no longer exists, and gives an
  argparse error. Use `--real` for the paid model.
- The README describes the state after this proposal is applied.
- Open gaps are in `docs/exec-plans/tech-debt-tracker.md`, including the three rows
  plan 0010 added.
