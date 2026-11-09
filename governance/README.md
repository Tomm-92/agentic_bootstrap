# Governance

**Owner:** `Tomm-92`.

## What each file holds

| File | Holds |
| --- | --- |
| `profile.yaml` | What this project's product agent is. Rules refer to its keys as `<profile.key>`. |
| `rules.yaml` | The canonical rules for coding agents (build) and the product agent (runtime). |
| `thresholds.yaml` | Numeric limits enforced in code: token budget, retention, eval floors, severity gate. |
| `tools.yaml` | Every product-agent tool, with its tier and the arguments holding a path or target. |
| `allowlists/models.yaml` | The exact model IDs allowed, and what each is used for. |
| `allowlists/packages.yaml` | Packages outputs may depend on without further approval. |
| `allowlists/services.yaml` | The only external services that may receive data, or that the agent may act on. |

## Which rules are in effect

The rules in effect are those committed at `HEAD`, identified by the governance hash:
`git rev-parse HEAD:governance`. Uncommitted edits are never in effect. Every commit
records the hash in a `Governance:` trailer, and every product-agent session event
carries it.

## Rule format

| Field | Allowed values |
| --- | --- |
| `id` | A unique ID, such as `GOV-001` |
| `applies_to` | A list from `build`, `runtime` |
| `rule` | "[subject] needs [constraint]" |
| `because` | The consequence of not having the rule; never empty |
| `tier` | `free` (agent acts), `confirm` (human approves each time), `deny` (never) |
| `kind` | `safety` (permanent), `capability` (review when the model changes) |
| `controls` | A list of controls |

Each control has exactly these fields:

| Field | Allowed values |
| --- | --- |
| `type` | `D` deterministic, `ND` model judgement, `H` human |
| `at` | Where it acts, such as `session`, `commit`, `ci`, `merge`, `runtime`, `review` |
| `by` | What enforces it |
| `status` | `active` (built and working), `planned` |

Every `deny` rule has a `D` control, and every `confirm` rule an `H` control.
`tests/governance/test_rules.py` checks this.

## Change process

1. An agent drafts the change under `proposals/<plan ID>/`, at the same relative path.
2. The owner reviews and commits it. Agents never edit `governance/`.
3. Relaxing a rule gets the most scrutiny: lowering a tier, removing a control or
   widening an allowlist is higher risk than most features.
4. Only the owner moves a control to `active`, in the change that makes it real.
