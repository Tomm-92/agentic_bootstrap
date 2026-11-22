---
id: '0003'
rules: [COST-001, GOV-002, SCOPE-001, SCOPE-002]
scope_paths:
  - proposals/0003/**
  - docs/governance-activation.md
  - docs/images/**
---

# Plan 0003: activate the COST-001 token budget

## Goal

Propose moving the COST-001 runtime control, `governance layer enforces
session_token_budget (S06)`, from `planned` to `active`, now that the Stage 6 manual
run has been done against a real model.

## Evidence

- On 2026-11-11 at 20:07 and 20:08, `.sessions/sessions.db` recorded `claude-haiku-5-5`
  model calls with real `total_token_count` values (1727, 1804, 1799).
- `.venv/bin/pytest -m integration` passed. `agent.app` runs the `GovernancePlugin`,
  which raises an error on a response without a token count, so a real response
  went through the budget check.

## Decisions

- The owner asked for this plan to run in the session that made plan 0002, even
  though AGENTS.md asks for a new session per plan.
- The proposal changes only the control's status in `proposals/0003/governance/rules.yaml`.
- The infographic is regenerated from the proposed rules, so it shows the state the
  repo will be in once the owner applies the proposal.

## Owner actions

1. In `docs/governance-activation.md`, change COST-001's owner check to
   `Confirmed by the owner, 2026-11-11`.
2. Run `.venv/bin/python scripts/check_activation.py proposals/0003/governance/rules.yaml`.
   It must print "The proposal passes."
3. Copy `proposals/0003/governance/rules.yaml` to `governance/rules.yaml` and commit
   through an owner PR.
