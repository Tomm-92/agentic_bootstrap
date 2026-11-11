---
id: '0005'
rules: [REV-001, COST-001, GOV-002, SCOPE-001, SCOPE-002]
scope_paths:
  - proposals/0005/**
---

# Plan 0005: skip the AI review with an `ai-review: no` trailer

## Goal

Let the author skip the paid `ai-review` workflow on a pull request by adding the
trailer `ai-review: no` (or `ai-review:no`) to the commit message, so not every PR
starts paid calls (COST-001).

## Change

- `proposals/0005/.github/workflows/ai-review.yml`: a first step reads the trailer from
  the PR's head commit with `git log -1 --format='%(trailers:key=ai-review,valueonly)'`.
  Every later step runs only when the API key is set and the trailer is not `no`.

## Decisions

- Only the PR's head commit is read. A later push without the trailer turns the
  review back on, so the skip applies to the commit that would be reviewed.
- The trailer must sit in the commit message's final paragraph, with `Governance:`
  and `Plan:`, or git does not parse it as a trailer.
- `.githooks/check_trailers.sh` accepts other trailers, so it needs no change.

## Risks

- A skipped run still shows as a green `ai-review` check, as it does today when the
  key is unset. The step summary says the review was skipped.

## Owner actions

1. Review `proposals/0005/.github/workflows/ai-review.yml`.
2. Copy it to `.github/workflows/ai-review.yml` and commit through an owner PR.
3. Move this plan to `docs/exec-plans/completed/`.
