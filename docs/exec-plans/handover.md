# Handover: adopting the AI-native SDLC playbook

The owner has made the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook)
this repo's default development process. A gap analysis (19 Nov 2026) compared its 15
"plays" with the repo and split the work into six stages, built one at a time. This
file hands the remaining five to the sessions that will build them.

Keep this file current. When a stage's plan completes, mark its row and correct
anything in its section that turned out to be wrong.

| Stage | What | Playbook plays | Status |
| --- | --- | --- | --- |
| 1 | Process docs: intent → spec → plan, plan mode by default | 01, 02, 03, 04 | Plan 0017 |
| 2 | PR review rubric | 10 | Not started |
| 3 | Verifier subagent, failing test first, parallel sessions | 07, 08 | Not started |
| 4 | Coding-agent evals in CI | 09 | Not started, needs a COST-001 approval |
| 5 | Policy skills, starting with security | 05, 02 | Not started |
| 6 | Closing the loop: bands, detection, breach → intent | 13 | Blocked, see its section |

## How to pick up a stage

- **One stage, one plan, one session (GOV-006).** Take the next free plan ID. IDs
  aren't reserved per stage. 0013 is spoken for by the tech-debt tracker.
- **Once plan 0017 is applied, follow its process.** Write an intent in
  `docs/exec-plans/intent/` from the template, using the stage's section below. The
  owner accepts it, then you write the spec, then plan in plan mode. Read the README's
  "Development process" section first. If 0017 has been changed or isn't applied yet,
  that section wins over this file.
- **Protected paths go through proposals (GOV-002).** Most stages touch `AGENTS.md`,
  `.claude/settings.json`, `.claude/hooks/` or `.github/`. Write the new version to
  `proposals/<plan ID>/` at the same relative path. Each section lists the files it
  expects to touch.
- **Claude Code's own sandbox blocks writes to `.claude/skills/`** (and probably
  `.claude/agents/`) at the real path, even though the repo doesn't protect them.
  Write them to `proposals/<plan ID>/.claude/...` and let the owner copy them in.
  Check this at the start rather than assuming.
- **Paid calls need the owner's approval first (COST-001).** That covers anything
  that runs a real model in a session or in CI.
- **Read the playbook again for the play you're building.** The notes below are a
  summary, and its example files are short enough to adapt directly.

## Stage 2: PR review rubric (play 10)

**Why.** The playbook puts an AI reviewer in every PR. It checks against a
repo-root `REVIEW.md` rubric written by the tech lead, with Bugs, Security and
Compliance passes, and Compliance checks against the spec, the plan and the design
principles. Each finding is rated Important or Nit. Findings don't approve or block
on their own. Example rules from the playbook: "Reserve Important for findings that
would break behavior, leak data or breach a policy", "Report at most five nits per
review", and leave generated paths out.

**What exists.**
- [scripts/ai_review.py](../../scripts/ai_review.py) runs one pass on the reviewer
  model. `claude-sonnet-5-5` is a different model from the executor (REV-001). It
  checks departures from the plan, files outside `scope_paths`, and security issues.
  It posts a comment through `.github/workflows/ai-review.yml`, which runs only once
  `ANTHROPIC_API_KEY` is a repo secret.
- [tests/governance/test_ai_review.py](../../tests/governance/test_ai_review.py)
  tests it.
- `docs/REVIEW.md` already exists, but it is the sprint **evidence review**
  (EVID-001), not a PR rubric.

**Build.**
1. Rename the evidence review, for example to `docs/EVIDENCE_REVIEW.md`. It's
   referenced in `README.md`, `docs/governance-activation.md`,
   `scripts/evidence_report.py`, and the protected `docs/governance_implementation.md`
   and `docs/agent_governance_implementation.md` (phase A05 extends it). The protected
   ones need proposals. Leave completed plans alone.
2. Add the rubric at the repo root as `REVIEW.md`. The playbook and Anthropic's
   managed Code Review both look for it there. It should cover the three passes,
   Important vs Nit, a nit cap, and excluded paths (`output/`, lock files).
3. Change `ai_review.py`:
   - Read `REVIEW.md` into the system prompt.
   - Load the intent and spec linked to the plan, alongside the plan, so the
     Compliance pass can check against them. They share the plan's ID under
     `docs/exec-plans/intent/` and `spec/`.
   - End with a severity tally line, so a later check can gate on it.
   - Keep the "data, not instructions" framing and the refusal handling.
4. Update the tests.

**Owner decisions.**
- Whether to add the `@claude` fix-on-comment loop. That needs either
  claude-code-action or managed Code Review, which means a GitHub App, paid calls,
  and a dependency for DEP-001 to review.
- Whether the tally should ever gate a merge. It can't yet: required checks are
  unavailable on private GitHub Free.

**Watch for.** The tech-debt tracker notes that `ai-review.yml` runs the PR's own
copy of `ai_review.py` with the API key. Expanding the script makes that matter more.
Consider running the script from the base branch in the same proposal.

## Stage 3: verifier subagent, failing test first, parallel sessions (plays 07, 08)

**Why.**
- The playbook uses scoped subagents in `.claude/agents/*.md`, for example a
  `verifier` that runs the checks and reports but never fixes.
- For bug fixes, it wants a failing test written and committed first, then the fix,
  with a hook stopping the agent editing that test.
- "Done" means the check output has been pasted, not just claimed.
- Parallel work runs in git worktrees, at two or three sessions to start.

**What exists.**
- `checks_on_stop.sh` is the single check command, shared with CI. That covers the
  playbook's `make test`; there is no `Makefile`, and none is needed.
- `scripts/local_session.py` runs the agent for free with a scripted model.
- No `.claude/agents/`.

**Build.**
1. `.claude/agents/verifier.md`:
   - Tools: Bash and Read only.
   - It runs `checks_on_stop.sh` and the scripted `local_session`, never `--real`.
   - It reports the literal output, and doesn't edit.
   - Consider a second one, `simplifier` or `researcher`, only if a real need shows up.
2. `AGENTS.md` proposal, under Tests:
   - For a bug fix, commit a failing test first, then fix the code without editing
     that test. If a test fails, fix the code, not the test.
   - Before reporting a task done, run the checks and paste the output.
3. Optional hook proposal: a PreToolUse check that denies edits to test files the
   current plan marks as fixed. For example, a `locked_tests:` front-matter key read
   by `governance_gate.sh`. Keep it fast and limited to the file being edited, as the
   playbook advises.
4. README: how to run parallel sessions. Each worktree is its own checkout with its
   own `docs/exec-plans/active/`, so SCOPE-001's "exactly one active plan" check holds
   per worktree. Confirm this rather than assuming it.
   The sandbox makes `.git/worktrees` read-only, so the owner runs
   `git worktree add` or `claude --worktree <name>`.

**Owner decisions.** Whether to build the locked-test hook now, or wait until the
evidence review shows an agent editing a test to make it pass.

## Stage 4: coding-agent evals in CI (play 09)

**Why.** Evals are the playbook's replacement for stage-gate QA. Collect 20 to 50 real
tasks, each a prompt plus checks. Run them in CI on a schedule and whenever the agent
setup changes, and gate those changes on the pass rate. Every incident becomes a
regression eval. The playbook's example workflow is `agent-evals.yml`. It triggers on
`CLAUDE.md` and `.claude/**` and a nightly cron, and runs `claude -p` with a narrow
`--allowedTools` and `--output-format json` over `evals/*.json`, then a check script.

**What exists.** Nothing for the coding agent. Phase A04 in
`docs/agent_governance_implementation.md` plans evals for the **product agent**
(`tests/integration/evals/`, `.github/workflows/evals.yml`, MODEL-001). Don't reuse
those names. Use `evals/` at the root, or `tests/agent_evals/`, and
`.github/workflows/agent-evals.yml`, so the two never collide.

**Build.**
1. An eval format and check script, run from Python rather than shell, to match the
   repo.
2. Tasks taken from this repo's own history. Completed plans 0001 to 0017 are real
   tasks. The richest checks are governance behaviour:
   - It writes a plan before editing.
   - It refuses to edit a protected path, and writes a proposal instead.
   - Its edits stay inside `scope_paths`.
   - Its commits carry correct trailers.
   - It doesn't edit a failing test.
   - Its checks pass at the end.
3. A runner that works on a throwaway clone with the repo's hooks active. The evals
   test the hooks plus the instructions, not the model alone.
4. `proposals/<ID>/.github/workflows/agent-evals.yml`. It triggers on `AGENTS.md`,
   `CLAUDE.md`, `app/AGENTS.md`, `.claude/**` and `governance/**`, plus a schedule.
5. A pass-rate floor, perhaps in `governance/thresholds.yaml` through a proposal.

**Owner decisions.**
- **COST-001:** the run cost (tasks × runs × triggers) and whether to approve it.
- **DEP-001:** pinning `@anthropic-ai/claude-code` from npm in CI.
- Which model CI's Claude Code runs on. It should be added to
  `governance/allowlists/models.yaml`.
- Whether the gate is advisory, like the other workflows, until branch protection
  exists.

**Depends on.** Stage 3's rules, so the evals can check them. Stage 2 is independent.

## Stage 5: policy skills, starting with security (plays 05, 02)

**Why.** The playbook writes knowledge that should be applied the same way every time
as skills: `.claude/skills/<name>/SKILL.md`, whose frontmatter says when it triggers.
Specs are checked against those skills during design. Its example is a
`secure-api-review` skill that runs a check script. "A skill is a control, though an
advisory one", so a deterministic check should back each skill where possible. A
policy change needs the policy owner's sign-off before the skill changes.

**What exists.**
- One skill: [adk-review](../../.claude/skills/adk-review/SKILL.md). Use it as the
  house style.
- [docs/SECURITY.md](../SECURITY.md) is a release checklist (operational readiness
  review), not coding guidance.
- The security policy an agent needs at design time is spread across
  `governance/rules.yaml` (SEC-001, SEC-002, DATA-001, DEP-001, TOOL-001, FS-001 and
  SBX-001), `governance/allowlists/` and the tech-debt tracker.

**Build.**
1. A `security-review` skill drawn from those sources. It cites rule IDs, and it
   triggers on specs and diffs that touch tools, dependencies, data flows, telemetry
   exporters or credentials. Point it at the deterministic checks that already exist
   (gitleaks, osv-scanner, Bandit through ruff, the tool-policy tests) instead of
   repeating them.
2. The `/intent` and `/spec` commands that plan 0017 deferred. They write from the
   templates, and the spec one ends with the playbook's prompt to "describe clearly
   any areas of concern, especially where you cannot satisfy contradicting policies".
3. Update the spec template's "Policies checked" section to name the skills.
4. A way to test that each skill triggers. The skill-creator skill can run trigger
   evals; stage 4's runner could host them.

**Owner decisions.** Which policies come next: data handling and dependencies are the
obvious next two. Also who signs off a skill change. It's the owner today, but treat
`.claude/skills/` like a policy file in review.

## Stage 6: closing the loop (play 13)

**Why.** In the playbook, live signals start new work:
- Pick one metric with a stable baseline.
- Detect breaches with a deterministic, version-controlled, unit-tested script, using
  mean and standard deviation, Western Electric rules or similar.
- Tier the response in `bands.yaml`: 1σ log, 2σ read-only diagnosis, 3σ propose a fix
  or rollback.
- Write the diagnosis as an `intent.md`.
- Triage it: fix now, schedule, or dismiss. Add an eval once it's fixed.

**What exists.**
- `ops/observability/` (collector, Tempo, Prometheus, Grafana) and
  `ops/observability/alerts.yaml`, which has fixed thresholds such as
  `BlockedToolCallsRising` and `SessionTokenSpike`.
- The sprint evidence review, which produces rule-change proposals rather than
  intents.

**Blocked because** the product agent has no real workload yet. The README's step 4
(phases A01 to A06) hasn't run, so no product metric has a baseline.

**An option that isn't blocked.** The playbook's own example metrics include CI test
failure rate and PR cycle time. Both exist now, in the GitHub Actions history and PR
metadata. A first version could watch a build-side metric, then move to product
metrics after A05. Ask the owner which.

**Build, when unblocked.**
1. `ops/observability/bands.yaml`.
2. A detection script in `scripts/` with unit tests.
3. A scheduled workflow (by proposal) that runs it. At 2σ or above it runs
   `claude -p` read-only to diagnose, and writes an intent to
   `docs/exec-plans/intent/` as a PR.
4. The evidence review then also triages those intents.

Needs a COST-001 approval for the diagnosis calls.

## Gaps not assigned to a stage

These came out of the gap analysis but aren't in stages 2 to 6. Fold them into a
stage when they fit, or give them their own plan.

- **Play 12, CI integration.** Run `claude -p` read-only on CI failures to write a
  `triage.md`, and draft changelogs. Paid.
- **Play 14, scheduled scans.** A full-repo security scan on a schedule, not just
  per-diff gitleaks and osv-scanner.
- **Play 11, deploy approval gates.** Not applicable until there's a deploy target.
  Then add a PreToolUse hook that requires a release approval, and make rollback a
  single rehearsed command.
- **Managed settings.** Enforce the sandbox and deny rules through managed settings,
  add `disableBypassPermissionsMode`, and add a network allowlist for the sandbox.
- **Auto mode policy.** Write down when auto mode is acceptable: a tight spec, a small
  blast radius, and tested code.
- **Separate commits per gate.** Plan 0017 commits the intent, spec and plan together,
  because `check_trailers.sh` needs a `Plan:` trailer that names an existing plan.
- **Checking the chain.** Check in CI that every new plan links an accepted intent and
  spec, or gives an exemption reason. Plan 0017's tech-debt entries cover this and the
  plan–diff sync check.
