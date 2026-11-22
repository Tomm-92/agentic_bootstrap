---
id: '0020'
rules: [GOV-002, GOV-004, GOV-006, SCOPE-001, SCOPE-002, QUAL-001, SEC-001]
scope_paths:
  - docs/**
  - observability/**
  - ops/**
  - proposals/**
  - README.md
  - ARCHITECTURE.md
  - scripts/ai_review.py
  - scripts/arm_governance.py
  - scripts/check_activation.py
  - scripts/evidence_report.py
  - tests/governance/test_ai_review.py
  - tests/governance/test_observability.py
  - tests/governance/test_quality_score.py
---

# Plan 0020: docs reorganisation

Status: in progress. The owner approved it in plan mode on 2026-11-22.

<!-- Written to docs/exec-plans/active/<ID>-<name>.md when the owner approves it in plan
mode. Moved to docs/exec-plans/completed/ when done. -->

## Goal

Intent: none (the owner has already done the moves; this plan updates everything that points at the old paths).

The owner reorganised the project structure in the working tree:

| Old | New |
| --- | --- |
| `docs/exec-plans/active/`, `completed/` | `docs/execution-plans/plan/active/`, `plan/completed/` |
| `docs/exec-plans/{intent,spec,templates}/`, `handover.md` | `docs/execution-plans/...` |
| `docs/exec-plans/tech-debt-tracker.md` | `docs/tech_debt_tracker.md` |
| `docs/governance_implementation.md` | `docs/bootstrap-implementation/project_governance.md` |
| `docs/agent_governance_implementation.md` | `docs/bootstrap-implementation/agent_governance.md` |
| `docs/initial_install.md`, `docs/codequality.md` | `docs/bootstrap-implementation/` |
| `docs/governance-activation.md` | `docs/records/governance_activation.md` |
| `docs/EVIDENCE_REVIEW.md`, `QUALITY_SCORE.md`, `SECURITY.md` | `docs/records/evidence_review.md`, `quality_score.md`, `security.md` |
| `docs/images/governance-controls.svg` | `docs/diagrams/governance_controls.svg` |
| `ops/observability/`, `docker-compose.yaml` | `observability/`, `compose.yaml` |
| `proposals/0003`, `0004`, `0005`, `0019` | deleted (all applied already) |

Nothing else knows yet. The edit gate and the commit-msg hook look for plans in
`docs/exec-plans/`, so every edit is blocked and no commit can name a plan. Scripts,
tests, protected files and docs name the old paths. This plan points all of them at
the new layout.

Naming convention (owner, 2026-11-22): hyphens in folder names, underscores in
document names.

## Files that change

The scope is wide (`docs/**`, `observability/**`, `ops/**`, `proposals/**`), so the
CI scope check accepts the owner's move commit. Within that scope I write only the files
listed under "Changed directly" and `proposals/0020/`. The two protected bootstrap
docs change only through the proposal.

**Changed directly (this session):**
- `scripts/evidence_report.py`, `check_activation.py`, `arm_governance.py` (`LEDGER`
  only), `ai_review.py`: new paths for the ledger, plans, intents, specs, tracker,
  evidence review and `observability/`.
- `tests/governance/test_quality_score.py`: read `docs/records/quality_score.md`, and
  resolve its links from `docs/records/`. The proposals check uses the repo root.
- `tests/governance/test_observability.py`: `observability/compose.yaml`.
- `tests/governance/test_ai_review.py`: fixture paths under `docs/execution-plans/`.
- `docs/records/quality_score.md`: links become `../../tests/...`,
  `../../requirements-dev.lock` and `governance_activation.md`.
- `docs/records/*`, `docs/tech_debt_tracker.md`, `docs/execution-plans/handover.md`,
  `docs/execution-plans/templates/*`, `docs/diagrams/governance_controls.svg` (footer
  text), `observability/README.md`, `README.md`, `ARCHITECTURE.md`,
  `docs/bootstrap-implementation/codequality.md` and `initial_install.md`: old paths
  become new ones, including relative links. The plan template's links become
  `../../intent/` and `../../spec/`. Its Owner actions say to delete `proposals/<ID>/`
  in the commit that applies it.
- Ledger rows keep their historical evidence text, such as `proposals/0001/...`. Only
  paths to files that still exist are updated.

**Proposed in `proposals/0020/`, at the same relative paths, for the owner to apply:**
- `.claude/hooks/governance_gate.sh`: `plans=(docs/execution-plans/plan/active/*.md)`.
  The plan-file exemption becomes `docs/execution-plans/*`, along with its comment and
  deny message.
- `.githooks/check_trailers.sh`: glob `docs/execution-plans/plan/*/$plan-*.md`, and its
  message.
- `.claude/settings.json`: deny and `denyWrite` entries for the two protected bootstrap
  docs at their new paths.
- `.github/CODEOWNERS` and `.github/workflows/governance.yml` (the protected-path diff
  list): the same two paths.
- `governance/rules.yaml`: the header comment, SCOPE-001 (`docs/execution-plans/plan/active/`)
  and QUAL-001 (`docs/records/quality_score.md`). The governance hash will change.
- `AGENTS.md` (plan and tracker paths, protected paths, Layout) and `CLAUDE.md` (plan
  path and template).
- `docs/bootstrap-implementation/project_governance.md` and `agent_governance.md`:
  every old path. The deny rules still name the old paths, so the new paths are open
  to edits until the owner applies this. I treat them as protected anyway.
- These files find plans, so they change in the same commit as the hook, or the checks
  fail in between: `scripts/check_scope.py` (prefix and plan folders),
  `tests/governance/test_check_scope.py`, `tests/governance/test_hooks.py` and
  `tests/governance/test_settings.py`.

## Order of work

- [ ] Write this plan to `docs/exec-plans/active/0020-docs-reorg.md`. Today's gate and
      commit hook only see that path.
- [ ] Owner commits their moves as one commit (it deletes protected files), with
      trailers `Governance: <hash>` and `Plan: 0020`.
- [ ] Make the direct changes. Commit the code and tests, then the docs.
- [ ] Write `proposals/0020/`, then commit it.
- [ ] Run the checks. Everything passes except where the old hook is still in effect.
- [ ] Owner applies `proposals/0020/` in one commit (see Owner actions).
- [ ] New session (GOV-006): run the checks with the verifier, tick this plan, and move
      it to `docs/execution-plans/plan/completed/`.

## Risks

- Between the owner's move commit and the apply commit, `main..HEAD` has commits that
  fail checks. CI runs on the PR head, so only the final state has to pass.
- A missed reference shows as a failing test, or as a broken path found by
  `grep -rnE 'exec-plans|QUALITY_SCORE|governance-activation|ops/observability|docker-compose'`.
- If proposal files are applied only partly, plans get lost: the gate, commit hook and
  scope check would look in different places. They must land in one commit.

## Proof

- The grep above finds nothing outside the finished plans, intents and specs.
- `echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh` passes (ruff,
  vulture, mypy, unit and governance tests).
- In the new session, the SessionStart hook reports plan 0020 at its new path, and an
  edit outside `scope_paths` is denied.
- `.githooks/check_trailers.sh main..HEAD` and
  `.venv/bin/python scripts/check_scope.py main..HEAD` pass.

## Decisions

- Plan, intent and spec files keep `<ID>-<name>.md`. The hooks and scripts find plans
  by matching `<ID>-*.md`.
- `compose.yaml` instead of `docker_compose.yaml`, so `docker compose` still finds it
  without `-f`.
- Finished plans, intents and specs (0001 to 0019) are left as they are. They record
  what was true when each ran (owner, 2026-11-22).
- All four bootstrap docs are updated, so a fresh bootstrap builds this layout (owner,
  2026-11-22).
- `proposals/` keeps its name and stays at the top level. Applied proposals are deleted.
- `governance/` is not reorganised.

## Owner actions

1. Commit your moves (see Order of work).
2. Review `proposals/0020/`. In one commit, copy each file to its path, delete
   `proposals/0020/`, and
   `git mv docs/exec-plans/active/0020-docs-reorg.md docs/execution-plans/plan/active/`.
   That leaves `docs/exec-plans/` empty, so remove it.
3. If the stack is running, restart it from the new folder:
   `docker compose -f observability/compose.yaml up -d`.
4. Start a new session for the close-out.
