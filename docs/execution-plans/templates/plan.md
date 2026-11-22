---
id: '<ID>'
rules: [SCOPE-001]
scope_paths:
  - <glob>
---

# Plan <ID>: <name>

<!-- Written to docs/execution-plans/plan/active/<ID>-<name>.md when the owner approves it
in plan mode. Moved to docs/execution-plans/plan/completed/ when done. -->

## Goal

Intent: [<ID>-<name>](../../intent/<ID>-<name>.md), or `Intent: none (<reason>)` for a small
change.
Spec: [<ID>-<name>](../../spec/<ID>-<name>.md)

What this plan delivers, in a few sentences.

## Files that change

- `<path>`: what changes and why.

## Order of work

- [ ] <step>
- [ ] ruff, mypy, vulture, and the unit and governance tests pass.
- [ ] Move this plan to `completed/`.

## Risks

What could break, and how it would show.

## Proof

Commands and results that show the change works.

## Decisions

Choices made while planning or building, with the reason for each.

## Owner actions

Steps only the owner can take, such as reviewing and applying `proposals/<ID>/`. The
commit that applies a proposal also deletes `proposals/<ID>/`.
