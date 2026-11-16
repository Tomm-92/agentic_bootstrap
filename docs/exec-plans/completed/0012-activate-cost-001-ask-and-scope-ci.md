---
id: '0012'
rules: [COST-001, SCOPE-002, GOV-002, SCOPE-001]
scope_paths:
  - docs/exec-plans/**
  - docs/governance-activation.md
  - proposals/0012/**
---

# Plan 0012: activate the COST-001 permission ask and the SCOPE-002 CI scope check

## Goal

Propose moving two controls from `planned` to `active`, as step 5 of the 0010 handover
describes:

- COST-001: `Claude Code permission ask on paid-model commands (S04)`
- SCOPE-002: `governance workflow scope check (S05)`

## Evidence

Confirmed by the owner on 2026-11-16, in a session under governance `b233b58`:

- COST-001 (S04): `.venv/bin/pytest -q -m integration` and
  `.venv/bin/python -m scripts.local_session --real hi` both prompted and were declined.
  `.venv/bin/python -m scripts.local_session hi` ran without a prompt and returned the
  scripted reply "Demo is a placeholder project."
- SCOPE-002 (S05): the "Plan scope" step passed on the pull request for
  `agent-instructions-split` (commit `a2ac814`).

## Checklist

- [x] Rewrite both controls' owner checks in `docs/governance-activation.md` to
      `Confirmed by the owner, 2026-11-16`, with what was seen.
- [x] Write `proposals/0012/governance/rules.yaml`, with only those two statuses moved
      to `active`.
- [x] Run `.venv/bin/python scripts/check_activation.py proposals/0012/governance/rules.yaml`.
      It must print "The proposal passes."
- [x] Delete `docs/exec-plans/handover.md`.
- [x] Add the tech-debt row on `.diff` proposals and the scope check.

## Decisions

- The PR number wasn't given and `gh` couldn't reach GitHub from the sandbox, so the
  ledger names the PR by branch and commit.
- The `.diff` gap in `scripts/check_scope.py` is fixed in plan 0013, not here: this plan
  activates the check that ran on the PR, so changing it in the same proposal would
  activate code CI hasn't run. Agreed with the owner, 2026-11-16.

## Risks

- Handover step 4's protected-path checks weren't run as tool calls. The agent turned
  down the Edit of `app/AGENTS.md` and `touch ruff.toml` by instruction (GOV-002)
  before calling a tool, so this session didn't see the deny rule or the sandbox
  refuse them. Neither control is in this proposal. The sandbox control was already
  confirmed on 2026-11-11.

## Owner actions

1. Review the ledger diff and `proposals/0012/governance/rules.yaml`.
2. Copy `proposals/0012/governance/rules.yaml` to `governance/rules.yaml`, delete
   `proposals/0012/`, and commit with `Plan: 0012` and the parent's governance hash
   (`b233b5839943381999383bd2c0341e4a5184bc1c`).
3. Start a new session, because the governance hash changes.
