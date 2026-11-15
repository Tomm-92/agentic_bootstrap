---
id: '0009'
rules: [SCOPE-001, SCOPE-002, GOV-002]
scope_paths:
  - README.md
  - docs/exec-plans/**
  - proposals/0009/**
---

# Plan 0009: put getting started at the top of the README

## Goal

A person who clones the repo should see straight away how to start developing.
Steps 1 to 3 (`initial_install.md`, `codequality.md`,
`governance_implementation.md`) are already applied in every clone, so the only
remaining step is to decide what the agent does and run
`docs/agent_governance_implementation.md`. Documentation only, no code changes.

## Checklist

- [x] Getting started section directly after the intro.
- [x] Per-clone setup (venv, git hooks, open at repo root) in one place.
- [x] The purpose inputs a cloner must decide, with an example.
- [x] Prerequisites, the exact prompt, and what happens after the run.
- [x] Remove the duplicated setup blocks lower down.
- [x] Propose a guided purpose interview for
      `docs/agent_governance_implementation.md` in `proposals/0009/`.
- [x] README step 2 describes the interview instead of a file to fill in.

## Decisions

- Purpose inputs are listed from the "Purpose inputs" table in
  `docs/agent_governance_implementation.md`, which stays the source of truth.
- The owner asked for the run to ask for purpose and output, then guide them
  through the other inputs, instead of needing a prepared file. That changes a
  protected file (GOV-002), so it goes to `proposals/0009/` and the scope was
  widened to that folder.
- The run recommends each remaining input from the purpose and output, and the
  owner confirms or changes it. A confirmed recommendation is the owner's answer,
  so the "don't guess" rule still holds.

## Risks

- Until the owner applies the proposal, the README describes a guided interview
  that the live `docs/agent_governance_implementation.md` doesn't yet ask for.
  Apply both in the same merge.

## Owner actions

- Review the README wording.
- Review `proposals/0009/docs/agent_governance_implementation.md`, then apply it:
  `cp -R proposals/0009/. . && rm -rf proposals/0009`.
