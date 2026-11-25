# Security checklist

The one list of what a security review checks in this repo. `spec-security` applies the
Spec lines to a spec. The CI review (`scripts/ai_review.py`) applies the Diff lines to a
pull request, through `REVIEW.md`'s Security pass. Rule text lives in
`governance/rules.yaml`: read the rule there, not here. The owner signs off every change
to this file.

Cite the rule ID in every finding. Check a rule only when the change touches its subject.

## SEC-001

- Spec: does anything read, load, copy or log a `.env` file, or ask an agent to?
- Diff: code, scripts or config that open `.env`, or commit one.
- Enforced by: the session deny rule on `.env` in `.claude/settings.json`, and
  `.gitignore`.

## SEC-002

- Spec: where does each credential come from, and can it reach code, a commit, a log,
  a trace or the agent's output?
- Diff: hard-coded keys, tokens or passwords, and secrets written to output, logs or
  span attributes.
- Enforced by: gitleaks, for commits.
- Not yet enforced: the secrets stage of `verify.sh` for agent output (A02, planned).
  A same-repo PR that edits `.github/workflows/ai-review.yml` can reach the API key
  (`docs/bootstrapper_tech_debt_tracker.md`).

## DATA-001

- Spec: does any new exporter, endpoint or service receive prompts, sessions, traces or
  outputs? Is it in `governance/allowlists/services.yaml`? Does anyone get a shell into a
  sandbox?
- Diff: network calls, exporters or collector config that send that data to a service
  not on the allowlist.
- Enforced by: the collector exporter tests in `tests/governance/test_observability.py`.
- Not yet enforced: sandbox containers without TTY or exec access (A02, planned), and
  the data-handling sign-off in `docs/records/security.md` (planned). Session logs hold
  prompts unredacted, and ADK spans hold prompts and responses
  (`docs/bootstrapper_tech_debt_tracker.md`).

## DEP-001

- Spec: does it add a library, tool, action or service? Is the owner's approval
  recorded, and is it pinned in `requirements.txt` or `requirements-dev.lock`? Is the
  package name real?
- Diff: new entries in a manifest or lockfile, or a new install command in a script or
  workflow, without a range or pin.
- Enforced by: the owner's review of dependency manifests, and pip-audit and
  osv-scanner.
- Not yet enforced: the runtime allowlist and registry existence check, and
  confirmation for packages off `governance/allowlists/packages.yaml` (A01, planned).

## TOOL-001

- Spec: does it add or change a product-agent tool or target? Does each one have a tier
  in `governance/tools.yaml`?
- Diff: a tool registered in `app/` with no entry in `governance/tools.yaml`, or a
  change that weakens the default deny.
- Enforced by: the before-tool policy, tested in `tests/unittests/test_tool_policy.py`.

## FS-001

- Spec: where does the product agent write? Is every write under the profile's
  `output_root`, in the approved work item?
- Diff: writes that build a path outside that root, or skip the before-tool path check.
- Enforced by: the before-tool path check, tested in `tests/unittests/test_tool_policy.py`.
- Not yet enforced: a symlink created after the check can still escape (A02's sandbox,
  `docs/bootstrapper_tech_debt_tracker.md`).

## SBX-001

- Spec: does the product agent run or scan anything it generated? Where, with which
  credentials, and with what network access?
- Diff: generated content that is executed or scanned outside the sandbox, or a sandbox
  given credentials or open network access.
- Not yet enforced: the verification sandbox container (A02, planned). The session
  sandbox blocks `docker` (`docs/bootstrapper_tech_debt_tracker.md`).

## Already enforced, don't report

These run on every pull request, so no review repeats what they find:

- gitleaks, pip-audit and osv-scanner in `.github/workflows/governance.yml`
- Bandit, through ruff's `S` rules in `ruff.toml`
- `tests/unittests/test_tool_policy.py`
- `tests/governance/test_observability.py`
