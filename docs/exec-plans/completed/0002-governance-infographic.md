---
id: '0002'
rules: [GOV-002, SCOPE-001, SCOPE-002, QUAL-001]
scope_paths:
  - README.md
  - docs/images/**
---

# Plan 0002: governance infographic

## Goal

Add an infographic to the README showing which governance controls exist, where
they act, and why, drawn from `governance/rules.yaml` and
`docs/governance-activation.md`.

## Decisions

- An SVG in `docs/images/`, so GitHub renders it in the README and it diffs as text.
- It shows the controls by the point where they act (session, commit, CI, merge,
  runtime), with each rule's `because`, and marks planned controls apart from active
  ones.

## Risks

- The graphic copies facts from `governance/rules.yaml`, so it goes stale when a
  control changes status. The README says the catalogue is the source of truth.

## Owner actions

- None.
