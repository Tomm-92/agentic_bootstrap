# Review instructions

The PR review rubric. `scripts/ai_review.py` applies it to every pull request, reading
it from the base branch, so a change to it applies from the next PR after it merges.
The owner owns it. Findings inform the owner's merge decision and never approve or
block a PR on their own.

## Passes

Run three passes and tag each finding with its pass:

- **Bugs:** logic errors, broken edge cases, regressions.
- **Security:** apply the Diff line of each rule in the security checklist,
  `.claude/skills/spec-security/checklist.md`, and cite the rule ID. The checklist is
  the only list of security checks: don't add others here.
- **Compliance:** the change matches its intent, spec and plan, the design principles,
  and the rules in `governance/rules.yaml`. Flag a plan that widens its own
  `scope_paths`, and a build that departs from its plan without updating it. The
  design principles are `ARCHITECTURE.md`, the "Code style" section of `AGENTS.md`,
  and `app/AGENTS.md`.

## What Important means here

Reserve Important for findings that would break behaviour, leak data or breach a
policy: a rule in `governance/rules.yaml` or in `AGENTS.md`. Everything else is a Nit.
Style and naming are Nits.

## Cap the nits

Report at most five Nits per review. Summarise the rest as a count.

## Do not report

- Generated paths: `output/` and `*.lock` files.
- Anything CI already enforces:
  - ruff lint and format, vulture, mypy and the unit tests
  - the rule and profile schema tests
  - commit trailers, the plan scope check and the intent, spec and plan chain check
  - the security checks in the checklist's "Already enforced, don't report" list

## Output

One line per finding: `[Pass] [Important|Nit] path:line: what is wrong and why it
matters.` If there are no findings, say so. End with this line, exactly, counting every
Nit, including summarised ones:

Tally: important=<n> nit=<n>
