# Intent 0018: PR review rubric

Author: Claude, drafted for the owner
Status: accepted
Accepted by: Tom Wilkinson, 2026-11-19

<!-- Copy to docs/exec-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

## Problem

The AI pre-review on pull requests (`scripts/ai_review.py`, run by
`.github/workflows/ai-review.yml`) follows a three-line prompt hard-coded in the
script. Nobody can read or change its review standard without editing code. The review
compares a diff with the plan only. It doesn't read the intent and spec that the
process from plan 0017 now produces, so it can't tell whether a change does what was
accepted. It doesn't rate its findings. A cosmetic note reads with the same weight as a
real bug, and nothing caps the noise. This is play 10 of the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook),
stage 2 in `docs/exec-plans/handover.md`.

This hurts the owner, who reviews every PR and gets findings that are hard to triage
and that never check against the intent and spec.

The repo-root name the playbook and Anthropic's managed Code Review expect,
`REVIEW.md`, is effectively taken. `docs/REVIEW.md` holds the sprint evidence review
(EVID-001), a different document with a different purpose, so a second `REVIEW.md`
would confuse people and agents.

Nothing feeds what PR reviews find back into the rules. A finding that recurs across
PRs points to a missing rule or a gap in `AGENTS.md`, but the evidence review never
sees it.

## Proposed outcome

- A repo-root `REVIEW.md` holds the PR review rubric. Its passes are Bugs, Security
  and Compliance, and Compliance checks against the intent, spec and plan, and the
  design principles. Findings are Important or Nit. Important is reserved for findings
  that would break behaviour, leak data or breach a policy. Nits are capped per review,
  and generated paths such as `output/` and lock files are left out. The owner owns the
  rubric and can change the review standard by editing it, without touching code.
- The AI pre-review applies that rubric. It reads the plan's linked intent and spec as
  well as the plan, and ends with a severity tally line that a later check could gate
  on. It still treats the PR's contents as data, not instructions, and still handles a
  refusal by telling the owner to review unaided.
- The evidence review is `docs/EVIDENCE_REVIEW.md`, and every live reference to it is
  updated. Completed plans are left as they were. Its purpose doesn't change.
- The evidence review lists PR review findings among its inputs, so a recurring
  Important finding becomes a candidate rule change.
- `docs/exec-plans/handover.md` shows stage 1 as done and stage 2 as this plan.
- The AI pre-review still decides nothing. The owner still decides every merge.
- No `@claude` fix-on-comment loop. The owner decided to defer it, and the tech-debt
  tracker records the gap and what closes it.

## Affected users and systems

- **The owner:** reads the rubric's findings on each PR, and owns `REVIEW.md`.
- **`scripts/ai_review.py`** and its tests in `tests/governance/test_ai_review.py`.
- **`.github/workflows/ai-review.yml`** (protected, so by proposal), if the script is
  to run from the base branch.
- **The evidence review:** renamed, plus one new input. References in `README.md`,
  `docs/governance-activation.md`, `scripts/evidence_report.py`, the handover file,
  and the protected `docs/governance_implementation.md` and
  `docs/agent_governance_implementation.md`, the last two by proposal.
- **Not affected:** the product agent in `app/`, and the runtime rules.

## Constraints

- **REV-001:** the reviewer keeps running on the allowlisted reviewer model, a
  different model from the executor's. No refusal fallback to another model
  (MODEL-001).
- **GOV-002:** protected paths change only through `proposals/0018/`.
- **COST-001:** the build makes no paid calls. Unit tests use fakes and never reach
  the network. Real reviews happen only in CI, once the owner adds
  `ANTHROPIC_API_KEY` as a repo secret.
- **DEP-001:** no new dependencies.
- **Free GitHub:** required checks aren't available on private GitHub Free, so nothing
  can block a merge yet.
- **SEC-002:** the workflow runs the PR's own copy of `ai_review.py` with the API key
  available (tech-debt tracker). Growing the script makes that risk larger.

## Open questions

1. **Should the severity tally block a merge?** Recommendation: advisory only. The
   tally line exists so a gate can be added once branch protection is available.
2. **Run `ai_review.py` from the base branch?** This would close the tech-debt entry
   in the same proposal. Recommendation: yes. It changes `ai-review.yml`, so it goes
   by proposal.
3. **The nit cap.** The playbook's example is five per review. Recommendation: five.
4. **Design principles.** Compliance checks against "the design principles". Which
   document holds them here: `ARCHITECTURE.md`, `AGENTS.md`'s code style, or both?
   The spec settles this.
