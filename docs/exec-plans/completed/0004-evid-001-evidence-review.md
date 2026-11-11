---
id: '0004'
rules: [EVID-001, GOV-002, SCOPE-001, SCOPE-002]
scope_paths:
  - proposals/0004/**
  - docs/REVIEW.md
  - docs/governance-activation.md
  - docs/images/**
---

# Plan 0004: activate the EVID-001 evidence review

## Goal

Hold the first evidence review ("After the run" step 8 in
`docs/agent_governance_implementation.md`) and propose moving the EVID-001 control
`evidence review each sprint (S09)` from `planned` to `active`.

## Evidence

- `.venv/bin/python -m scripts.evidence_report` and `.sessions/sessions.db`, which
  holds real `claude-haiku-5-5` runs from 2026-11-11.

## Decisions

- The owner approves the review answers before they are written to `docs/REVIEW.md`.
- Rule changes the review suggests are raised as proposals under `proposals/0004/`,
  not applied.
- The proposal changes only the control's status in `proposals/0004/governance/rules.yaml`.
- `docs/images/governance-controls.svg` is edited by hand to show the state after the
  owner applies the proposal: 34 active, 12 planned.
- The review is thin, covering one prompt and one free tool, but it meets "After the run"
  step 8 in `docs/agent_governance_implementation.md`.

## Owner actions

1. In `docs/governance-activation.md`, change the EVID-001 review row's owner check to
   `Confirmed by the owner, <date>`.
2. Run `.venv/bin/python scripts/check_activation.py proposals/0004/governance/rules.yaml`.
   It must print "The proposal passes."
3. Copy `proposals/0004/governance/rules.yaml` to `governance/rules.yaml` and commit
   through an owner PR.
