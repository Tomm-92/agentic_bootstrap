# Intent 0025: spec-security skill, and /intent and /spec

Author: Claude, drafted for the owner
Status: accepted
Accepted by: Thomas Wilkinson, 2026-11-25

<!-- Copy to docs/execution-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

## Problem

Plays 05 and 02 of the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook)
are stage 5 in `docs/execution-plans/handover.md` (Linear TMW-18). Three things are wrong
or missing.

- **Specs aren't checked against security policy.** The policy an agent needs at
  design time is spread across `governance/rules.yaml` (SEC-001, SEC-002, DATA-001,
  DEP-001, TOOL-001, FS-001 and SBX-001), `governance/allowlists/` and the two tech-debt
  trackers. Some of it is enforced only by controls still marked `planned`. A spec's
  "Policies checked" section is filled in from memory, so the same spec could be
  checked differently each time. A policy conflict is cheapest to fix before code is
  written.
- **Diffs have two security reviewers.** The CI review (`scripts/ai_review.py`) reviews
  every pull request against the Security and Compliance passes in `REVIEW.md`, with
  this repo's rules. Claude Code's built-in `/security-review` reviews the same diffs
  for the same kind of problem, without those rules. It comes with Claude Code, so it's
  available here even though nothing in the repo uses it, and the model can start it
  on its own.
- **`/intent` and `/spec` don't exist.** Plan 0017 deferred them to this stage. Each
  intent and spec is copied from its template by hand, for every change in the project,
  not only security ones. Nothing makes an agent check a spec against policy as it
  writes one.

This hurts the owner, who has to spot policy gaps in a spec unaided and may get two
overlapping security reviews of the same code. It also hurts agents, which have no
single place to read the security policy that applies to a change.

## Proposed outcome

Security is written down once, and each stage has exactly one reviewer:

| Stage | Reviewer | Checks against |
| --- | --- | --- |
| Spec | `spec-security` skill | The security checklist |
| Pull request | CI review (`scripts/ai_review.py`) | The same checklist, through `REVIEW.md`'s Security pass |
| Every edit and CI | Deterministic checks | Their own fixed rules |

- **One security checklist.** It holds the security policy in one place. It cites the
  rule IDs above, including their `planned` controls and the gaps the tech-debt
  trackers record, and points to `rules.yaml` rather than copying rule text. It names
  the deterministic checks that already enforce a rule, so neither reviewer repeats
  them:
  - gitleaks and osv-scanner in `.github/workflows/governance.yml`
  - Bandit through ruff's `S` rules
  - `tests/unittests/test_tool_policy.py`
  - the collector-exporter allowlist tests in `tests/governance/test_observability.py`
- **`spec-security` reviews specs only.** It applies the checklist to a spec and cites
  a rule ID for every finding. It triggers on specs that touch tools, dependencies,
  data flows, telemetry exporters or credentials. It never reviews code.
- **The CI review is the only diff reviewer.** `REVIEW.md`'s Security pass points to
  the checklist instead of keeping its own list, and `scripts/ai_review.py` loads the
  checklist at the base commit, as it loads `REVIEW.md`. A pull request can't rewrite
  the checklist that reviews it.
- **The built-in `/security-review` is switched off** in this repo by
  `"skillOverrides": {"security-review": "off"}` in `.claude/settings.json`, so neither
  the model nor the owner starts it here. It's a bundled skill, and `off` hides it from
  both. `disableBundledSkills` would also remove `/code-review` and `/simplify`, which
  the README uses, so it isn't used.
- **`/intent` and `/spec` serve the whole project.** They're used for every change that
  goes through the intent → spec → plan process, not only security ones. They're in
  this intent because `/spec` is how `spec-security` gets applied to every spec. Each
  writes a new intent or spec from its template under the next free ID. `/spec` runs
  `spec-security` to fill in "Policies checked", and ends with the playbook's prompt to
  "describe clearly any areas of concern, especially where you cannot satisfy
  contradicting policies".
- **Claude starts them itself.** Whenever an agent drafts an intent or spec, it uses
  the skill rather than copying the template by hand, and `/spec` always runs
  `spec-security`. The owner can also start them. Each skill's description says when it
  applies, and that small changes the README exempts skip the intent and spec. The
  owner's control is unchanged: only the owner sets `Status: accepted`.
- **The spec template's "Policies checked" section** names `spec-security`.
- **A free test** that the skills and the checklist are well formed and cite only
  things that exist.
- **The README's review commands** show which reviewer covers which stage. **The
  handover** shows stage 5 done, and corrects anything in its stage 5 section that
  turned out to be wrong.

## Affected users and systems

- **The owner:** can run `/intent` and `/spec`, reads policy findings in each spec,
  gets one security review per pull request, and applies the proposals.
- **Coding agents:** use `/intent` and `/spec` for every intent and spec they draft,
  and so `spec-security` on every spec.
- **`.claude/skills/`** (new skills and the checklist) and **`.claude/settings.json`**
  (the `skillOverrides` entry). Both go in `proposals/0025/`: the sandbox blocks the first, and
  GOV-002 protects the second.
- **`REVIEW.md`** (its Security pass) and **`scripts/ai_review.py`** (one more
  instructions file), with `tests/governance/test_ai_review.py`.
- **`docs/execution-plans/templates/spec.md`**, the README, the handover and a new
  test.
- **Not affected:** the product agent in `app/`, the runtime rules and the CI workflow
  files. `ai-review.yml` already checks out the whole base commit.

## Constraints

- **GOV-002:** skill files, the checklist and the settings change go through
  `proposals/0025/`.
- **COST-001:** the build makes no paid calls. The CI review's model calls are already
  approved, and loading one more file doesn't change how many it makes. Any trigger
  test that runs a real model waits for an approval.
- **No new overlap:** no reviewer re-checks what a deterministic check enforces, and
  no security rule is written in more than one file.
- **Concise:** follow `.claude/skills/adk-review/SKILL.md` as house style.

## Open questions

1. **Can Claude Code switch off a built-in skill?** Resolved, 2026-11-25. Claude Code
   2.1.330 registers `security-review` as a bundled skill. Its settings schema has
   `skillOverrides`, keyed by skill name, where `"off"` "hides it from both" the model
   and the `/` command. Older versions may not know the setting: the owner's terminal
   `claude` is 2.1.19. The spec checks that version too, and the plan verifies in a
   fresh session after the owner applies the proposal.
2. **Where does the checklist live?** Agreed by the owner. Recommendation:
   `.claude/skills/spec-security/checklist.md`, beside the skill that owns it. The
   skill reads it, and `scripts/ai_review.py` loads it at the base commit. Putting it
   in `governance/` would change the governance hash with every wording change.
3. **Should a check make sure `spec-security` ran?** Agreed by the owner. A skill Claude starts itself is
   likely to be used, not certain to be. A check could fail when a new spec's
   "Policies checked" section has no `spec-security` findings. This is part of the
   handover's "Checking the chain" gap. Recommendation: leave it out of 0025, and add
   it when that gap gets its own plan, so the chain is checked in one place rather
   than one artifact at a time.
4. **How is triggering tested?** Agreed by the owner. Recommendation: a free unit test now. It checks that
   each skill has frontmatter with a description, that every rule ID the checklist
   cites exists in `governance/rules.yaml`, and that every file or check it names
   exists. Model-based trigger evals wait for stage 4's runner and a COST-001 approval.
5. **Which policies come next, and who signs off a checklist or skill change?**
   Recommendation: the owner signs off, and `REVIEW.md` treats a change under
   `.claude/skills/` as a policy change. Data handling and dependencies are the next
   two, each with its own plan, and each adds to a checklist rather than a new
   reviewer.
