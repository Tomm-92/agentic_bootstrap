# Spec 0025: spec-security skill, and /intent and /spec

Intent: [0025-spec-security-skill](../intent/0025-spec-security-skill.md)
Status: accepted
Accepted by: Thomas Wilkinson, 2026-11-25

<!-- Copy to docs/execution-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

1. **One checklist.** `.claude/skills/spec-security/checklist.md` is the only file that
   says what a security review checks. No other file lists security checks.
2. The checklist covers SEC-001, SEC-002, DATA-001, DEP-001, TOOL-001, FS-001 and
   SBX-001. For each rule it gives the rule ID, what to look for in a spec, what to
   look for in a diff, the deterministic checks that already enforce it, and any
   `planned` control or tracker gap that leaves part of it unenforced. It quotes no
   rule text from `governance/rules.yaml`.
3. **`spec-security` reviews specs only.** Given a spec path, or the newest spec when
   none is given, it applies the checklist's spec column and reports findings, each
   citing a rule ID. It never reads a diff, and its description says so.
4. **The CI review reads the same checklist.** `scripts/ai_review.py` loads the
   checklist at the base commit as one more instructions file. `REVIEW.md`'s Security
   pass says to apply the checklist's diff column and keeps no list of its own.
5. **The built-in `/security-review` is off.** `.claude/settings.json` sets
   `"skillOverrides": {"security-review": "off"}`.
6. **`/intent`** writes `docs/execution-plans/intent/<ID>-<name>.md` from the template,
   under the next free ID, with `Status: draft` and the placeholder `Accepted by:`.
7. **`/spec`** writes `docs/execution-plans/spec/<ID>-<name>.md` from the template for an
   accepted intent. It runs `spec-security` on the draft and puts the findings in
   "Policies checked". It ends by filling in "Concerns", with the playbook's prompt to
   describe any area where contradicting policies can't both be met.
8. Claude can start all three skills itself. `/intent` and `/spec` refuse to go on when
   their input isn't accepted: `/spec` needs an intent with `Status: accepted` and a
   filled-in `Accepted by:`.
9. **A free test** fails if a skill has no `name` or `description` frontmatter, if the
   checklist cites a rule ID missing from `governance/rules.yaml`, or if a skill or the
   checklist names a repo path that doesn't exist.
10. The spec template's "Policies checked" section names `spec-security`. The README's
    review commands show which reviewer covers which stage. The handover marks stage 5
    done.

## Design

### Files

| File | Change |
| --- | --- |
| `proposals/0025/.claude/skills/spec-security/SKILL.md` | New |
| `proposals/0025/.claude/skills/spec-security/checklist.md` | New |
| `proposals/0025/.claude/skills/intent/SKILL.md` | New |
| `proposals/0025/.claude/skills/spec/SKILL.md` | New |
| `proposals/0025/.claude/settings.json` | Current file plus `skillOverrides` |
| `scripts/ai_review.py` | One `INSTRUCTIONS` entry, and a line in `SYSTEM` |
| `tests/governance/test_ai_review.py` | The fake base commit gains the checklist |
| `tests/governance/test_skills.py` | New (requirement 9) |
| `REVIEW.md` | Security pass and "Do not report" point to the checklist |
| `docs/execution-plans/templates/spec.md` | "Policies checked" names `spec-security` |
| `README.md`, `docs/execution-plans/handover.md` | Review commands, stage 5 status |

### The checklist

There's one section per rule, in house style:

```markdown
## DATA-001
- Spec: does any new exporter, endpoint or service receive prompts, sessions,
  traces or outputs? Is it in `governance/allowlists/services.yaml`?
- Diff: new network calls or exporter config that send that data elsewhere.
- Enforced by: `tests/governance/test_observability.py` (collector exporters).
- Not yet enforced: sandbox TTY and exec access (A02, planned); ADK span content
  (`docs/bootstrapper_tech_debt_tracker.md`).
```

A closing "Already enforced, don't report" list holds the deterministic security checks:
gitleaks, pip-audit and osv-scanner in `.github/workflows/governance.yml`, Bandit
through ruff's `S` rules, `tests/unittests/test_tool_policy.py` and the exporter tests.
`REVIEW.md`'s "Do not report" keeps its non-security items and drops gitleaks, pip-audit
and osv-scanner, which now live only in the checklist (requirement 1).

### Skills

All three follow `.claude/skills/adk-review/SKILL.md`: frontmatter, then numbered
steps. They don't set `disable-model-invocation`, so Claude can start them itself
(intent, "Claude starts them itself").

- **`spec-security`.** Its description: *"Check a spec, not code, against this repo's
  security policy before it's accepted. Use when writing or reviewing a spec under
  docs/execution-plans/spec/, or when /spec runs it. Diffs are reviewed by the CI review,
  not this skill."* Steps: read the spec, read `checklist.md`, then for each rule whose
  subject the spec touches, report `rule ID: finding: fix`, or "no finding". It works in
  this session and starts no subagents, like `adk-review`.
- **`intent`.** Its description says to use it whenever an intent is drafted, and that
  the README's small changes skip it. Steps: find the highest ID in
  `docs/execution-plans/`, ask for the name if it isn't given, copy the template, fill it
  from the conversation, and leave the status lines for the owner.
- **`spec`.** Its description says to use it whenever a spec is drafted from an
  accepted intent. Steps: check the intent's two header lines, copy the template, write
  the requirements and design, run `spec-security` and paste its findings into "Policies
  checked", then write "Concerns".

### The CI review

Add `'security': '.claude/skills/spec-security/checklist.md'` to `INSTRUCTIONS`. Name
`<security>` in `SYSTEM` as what the Security pass checks against. The workflow checks
out the base commit and runs the base's script, so the new entry takes effect only
after it merges, when the checklist is already on the base branch. No PR sees the
script ask for a file that isn't there yet.

### Rejected options

- **A permission deny rule (`Skill(security-review)`) instead of `skillOverrides`.**
  The docs describe it only for the model's own calls, not a typed `/security-review`.
- **`disableBundledSkills`.** It also removes `/code-review` and `/simplify`, which the
  README uses.
- **The checklist in `governance/`.** Every wording change would change the governance
  hash and end every open session (GOV-006).
- **The checklist copied into the CI review's prompt.** Two copies would drift apart.

## Out of scope

- A check that `spec-security` ran on each spec (intent question 3, "Checking the chain").
- Model-based trigger evals (stage 4, COST-001).
- Data handling and dependency policies beyond what the security rules already cover.
  Each gets its own plan.
- Any change to the product agent in `app/` or to the CI workflow files.

## Policies checked

`spec-security` doesn't exist yet, so this was checked by hand against the same
rules.

- **GOV-002:** the skills, checklist and settings go through `proposals/0025/`.
  `REVIEW.md`, `scripts/ai_review.py`, the tests and the docs aren't protected.
- **SEC-001, SEC-002:** no file reads `.env` or holds a credential. The CI review's API
  key handling doesn't change.
- **COST-001:** no new paid calls. The CI review makes one call per PR, as before, and
  its prompt grows by the checklist's length.
- **MODEL-001, REV-001:** the reviewer model and how it's chosen don't change.
- **SCOPE-002:** the plan's `scope_paths` cover `proposals/0025/`, `.claude/skills/` and
  `.claude/settings.json` (the owner's apply commit), `scripts/ai_review.py`, `tests/`,
  `REVIEW.md`, `README.md` and `docs/execution-plans/`.
- **DATA-001, DEP-001, TOOL-001, FS-001, SBX-001:** the change adds no service,
  dependency, tool or product-agent write.
- `docs/records/security.md`: no data, secrets or access change.
- `app/AGENTS.md`: not applicable, nothing in `app/` changes.

## Concerns

- **Older Claude Code versions ignore `skillOverrides`.** Version 2.1.19 has no such
  setting, and on it `/security-review` stays available. The owner's terminal CLI and
  the VS Code extension are both on 2.1.330, which supports it (2026-11-25). Any other
  machine or CI job that runs Claude Code needs a version that knows the setting.
- **Every checklist change goes through the owner, by design.** Claude Code's sandbox
  blocks agent writes to `.claude/skills/`, so a change, however small, is written to
  `proposals/<plan ID>/` and the owner copies it in and commits it. This enforces the
  intent's decision that the owner signs off policy changes, and stops an agent
  weakening the checklist that reviews its own work. The cost is one owner step per
  change, which is acceptable because policy wording should change rarely. The
  checklist was kept here rather than moved to a writable path such as `docs/`, where
  sign-off would rest only on the owner spotting the change in PR review.
- **Skills Claude starts itself are advisory.** Claude may still draft a spec by hand.
  The check for that is deferred (intent question 3).
- **The test reads `.claude/skills/`,** which only exists after the owner applies the
  proposal. The plan orders the work so the test lands after the owner's apply commit.
