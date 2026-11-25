# Intent 0026: decide on the gaps not assigned to a stage

Author: Claude, drafted for the owner
Status: accepted
Accepted by: Tom Wilkinson, 2026-11-25

<!-- Copy to docs/execution-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

<!-- Revised 2026-11-25 after the owner's first acceptance. The owner wants no new
Linear issues under milestone 1, and everything that can be resolved here resolved in
this plan. Needs accepting again. -->

## Problem

The 19 Nov 2026 gap analysis against the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook)
left seven gaps outside stages 2 to 6. They're listed under "Gaps not assigned to a
stage" in `docs/execution-plans/handover.md` (Linear TMW-19). The list says only "fold
them into a stage when they fit, or give them their own plan". Nobody has decided which.
Play 11, deploy approval gates, is tracked separately as TMW-21 and isn't part of this.

This hurts the owner and the next sessions. A session picking up stage 4 can't tell
which of these it should absorb. Gaps nobody owns don't get built, and they also don't
reach the tech-debt trackers, which is where the repo records what it has chosen not to
do yet.

## Proposed outcome

Every gap is resolved by this plan, found not to be needed, or handed to stage 4,
which already has its own section and Linear issue. No new tech-debt tracker row and no
new Linear issue is created. A tracker row would need both a gap worth resolving now
and a reason it can't be resolved in this plan, and none of these gaps has both. The
two existing rows this plan closes (the chain check and per-gate commits) are removed. The handover's section is replaced by
a table of the decisions.

| Gap | Decision | Why |
| --- | --- | --- |
| Play 14: scheduled full-repo scans | Build here | Free and small. The per-PR jobs in `governance.yml` scan only the diff for secrets, and scan the lockfiles only when a PR runs. A weekly run of gitleaks over the full history, and of pip-audit and osv-scanner over the lockfiles, catches two things the PR jobs miss: a leak older than the scan, and a vulnerability published after the last PR. Goes in as a `.github/` proposal. |
| Separate commits per gate | Build here | `check_trailers.sh` accepts a `Plan:` trailer only if a plan with that ID exists, so the intent, spec and plan share one commit. Also accepting an intent or spec with that ID lets each gate be its own commit. The CI scope check already skips a commit whose plan doesn't exist yet. Goes in as a `.githooks/` proposal. |
| Checking the chain | Build here | A CI check that every newly added plan links an accepted intent and an accepted spec, and that the spec's "Policies checked" names `spec-security`. A plan that gives `Intent: none (<reason>)` passes instead. This closes the tracker row and intent 0025's question 3. It can't tell who set `Status: accepted`, because the owner's commits and the agent's share an author, so that part of the row stays open. |
| `disableBypassPermissionsMode` | Build here | Bypass mode still applies deny rules, ask prompts and the sandbox's write limits, and `branch_guard.sh` already refuses paid-model commands outside manual mode. What bypass mode loosens is the network: a sandboxed command can reach any host without a prompt. The setting is allowed in project settings, so every clone gets it. The docs don't say whether a command-line flag overrides it, so the build tests that. |
| Sandbox network allowlist | Not needed, no tracker row | In project settings, `sandbox.network.allowedDomains` only stops the prompt for listed hosts. Unlisted hosts already prompt in manual mode, and are refused in auto mode unless the auto mode reviewer approves them for one command. With bypass mode disabled, no mode reaches a host silently. Recorded only in the handover's decision table, so it isn't raised again. |
| Auto mode policy | Build here | A short written rule on when auto mode is acceptable: an accepted spec, a small blast radius and tested code. It must agree with plans 0021 and 0022. |
| Managed settings file | Build here only if the bypass flag wins | It adds no behaviour of its own. It only stops a local settings file or a command-line flag overriding the project settings. With one owner, that matters only if the command-line bypass flag overrides `disableBypassPermissionsMode`. The owner tests that. If the flag wins, this plan ships the managed file as a proposal and the owner installs it. If not, it isn't needed. |
| Play 12: CI failure triage | After stage 4, in stage 4's handover section | It needs Claude Code running in CI and a COST-001 approval, which stage 4 (TMW-17) brings. Stage 4's "Also revisit" paragraph gains a line for it. |
| Play 12: changelogs | Not needed, no tracker row | There are no releases to write them for. |
| Play 08: parallel sessions in worktrees | Not needed, no tracker row | The owner dropped it from stage 3 (intent 0019): every artifact goes through the owner, so more sessions mostly lengthen the review queue. The handover's decision table keeps the two blockers in case it's ever raised again: a new worktree has no `.venv`, and the sandbox makes `.git/worktrees` read-only. |

## Affected users and systems

- **The owner:** reviews and applies the proposals. They also run one check in their
  own terminal: whether the command-line bypass flag overrides the project setting.
- **Coding agents:** follow the auto mode policy, and can commit each gate on its own.
- **Proposals (GOV-002):**
  - `.github/workflows/`: a new scheduled workflow, and a chain-check step in
    `governance.yml`
  - `.githooks/check_trailers.sh`
  - `.claude/settings.json`
  - `AGENTS.md`: one line pointing to the auto mode policy
- **Unprotected files:**
  - a new `scripts/check_chain.py` and its tests
  - the README's "Development process" section
  - the handover and the tracker
  - `REVIEW.md`'s "Do not report" list, for the new CI check
- **Linear:** TMW-19 gets a comment with the decisions and is closed. Nothing is
  created.
- **Not affected:** the product agent in `app/`, and `governance/`.

## Constraints

- **GOV-002:** every protected file goes through `proposals/0026/`.
- **GOV-006:** one session. If the plan outgrows a session, the rest moves to a new
  plan, with no Linear issue.
- **COST-001:** no paid calls. The scheduled scans use no model.
- **DEP-001:** the scheduled workflow uses the same pinned gitleaks and osv-scanner
  releases as `governance.yml`, and adds no new tool.

## Open questions

1. **Where does the auto mode policy go?** Recommendation: the README's "Development
   process" section. It isn't protected, and it's where agents already read the
   process. `AGENTS.md` gets one line pointing to it, through a proposal.
2. **How often do the scheduled scans run?** Recommendation: weekly, plus a manual
   trigger. When a scheduled run fails, GitHub emails the owner. That's the only alert
   this repo has.
3. **What if the command-line bypass flag overrides `disableBypassPermissionsMode`?**
   Recommendation: keep the project setting anyway, since it still removes bypass from
   the mode switch inside a session. Add a managed settings file holding only that
   setting, as a proposal the owner installs. No tracker row.
4. **Does the chain check look at old plans?** Recommendation: no. It checks only the
   plans a pull request adds, because plans 0001 to 0016 predate the intent → spec →
   plan process. Moving a plan from `active/` to `completed/` doesn't count as adding
   it.
