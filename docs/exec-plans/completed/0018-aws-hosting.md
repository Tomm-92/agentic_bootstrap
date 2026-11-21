---
id: '0018'
rules: [GOV-002, GOV-004, GOV-006, SCOPE-001, SCOPE-002, DEP-001, COST-001]
scope_paths:
  - docs/aws_hosting_implementation.md
  - docs/exec-plans/**
  - README.md
  - proposals/0018/**
  - tests/governance/test_settings.py
---

# Plan 0018: AWS hosting instructions

Status: done. The owner approved it on 2026-11-21.

## Goal

Intent: [0018-aws-hosting](../intent/0018-aws-hosting.md)
Spec: [0018-aws-hosting](../spec/0018-aws-hosting.md)

The four instruction files take a project from an empty repo to a governed ADK agent
that runs only on a developer's machine. This plan adds a fifth, optional file,
`docs/aws_hosting_implementation.md`, which an agent runs in one session after file 4.
That run produces:

- a container image for the agent
- Terraform for a dev and a prod environment on ECS Fargate
- a deploy path where prod runs only the image digest that passed in dev
- proposals for every protected path it needs to change

The file also compares the AWS alternatives. This plan writes the file, lists it in
the README and proposes protecting it. It builds no infrastructure.

## Files that change

- `docs/aws_hosting_implementation.md` (new). It follows the structure of
  `docs/agent_governance_implementation.md`:
  - Before you start
  - How to run this file
  - Hosting inputs (the interview)
  - Phases H01 to H06, each with Build, Acceptance criteria and Ledger
  - Alternatives to ECS Fargate
  - After the run, Verified facts, Known gaps and Sources
- `README.md`:
  - "Getting started" lists five files, with a new row 5.
  - The protected-paths paragraph adds the new file.
  - The ADK deployment bullet points to file 5.
- `proposals/0018/` adds the new file alongside
  `docs/agent_governance_implementation.md` in each of these:
  - `AGENTS.md`
  - `.claude/settings.json` (the deny rule and `denyWrite`)
  - `.github/CODEOWNERS`
  - `.github/workflows/governance.yml`
  - `test_settings.diff`, a patch to `tests/governance/test_settings.py`. It's a
    patch, as in plan 0010, because a copy under `proposals/` is linted as
    non-test code and fails ruff.
- `docs/exec-plans/tech-debt-tracker.md`: a row for the plan-mode gate conflict.

## Order of work

- [x] Write this plan.
- [x] Re-check the ADK facts taken from adk.dev against the installed 2.14 source.
- [x] Write `docs/aws_hosting_implementation.md`.
- [x] Update `README.md` and `tech-debt-tracker.md`.
- [x] Write the proposals, and run the settings test against the proposed settings.
- [x] ruff, mypy, vulture, and the unit and governance tests pass.
- [x] Commit, with the intent and spec, on `feature/add-infra-pillar`.
- [x] Move this plan to `completed/`.

## Risks

- An ADK fact could go stale after an upgrade. Each fact is marked with its source,
  and Verified facts says to re-check them.
- The live test and the proposed settings could disagree. The test changes inside the
  proposal, so both are applied in one commit.
- The file could grow too long to run in one session. Its phases point to the
  spec's design instead of repeating it.

## Proof

- Every ADK name the new file cites was found in the installed 2.14 source, checked
  with grep. Every rule ID it cites is in `governance/rules.yaml`, except HOST-001
  and DEPLOY-001, which it proposes.
- Re-checked in the source, all held:
  - `ADK_FORCE_LOCAL_STORAGE` and `ADK_DISABLE_LOCAL_STORAGE`
  - asyncpg for PostgreSQL
  - the OTLP environment variables
- Corrected by the source: Python does have a `FileArtifactService`, so artifacts use
  `file://` on EFS.
- In a scratch copy of the repo, with `proposals/0018/` and the diff applied,
  `tests/governance/test_settings.py` passes all 44 tests.
- `git apply --check proposals/0018/test_settings.diff` passes.
- ruff, ruff format, vulture and mypy are clean, and `pytest` passes 291 tests, with
  1 deselected.

## Decisions

- **ECS Fargate and Terraform**, both chosen by the owner.
- **The new file is protected**, like files 3 and 4, because it gives an agent rules
  for a run.
- **The `hosting` profile block is left to the H01 run.** It's proposed then, not
  added here.
- **Line references come from the 2.14 source.** The new file names
  `user_id`'s three locations, and the route allowlist, from `cli/api_server.py`.
  The website alone missed the body and query-string cases.
- **This plan was approved in chat, not through Claude Code's plan file.** The edit
  gate refuses `~/.claude/plans/` while no plan is active, so the plan file couldn't
  be written. The gap is in the tech-debt tracker.

## Owner actions

1. Review `docs/aws_hosting_implementation.md`, especially H02's identity binding,
   the Alternatives table, and the AWS facts marked as not checked in this repo.
2. Review `proposals/0018/`, then apply it on this branch:

   ```bash
   git apply proposals/0018/test_settings.diff && rm proposals/0018/test_settings.diff
   cp -R proposals/0018/. . && rm -rf proposals/0018
   git add -A && git commit -m "Apply proposal 0018" \
     -m "Governance: $(git rev-parse HEAD:governance)" -m "Plan: 0018"
   ```

3. Push `feature/add-infra-pillar`, open a pull request and merge it.
4. Start a new Claude Code session, so the new deny rule and sandbox path load.
5. Decide on the tech-debt row about plan mode and the edit gate.
