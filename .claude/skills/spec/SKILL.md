---
name: spec
description: Draft a spec from an accepted intent, and check it against the security policy. Use whenever a spec is drafted for a change to this repo, by the owner or an agent.
argument-hint: "[intent file or ID; default: the newest intent]"
---

Draft a spec for the owner to accept. Never set `Status: accepted` or fill in
`Accepted by:`. Only the owner does.

## 1. The intent

Use the intent `$ARGUMENTS` names, or the newest one in `docs/execution-plans/intent/`.
Stop and ask the owner if its header doesn't say `Status: accepted`, or if `Accepted by:`
is still the placeholder.

## 2. Write it

Copy `docs/execution-plans/templates/spec.md` to
`docs/execution-plans/spec/<ID>-<name>.md`, with the intent's ID and name. Write
numbered, testable requirements and the design, including the options rejected and why.
Settle every open question in the intent, or carry it into Concerns.

## 3. Policies checked

Run the `spec-security` skill on the draft, and paste its report into "Policies
checked". Add the other rule IDs that apply from `governance/rules.yaml`, and say how
the design meets each.

## 4. Concerns

Describe clearly any areas of concern, especially where you cannot satisfy
contradicting policies.

## 5. Hand over

Give the owner the path and the concerns. Don't plan until the owner accepts the spec.
