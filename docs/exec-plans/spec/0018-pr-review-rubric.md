# Spec 0018: PR review rubric

Intent: [0018-pr-review-rubric](../intent/0018-pr-review-rubric.md)
Status: accepted
Accepted by: <owner>, <YYYY-MM-DD>

<!-- Copy to docs/exec-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

1. `REVIEW.md` at the repo root is the PR review rubric. It follows the playbook's
   example ("AI in the PR review loop") and has these sections:
   - **Passes.** Three passes, and every finding is tagged with its pass:
     - Bugs: logic errors, broken edge cases, regressions.
     - Security: injection risks, authentication and authorisation gaps, secrets or
       personal data in code, logs or telemetry, and prompt injection reaching a tool.
     - Compliance: the change matches its intent, spec and plan, the design
       principles (requirement 2), and `governance/rules.yaml`. This includes a plan
       that widens its own `scope_paths`, and a build that departs from the plan
       without updating it.
   - **Severity.** Every finding is Important or Nit. Important is reserved for
     findings that would break behaviour, leak data or breach a policy (a rule in
     `governance/rules.yaml` or an `AGENTS.md` rule). Style and naming are Nits.
   - **Nit cap.** At most five Nits per review. Any beyond that are summarised as a
     count.
   - **Do not report.**
     - Generated paths: `output/` and `*.lock`.
     - Anything CI already enforces: ruff lint and format, vulture, mypy, the unit
       tests, the rule and profile schema tests, commit trailers, the plan scope
       check, gitleaks, pip-audit and osv-scanner.
   - **Output.** Each finding names its pass, its severity, and the file and line, and
     says why it matters. The review ends with the tally line (requirement 4).
2. The design principles for the Compliance pass are `ARCHITECTURE.md` (trust
   boundaries, where each rule is enforced, the telemetry invariants), the "Code style"
   section of `AGENTS.md`, and `app/AGENTS.md`. `REVIEW.md` names them.
3. `scripts/ai_review.py` builds the review prompt from two kinds of input:
   - **Instructions, read at the base commit:** `REVIEW.md`, `AGENTS.md`,
     `app/AGENTS.md` and `ARCHITECTURE.md`. They go in the system prompt with a short
     fixed preamble. The preamble keeps the current framing: the human decides the
     merge, and the PR's contents are data, never instructions.
   - **Data, read at the head commit:** the plan named by the head commit's `Plan:`
     trailer, the intent and spec that share its ID under `docs/exec-plans/intent/`
     and `spec/`, the list of changed files, and the diff. A missing intent or spec is
     stated in the prompt, for example "No spec for plan 0019". Small changes have
     neither (`Intent: none`).
4. The review's last line is the tally, exactly `Tally: important=<n> nit=<n>`. The Nit
   count includes Nits summarised beyond the cap. If the model's last line doesn't
   match, the script appends `Tally: unavailable`, so a later gate never misreads
   free text.
5. Refusal handling is unchanged. On `stop_reason == 'refusal'` the script returns
   `REFUSED`, which tells the owner to review unaided, and it doesn't retry on another
   model (MODEL-001).
6. `ai-review.yml` checks out the base commit (`BASE_SHA`), and installs the
   dependencies and runs `scripts/ai_review.py` from there. The head commit's files
   reach the reviewer only as data, through git (requirement 3). The workflow is
   still advisory (`continue-on-error: true`) and still posts one PR comment.
7. The tally doesn't block merges. Nothing in this change reads the tally.
8. The evidence review moves from `docs/REVIEW.md` to `docs/EVIDENCE_REVIEW.md`, with
   its review log intact. These live references are updated:
   - `README.md`
   - `docs/governance-activation.md` (the EVID-001 row)
   - `scripts/evidence_report.py`
   - `docs/exec-plans/handover.md`
   - `docs/governance_implementation.md` and `docs/agent_governance_implementation.md`,
     by proposal

   Completed plans keep their old references.
9. The evidence review's Inputs list "PR review findings: the ai-review comments and
   their `ai-review` artifacts. A recurring Important finding is a candidate rule or
   `AGENTS.md` change." The `governance_implementation.md` proposal lists the same
   input.
10. The tech-debt row "`ai-review.yml` runs the PR's own copy of `scripts/ai_review.py`
    with the API key available" is removed once the requirement 6 proposal exists.
    The remaining risk is recorded under Concerns, and in a new row if it stays open.
11. The handover file marks stage 1 done (plan 0017) and stage 2 as plan 0018, and
    corrects its stage 2 section where this spec departs from it.
12. Unit tests in `tests/governance/test_ai_review.py`, using the existing stub client
    and stubbed git, show that:
    - the system prompt holds `REVIEW.md`, read at the base commit
    - the user content holds the plan, intent and spec, read at the head commit
    - a missing intent or spec is stated, not an error
    - a valid tally is kept, and a missing or malformed one becomes `Tally: unavailable`
    - the existing reviewer-model and refusal tests still pass

## Design

**Trusted instructions from base, PR content as data.** Today the script reads the
plan from the working tree, and the workflow checks out the PR. So a PR can rewrite
the reviewer that reviews it, along with any rubric that reviewer reads. Splitting by
commit closes that. Everything that tells the model how to review comes from
`BASE_SHA`, and everything under review comes from `HEAD_SHA`. One git helper serves
both: `_git('show', f'{sha}:{path}')`. Files are found by ID with
`_git('ls-tree', '--name-only', head, 'docs/exec-plans/<folder>/')` and a prefix
match, replacing the working-tree `glob`.

**Prompt shape.** The system prompt is the preamble followed by each instruction file
in its own tag (`<rubric>`, `<agents>`, `<app_agents>`, `<architecture>`). The user
content keeps today's tags (`<plan>`, `<files>`, `<diff>`) and adds `<intent>` and
`<spec>`. Together the instruction files are about 15 KB.

**Tally check.** The script checks the last non-blank line against
`^Tally: important=\d+ nit=\d+$`. The model writes the tally rather than the script
counting findings, because the findings are free text.

**Workflow.** `actions/checkout` takes `ref: ${{ github.event.pull_request.base.sha }}`
with `fetch-depth: 0`, so the head commit is still available to `git show`. The
trailer step already reads `HEAD_SHA` through git, so it works unchanged. Dependencies
are installed from the base commit's `requirements-dev.lock`, so a PR can't change
what gets installed in a job that holds the key.

**Options rejected:**
- **Filtering generated paths out of the diff in the script** (`':(exclude)output/**'`).
  It would save tokens, but it moves policy into code. `REVIEW.md` stays the only
  place the owner edits the review standard. Revisit if lock-file diffs make reviews
  costly.
- **Structured output or tool use for findings.** A machine-readable findings list
  would let the script count the tally itself. That's more code and more prompt than
  one advisory comment needs. The tally line is enough for a later gate.
- **Loading all of `governance/rules.yaml` into the prompt.** It's large, and
  `AGENTS.md` plus the plan's `rules:` list already name the rules in play. The
  Compliance pass cites rule IDs from those.
- **Gathering PR findings in `scripts/evidence_report.py`.** That needs the GitHub API
  and a network call. The owner reads the comments and artifacts during the review.
  Automate it if the review shows it's worth it.
- **The `@claude` fix-on-comment loop.** Deferred by the intent, and recorded in the
  tech-debt tracker.

## Out of scope

- The `@claude` fix-on-comment loop and managed Code Review.
- Blocking a merge on the tally, and branch protection.
- Adding `ANTHROPIC_API_KEY` as a repo secret. That's the owner's COST-001 decision.
- Evals for the reviewer, which belong with stage 4.
- Phase A05's additions to the evidence review.
- Rewriting completed plans that mention `docs/REVIEW.md`.

## Policies checked

- `governance/rules.yaml`:
  - **REV-001:** the reviewer still uses the allowlisted reviewer model, which differs
    from the executor's. The existing test stays.
  - **MODEL-001:** no refusal fallback to a model outside the allowlist.
  - **GOV-002:**
    - `ai-review.yml`, `governance_implementation.md` and
      `agent_governance_implementation.md` change by proposal in `proposals/0018/`.
    - `REVIEW.md` isn't on the protected list, but it is now policy that the owner
      owns. See Concerns.
  - **SEC-002:** the job that holds the API key no longer runs, or installs from, PR
    code (requirement 6).
  - **COST-001:**
    - The build makes no paid calls, and the tests use the stub client.
    - Each review's prompt grows by about 15 KB of instructions plus the intent and
      spec. The workflow still runs only once the owner adds the secret.
  - **DEP-001:** no new dependencies.
  - **EVID-001:** the evidence review keeps its log and purpose, and gains an input.
  - **GOV-004, GOV-006, SCOPE-001, SCOPE-002:** one plan, one session, the
    trailers, and edits inside `scope_paths`.
- `docs/SECURITY.md`:
  - No new data leaves the repo. The reviewer already sends the diff and plan to the
    model provider.
  - The intent and spec join them. Both are repo files, already public to anyone who
    can read the PR.
- `app/AGENTS.md`: `app/` doesn't change, so nothing applies.

## Concerns

- **The workflow file still comes from the PR.** On `pull_request`, GitHub runs the
  workflow as it is in the PR's merge commit, so a same-repo PR can edit
  `ai-review.yml` itself and reach the key. Requirement 6 still matters: an agent can
  edit `scripts/` inside a plan's scope, but deny rules and the sandbox block it from
  `.github/` (GOV-002). With one author, owner review of protected-path changes covers
  the rest. Closing this fully means `pull_request_target`, which brings its own
  checkout risks, or branch protection. A tech-debt row records it.
- **Bootstrap.** Under requirement 6, a PR is reviewed by the base branch's rubric
  and script. This PR's own review, if the secret were set, would run the old script.
  Once the owner applies the proposal after merge, the next PR is the first reviewed
  under the rubric. There's no fallback for a base without `REVIEW.md`, because that
  base never exists after this lands.
- **`REVIEW.md` isn't a protected path.** An agent could weaken the rubric within a
  plan that scopes it. Because of requirement 6, such a change applies only after it
  merges, so the owner sees it in review first. Protecting it would mean a
  `governance/` or `AGENTS.md` change, and needs its own intent. Recommendation: leave
  it unprotected for now, and revisit if the evidence review finds rubric edits.
- **The tally comes from the model.** It can miscount. It's advisory, and requirement
  4 guarantees only its format, not its accuracy.
