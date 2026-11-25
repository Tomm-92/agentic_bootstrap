# Spec 0026: decide on the gaps not assigned to a stage

Intent: [0026-unassigned-gaps-decision](../intent/0026-unassigned-gaps-decision.md)
Status: accepted
Accepted by: Thomas Wilkinson, 2026-11-25

<!-- Copy to docs/execution-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

The intent's open questions are settled by their recommendations, as the owner agreed
for the first draft: the auto mode policy goes in the README, scans run weekly plus a
manual trigger, the project setting stays even if the flag wins, and the chain check
looks only at added plans.

### Scheduled scans (play 14)

1. A new workflow, `.github/workflows/scheduled-scans.yml`, runs every Monday and on
   `workflow_dispatch`, with `permissions: contents: read` and no secrets.
2. Its secrets job runs gitleaks v8.30.1, the release `governance.yml` pins, over the
   full git history with `--redact`, and uploads the SARIF report for 90 days.
3. Its dependencies job runs pip-audit and osv-scanner v2.7.0 over
   `requirements-dev.lock` and `requirements.txt`, as `governance.yml` does, and uploads
   both reports for 90 days.
4. Neither job sets `continue-on-error`, so a finding fails the run and GitHub emails
   the owner.
5. pip-audit is installed at a pinned version in both workflows. Today
   `governance.yml` installs it unpinned.

### Separate commits per gate

6. `check_trailers.sh` accepts a `Plan: <ID>` trailer when a file named `<ID>-*.md`
   exists in `plan/active/`, `plan/completed/`, `intent/` or `spec/` under
   `docs/execution-plans/`. Its error message names all four.
7. Tests in `tests/governance/test_hooks.py` show that a commit whose trailer names only
   an intent passes, and that an ID with no file anywhere still fails.

### Checking the chain

8. A new `scripts/check_chain.py` takes a git range. It checks each plan file the range
   adds under `docs/execution-plans/plan/`. A plan moved from `active/` to `completed/`
   is a rename, not an addition, and isn't checked.
9. A plan passes if its Goal has `Intent: none (<reason>)` with a reason that isn't
   empty. Otherwise it fails unless all of the following hold, at the range's head:
   - its `Intent:` and `Spec:` links resolve to existing files;
   - each linked file's header has `Status: accepted`, and an `Accepted by:` line
     that isn't the template placeholder;
   - the spec's "Policies checked" section names `spec-security`, and isn't the
     template's placeholder text.
10. It prints one line per problem, naming the plan, and exits 1 if there are any.
11. `governance.yml` runs it on pull requests after the plan scope step, in the same
    way, and saves its output in the governance report.
12. `tests/governance/test_check_chain.py` covers each pass and fail case in
    requirement 9, and the rename case, using throwaway git repos as
    `test_check_scope.py` does.

### Acceptance lines (added by this spec)

The intent left "an agent could set `Status: accepted` itself" open, because CI can't
tell the owner's commits from the agent's. A session hook can stop it at the moment of
the edit, so this plan resolves it.

13. `governance_gate.sh` denies an Edit or Write to a file under
    `docs/execution-plans/intent/` or `docs/execution-plans/spec/` when the new text
    adds a `Status: accepted` line, or an `Accepted by:` line that isn't the
    placeholder. For an Edit, the new text is `new_string`, so an edit elsewhere in an
    accepted file still works. For a Write, it is `content` compared with the file on
    disk, so rewriting an accepted file that keeps its header also works. The deny
    message cites the `AGENTS.md` rule.
14. Tests in `test_hooks.py` cover: adding each line by Edit (denied); adding each
    line by Write (denied); an Edit elsewhere in an accepted file (allowed); and
    setting `Status: draft` (allowed).

### Bypass mode and the managed settings file

15. `.claude/settings.json` gains `"disableBypassPermissionsMode": "disable"` under
    `permissions`, with a test in `tests/governance/test_settings.py`.
16. After applying it, the owner starts a new session in this repo with
    `claude --dangerously-skip-permissions`, and again with
    `claude --permission-mode bypassPermissions`. They record in the plan whether
    either session reaches bypass mode. Agents can't see the result (`AGENTS.md`), so
    it's the owner's report.
17. If either flag reaches bypass mode, the plan ships
    `proposals/0026/managed-settings.json` holding only that setting. It also adds a
    README step to install it at `/Library/Application Support/ClaudeCode/` on macOS,
    or `/etc/claude-code/` on Linux. The owner installs it and repeats the test. If
    neither flag reaches bypass mode, no file is shipped.

### Auto mode policy

18. The README's "Development process" section gains a short "When to use auto mode"
    part. Auto mode is acceptable when all three hold: the change has an accepted spec,
    or is a small change the README exempts; it stays within the plan's `scope_paths`;
    and tests cover the code it changes. Otherwise use manual mode. It also says that
    `branch_guard.sh` refuses paid-model commands outside manual mode, so those checks
    are deferred to the owner.
19. `AGENTS.md` gains one line under "While working" pointing to that part. This goes
    through `proposals/0026/AGENTS.md`, built on the owner's uncommitted edit to the
    tracker rule.

### Records

20. The handover's "Gaps not assigned to a stage" section is replaced by the intent's
    decision table, each row giving its result in this plan. Stage 4's "Also revisit"
    paragraph gains a line for play 12's CI failure triage. The "How to pick up a
    stage" bullet that says to commit the plan with the intent and spec is updated to
    match requirement 6.
21. In `docs/bootstrapper_tech_debt_tracker.md`, the two rows this plan closes are
    removed: the chain check and the intent-commit row. The row "The edit gate checks
    scope only for the Edit, Write and NotebookEdit tools" also gains "and acceptance
    lines", because a shell command can still write them (requirement 13). No row is
    added.
22. The README's "One commit holds all three" paragraph is replaced. Each gate can be
    its own commit, with `Plan: <ID>` naming the intent or spec, and the chain check
    runs in CI.
23. `REVIEW.md`'s "Do not report" list adds the chain check.
24. TMW-19 gets a comment listing the decisions, and moves to Done when the plan
    completes. Nothing else changes in Linear.
25. The checks pass, and their output is pasted into the plan.

## Design

**Proposals and order.** These protected files go to `proposals/0026/` at their real
paths:
- `.github/workflows/scheduled-scans.yml` and `.github/workflows/governance.yml`
- `.githooks/check_trailers.sh`
- `.claude/hooks/governance_gate.sh` and `.claude/settings.json`
- `AGENTS.md`, and `managed-settings.json` if requirement 17 applies

The tests in `tests/governance/` read the real paths, so the tests for requirements 7,
14 and 15 land after the owner's apply commit, as in plan 0025.
`scripts/check_chain.py` and its tests aren't protected and land first. The plan's
`scope_paths` list every protected path above, so the owner's apply commits pass the
CI scope check.

**Commits for this plan.** The intent, spec and plan are committed together this one
last time, because the old `check_trailers.sh` is still live until the owner applies
the new one.

**`check_chain.py`** matches `check_scope.py`'s shape: `_git` for subprocess calls, a
`problems(rev_range)` function, and a `__main__` that writes problems to stderr. It
finds added plans with
`git diff --name-only --diff-filter=A --find-renames <range> -- docs/execution-plans/plan/`,
and reads files at the head with `git show`. It parses only the header lines and the
two link lines, with no Markdown library.

**The acceptance-line gate** runs inside the existing PreToolUse branch, before the
`docs/execution-plans/` exemption returns. It reads `tool_input.new_string` or
`tool_input.content` from the hook input it already has.

**Options rejected:**
- **Adding `schedule:` to `governance.yml`.** On a schedule, `BASE_SHA` is empty, so
  the diff-based steps would need new guards. A separate workflow is simpler.
- **CodeQL as the full-repo scan.** Code scanning on private repos needs GitHub
  Advanced Security. Ruff's `S` rules already run Bandit's checks on every PR.
- **A new trailer such as `Intent:` for gate commits.** IDs are shared across the
  intent, spec and plan, so `Plan: <ID>` already names the change. A second trailer
  would mean changing GOV-004's wording in `governance/`.
- **Checking every plan, not just added ones.** Plans 0001 to 0016 predate the chain
  and would fail.
- **Checking authorship of acceptance in CI.** The owner's commits and the agent's
  share a git author, so CI can't tell them apart. The session hook catches it as it
  happens instead.
- **A network allowlist in project settings.** Not needed (intent).

## Out of scope

- Stage 4, and play 12's CI failure triage, which follows it.
- Play 11 (TMW-21).
- The plan–diff sync check, which stays in the tracker.
- Branch protection and required checks. All workflows stay advisory except the new
  scheduled one, which has no pull request to block.

## Policies checked

`spec-security` report:

- DEP-001: finding. Requirement 5: `governance.yml` installs pip-audit with no pin,
  and copying that line would add a second unpinned install. Fix: pin pip-audit in
  both workflows, with the owner approving the version. The spec now requires this.
  gitleaks and osv-scanner are already pinned to the releases they reuse.
- SEC-002: finding. Requirement 2: a full-history gitleaks report would hold any secret
  it finds, and the artifact is kept for 90 days. Fix: `--redact`, now in requirement
  2. The workflow uses no secrets, and `contents: read` limits its token.
- SEC-001: no finding. Nothing reads or asks an agent to read a `.env` file. The
  acceptance gate reads only the hook input and the intent or spec on disk.
- DATA-001: no finding. No new service receives prompts, sessions, traces or outputs.
  The workflows send nothing out. The TMW-19 comment is planning text.
- Not touched: TOOL-001, FS-001, SBX-001.

Other rules in `governance/rules.yaml`:

- **GOV-002:** every protected file goes through `proposals/0026/`, listed above.
  `governance/` doesn't change.
- **GOV-004:** the trailer rule still requires a `Governance:` hash and a `Plan:` ID
  for every commit. It only widens which files an ID may name.
- **GOV-006:** one session. If the plan outgrows it, the rest moves to a new plan with
  no Linear issue.
- **SCOPE-001, SCOPE-002:** `scope_paths` cover every edited file, including the
  owner's apply commits and the owner's `AGENTS.md` edit.
- **COST-001:** no paid calls. The workflows run no model, and the bypass test needs
  no model call beyond starting a session.
- **EVID-001:** reports are kept for 90 days, as `retention_days` requires.
- `docs/records/security.md`: no data or access change. A redacted report holds no
  secret text.
- `app/AGENTS.md`: not applicable, nothing in `app/` changes.

## Concerns

- **The first full-history gitleaks run may fail on old findings.** If it does, the
  owner reviews each one. A real leaked secret is rotated, and a false positive goes in
  a `.gitleaksignore`, which is part of the same plan.
- **Requirement 13 goes beyond the intent.** The intent left acceptance authorship
  open. The spec resolves it, following the owner's instruction to resolve here what
  can be. A shell command can still write the lines, and requirement 21 records that
  on the existing shell-write row rather than adding a row. If the owner would rather
  keep the plan to the intent's table, strike requirements 13, 14 and that part of 21.
- **The bypass test depends on the owner.** Agents can't see which mode a session
  starts in, so requirements 16 and 17 rest on the owner's report.
- **A managed settings file applies to every project on the machine,** not only this
  repo. It would hold only `disableBypassPermissionsMode`, so other projects lose
  bypass mode too. The owner should know this before installing it.
- **The plan is large for one session.** It has five parts and an apply step between
  the proposals and their tests. The order of work puts the unprotected parts first,
  so if it runs long, the rest moves to a new plan with the work already done intact.
- **`AGENTS.md` has an uncommitted owner edit.** The proposal must start from that
  version. The owner commits their edit under `Plan: 0026` once the plan is active.
