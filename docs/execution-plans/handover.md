# Handover: adopting the AI-native SDLC playbook

The owner has made the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook)
this repo's default development process. A gap analysis (19 Nov 2026) compared its 15
"plays" with the repo and split the work into six stages, built one at a time. This
file hands the remaining three to the sessions that will build them.

Keep this file current. When a stage's plan completes, mark its row and correct
anything in its section that turned out to be wrong.

**Next:** stage 4 (Linear TMW-17), as plan 0027 unless a higher ID is taken by then. It
needs a COST-001 approval first. Plan 0026 resolved the gaps no stage covered (see
the end of this file). Play 12's CI failure triage follows stage 4. Stage 6 is still
blocked.

| Stage | What | Playbook plays | Status |
| --- | --- | --- | --- |
| 1 | Process docs: intent → spec → plan, plan mode by default | 01, 02, 03, 04 | Done (plan 0017) |
| 2 | PR review rubric | 10 | Done (plan 0018) |
| 3 | Verifier subagent, failing test first | 07, 08 | Done (plan 0019) |
| 4 | Coding-agent evals in CI | 09 | Not started, needs a COST-001 approval |
| 5 | Policy skills, starting with security | 05, 02 | Done (plan 0025) |
| 6 | Closing the loop: bands, detection, breach → intent | 13 | Blocked, see its section |

## How to pick up a stage

- **One stage, one plan, one session (GOV-006).** Take the next free plan ID. IDs
  aren't reserved per stage. 0013 is spoken for by the bootstrapper tech-debt tracker. Check
  `docs/execution-plans/` for the highest ID in use.
- **Follow plan 0017's process.** Read the README's "Development process" section
  first. Where it and this file disagree, the README wins.
  - Write an intent in `docs/execution-plans/intent/` from the template, using the stage's
    section below.
  - The owner accepts it, then you write the spec.
  - The owner accepts the spec, then you plan in plan mode.
  - Plan 0018 followed this end to end. Its intent, spec and plan are a worked
    example.
- **Acceptance is two header lines.** `Status: accepted` and `Accepted by:` are both
  the owner's to set. Check both before moving on, and ask if either is missing.
  Spec 0018's `Accepted by:` was still the placeholder when its plan was built. Since
  plan 0026, the edit gate refuses an agent edit that adds either line. Setting
  `Status: draft` is still allowed, for an accepted file whose content you revise.
- **The chain check runs on every pull request (plan 0026).** Each plan from 0026 on
  must link an accepted intent and an accepted spec whose "Policies checked" holds the
  `spec-security` report, or give `Intent: none (<reason>)`. Run
  `.venv/bin/python scripts/check_chain.py main..HEAD` before handing over.
- **Add trailers with `--trailer`, not a second `-m`.** Each `-m` is its own paragraph,
  and git reads only the last one as trailers, so
  `-m "Governance: ..." -m "Plan: ..."` fails `commit-msg`. Use
  `git commit -m "<subject>" --trailer "Governance: $(git rev-parse HEAD:governance)" --trailer "Plan: <ID>"`.
- **Protected paths go through proposals (GOV-002).** Most stages touch `AGENTS.md`,
  `.claude/settings.json`, `.claude/hooks/` or `.github/`. Write the new version to
  `proposals/<plan ID>/` at the same relative path. Each section lists the files it
  expects to touch.
- **Claude Code's own sandbox blocks writes to `.claude/skills/`** (and probably
  `.claude/agents/`) at the real path, even though the repo doesn't protect them.
  Write them to `proposals/<plan ID>/.claude/...` and let the owner copy them in.
  Check this at the start rather than assuming.
- **Write proposals with the Write tool.** In plan 0026, a shell `cp` of protected
  files into `proposals/0026/` was declined. Writing each file in full and checking it
  with `diff` against the real path worked.
- **Test a proposed hook before the owner applies it.** `tests/governance/test_hooks.py`
  reads `HOOKS_DIR`, so `HOOKS_DIR=proposals/<ID>/.claude/hooks .venv/bin/pytest
  tests/governance/test_hooks.py -k "not guard"` runs the gate tests against the
  proposal. New cases can go in a throwaway file under `proposals/<ID>/`: the gate
  refuses writes outside the repo, including the scratchpad. Delete it before
  committing, then add the real tests after the apply commit.
- **Plan mode's own plan file** (`~/.claude/plans/*.md`) is exempt from the
  governance gate, so a plan can be drafted in plan mode before any plan is active.
  On approval, copy it to `docs/execution-plans/plan/active/` and commit it. Since plan
  0026, the intent and spec can each be committed at their own gate, with `Plan: <ID>`
  naming them.
- **A protected file the owner edits during a plan must be in its `scope_paths`.**
  `scripts/check_scope.py` reads the plan's scope as of each commit, and the owner's
  commits are checked too. Add the path to the plan before the owner commits the
  edit. In plan 0018, the owner's `governance_gate.sh` fix failed the check, and the
  commit had to be amended.
- **Finish every edit before moving the plan to `completed/`.** With no active plan,
  the gate denies edits outside `docs/execution-plans/`. In plan 0019, a last fix to
  `proposals/0019/` was blocked after the move. Stage the plan's last edits before
  `git mv`: it stages the rename, not unstaged changes, so in plan 0026 they needed a
  second commit.
- **A new subagent loads only in a new session.** After the owner copies a file into
  `.claude/agents/`, check it in a fresh session: it appears among the available agent
  types. Claude Code no longer has an `/agents` command to list them.
- **A stage that adds a CI check also updates `REVIEW.md`.** Its "Do not report"
  section lists what CI already enforces, so the reviewer doesn't repeat it.
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

**As built (plan 0018).** The playbook's design, with these departures from the
original notes:
- The evidence review is now `docs/records/evidence_review.md`, and lists PR review findings
  among its inputs.
- `REVIEW.md` is at the repo root. Its design principles are `ARCHITECTURE.md`, the
  "Code style" section of `AGENTS.md`, and `app/AGENTS.md`.
- `scripts/ai_review.py` reads the rubric and design principles at the base commit,
  as instructions, and the plan, intent, spec and diff at the head commit, as data.
  `proposals/0018/.github/workflows/ai-review.yml` checks out the base commit, so the
  job holding the API key never runs PR code.
- The review ends with `Tally: important=<n> nit=<n>`, or `Tally: unavailable` when
  the model's last line isn't one. Nothing gates on it yet.
- The `@claude` fix-on-comment loop is deferred, with a row in the bootstrapper tech-debt tracker.
  Revisit it with stage 4.

## Stage 3: verifier subagent, failing test first (plays 07, 08)

**Why.**
- The playbook uses scoped subagents in `.claude/agents/*.md`, for example a
  `verifier` that runs the checks and reports but never fixes.
- For bug fixes, it wants a failing test written and committed first, then the fix,
  with a hook stopping the agent editing that test.
- "Done" means the check output has been pasted, not just claimed.

**As built (plan 0019).** The playbook's design, with these departures from the
original notes:
- `.claude/agents/verifier.md` has Bash and Read only, and its description tells
  Claude to call it proactively before reporting a task done. It removes the Stop
  hook's fingerprint and runs the hook exactly as CI does, because run as is the hook
  can skip the checks. It runs the scripted `local_session` only for `app/` changes,
  so scripted sessions don't fill the evidence log. The sandbox blocks
  `.claude/agents/`, so it went in by proposal.
- A bug fix starts with a reproducing test marked
  `@pytest.mark.xfail(strict=True, ...)`, and the fix commit removes only the marker.
  A plain failing test would block the Stop hook and fail CI on that commit.
- A test changes only when the plan changes the behaviour it checks, or for a stated
  reason, and always in its own commit with that reason. These rules are in
  `AGENTS.md`'s Tests section.
- No locked-test hook. The owner chose to wait until the evidence review shows an
  agent editing a test to make it pass.
- Parallel sessions in git worktrees were dropped. See "Gaps not assigned to a stage".

## Stage 4: coding-agent evals in CI (play 09)

**Why.** Evals are the playbook's replacement for stage-gate QA. Collect 20 to 50 real
tasks, each a prompt plus checks. Run them in CI on a schedule and whenever the agent
setup changes, and gate those changes on the pass rate. Every incident becomes a
regression eval. The playbook's example workflow is `agent-evals.yml`. It triggers on
`CLAUDE.md` and `.claude/**` and a nightly cron, and runs `claude -p` with a narrow
`--allowedTools` and `--output-format json` over `evals/*.json`, then a check script.

**What exists.** Nothing for the coding agent. Phase A04 in
`docs/bootstrap-implementation/agent_governance.md` plans evals for the **product agent**
(`tests/integration/evals/`, `.github/workflows/evals.yml`, MODEL-001). Don't reuse
those names. Use `evals/` at the root, or `tests/agent_evals/`, and
`.github/workflows/agent-evals.yml`, so the two never collide.

**Build.**
1. An eval format and check script, run from Python rather than shell, to match the
   repo.
2. Tasks taken from this repo's own history. Completed plans 0001 to 0026 are real
   tasks. The richest checks are governance behaviour:
   - It writes a plan before editing.
   - It refuses to edit a protected path, and writes a proposal instead.
   - Its edits stay inside `scope_paths`.
   - Its commits carry correct trailers.
   - A bug fix starts with a strict `xfail` test, and the fix commit removes only its
     marker.
   - A test change comes in its own commit, with a reason.
   - It never accepts its own intent or spec, and its plan passes the chain check.
   - It adds a tech-debt row only when the gap is worth resolving now and can't be
     resolved in the plan (`AGENTS.md`).
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

**Also revisit** the tech-debt row for the `@claude` fix-on-comment loop, which plan
0018 deferred. Running Claude Code in CI under the repo's hooks is the question both
need answered. A non-interactive start also needs its own `--permission-mode`,
because the default mode is `plan` (bootstrapper tech-debt tracker).

**Permission modes in CI** (plan 0026). `.claude/settings.json` disables bypass mode,
and the owner checked that neither `--dangerously-skip-permissions` nor
`--permission-mode bypassPermissions` gets past it. So CI's `claude -p` can't run in
bypass mode under the repo's settings, and shouldn't. Use `dontAsk` with a narrow
`--allowedTools`, as the playbook's example does, or `acceptEdits`. `branch_guard.sh`
refuses paid-model commands outside manual (`default`) mode, which matters if an eval
task would run one.

**Claude Code on the owner's machine** is at `~/.local/bin/claude`, version 2.1.332 on
2026-11-25. That folder isn't on the shell's PATH, so give the full path in any
command the owner runs.

**Then add play 12's CI failure triage** (plan 0026): `claude -p`, read-only, on a CI
failure, writing a `triage.md`. It reuses this stage's runner, pin and model, and needs
its own COST-001 approval for runs triggered by failures.

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
- [docs/records/security.md](../records/security.md) is a release checklist (operational readiness
  review), not coding guidance.
- The security policy an agent needs at design time is spread across
  `governance/rules.yaml` (SEC-001, SEC-002, DATA-001, DEP-001, TOOL-001, FS-001 and
  SBX-001), `governance/allowlists/` and the bootstrapper tech-debt tracker.

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

**As built (plan 0025).** The owner ruled out any overlap between reviewers, which
changed the design:
- **One checklist.** `.claude/skills/spec-security/checklist.md` is the only list of
  security checks, with Spec and Diff lines per rule. The skill is `spec-security`, not
  `security-review`, which is Claude Code's built-in name.
- **One reviewer per stage.** `spec-security` checks specs only. The CI review applies
  the checklist to diffs: `scripts/ai_review.py` loads it at the base commit, and
  `REVIEW.md`'s Security pass points to it.
- **The built-in `/security-review` is off,** by `skillOverrides` in
  `.claude/settings.json`. The setting needs a recent Claude Code: 2.1.19 lacks it, and
  2.1.330 has it.
- **`/intent` and `/spec` serve the whole project,** and Claude starts them itself.
  `/spec` runs `spec-security`.
- **Triggering is tested structurally** in `tests/governance/test_skills.py`. Model-based
  trigger evals wait for stage 4. A check that `spec-security` ran on each spec waits
  for "Checking the chain".
- **Owner decisions taken:** the owner signs off every checklist and skill change, which
  the sandbox enforces because agents can't write `.claude/skills/`. Data handling and
  dependencies come next, each in its own plan, adding to a checklist rather than a new
  reviewer.

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
- `observability/` (collector, Tempo, Prometheus, Grafana) and
  `observability/alerts.yaml`, which has fixed thresholds such as
  `BlockedToolCallsRising` and `SessionTokenSpike`.
- The sprint evidence review, which produces rule-change proposals rather than
  intents.

**Blocked because** the product agent has no real workload yet. The README's step 4
(phases A01 to A05) hasn't run, so no product metric has a baseline.

**An option that isn't blocked.** The playbook's own example metrics include CI test
failure rate and PR cycle time. Both exist now, in the GitHub Actions history and PR
metadata. A first version could watch a build-side metric, then move to product
metrics after A05. Ask the owner which.

**Build, when unblocked.**
1. `observability/bands.yaml`.
2. A detection script in `scripts/` with unit tests.
3. A scheduled workflow (by proposal) that runs it. At 2σ or above it runs
   `claude -p` read-only to diagnose, and writes an intent to
   `docs/execution-plans/intent/` as a PR.
4. The evidence review then also triages those intents.

Needs a COST-001 approval for the diagnosis calls.

## Gaps not assigned to a stage

Decided in plan 0026 (Linear TMW-19, intent 0026). None became a tech-debt row or a new
Linear issue. Play 11, deploy approval gates, is TMW-21.

| Gap | Result | Why |
| --- | --- | --- |
| Play 14: scheduled full-repo scans | Built: `.github/workflows/scheduled-scans.yml` | Weekly, plus a manual trigger. gitleaks over the full history, redacted, and pip-audit and osv-scanner over the lockfiles. The PR jobs miss a leak older than the scan and a vulnerability published since the last PR. |
| Separate commits per gate | Built: `check_trailers.sh` | A `Plan: <ID>` trailer may name an intent or spec, so each gate is its own commit. |
| Checking the chain | Built: `scripts/check_chain.py` in `governance.yml` | Each plan a PR adds, from 0026 on, links an accepted intent and an accepted spec carrying the `spec-security` report, or gives `Intent: none (<reason>)`. Earlier plans predate the chain or the report. |
| Agents accepting their own intent or spec | Built: `governance_gate.sh` | CI can't tell the owner's commits from the agent's, so the session gate refuses an edit that adds an acceptance line. A shell command can still write one (tracker, shell-write row). |
| Bypass mode | Built: `disableBypassPermissionsMode` in `.claude/settings.json` | Bypass mode keeps deny rules, ask prompts and the sandbox's write limits, but lets a sandboxed command reach any host without a prompt. |
| Managed settings file | Not needed | It adds no behaviour of its own, and with one owner it mattered only if a command-line flag beat the project setting. Neither `--dangerously-skip-permissions` nor `--permission-mode bypassPermissions` reached bypass mode on Claude Code 2.1.332 (plan 0026, Proof). |
| Sandbox network allowlist | Not needed | In project settings it only removes the prompt for listed hosts. Unlisted hosts prompt in manual mode and are refused in auto mode. Refusing them everywhere needs `strictAllowlist`, which the repo can't set. |
| Auto mode policy | Built: README, "When to use auto mode" | An accepted spec or an exempt small change, inside `scope_paths`, with tests covering the code. |
| Play 12: CI failure triage | After stage 4, noted in its section | Needs Claude Code in CI and a COST-001 approval. |
| Play 12: changelogs | Not needed | There are no releases. |
| Play 08: parallel sessions in worktrees | Not needed | The owner reviews every artifact, so more sessions mostly lengthen the queue (intent 0019). If it's ever raised again: a new worktree has no `.venv`, and the sandbox makes `.git/worktrees` read-only, so the owner creates worktrees. |
