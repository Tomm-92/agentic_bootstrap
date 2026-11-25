---
name: intent
description: Draft a new intent from the template. Use whenever an intent is drafted for a change to this repo, by the owner or an agent. Not for small changes the README exempts (fixes that restore documented behaviour, doc corrections, dependency bumps), which start at the plan.
argument-hint: "[short name for the change]"
---

Draft an intent for the owner to accept. Never set `Status: accepted` or fill in
`Accepted by:`. Only the owner does.

## 1. ID and name

Take the next free ID: one more than the highest ID in any file under
`docs/execution-plans/`. IDs aren't reserved, but 0013 is taken. Use `$ARGUMENTS` as the
name, in kebab case. If there's no name, ask for one.

## 2. Write it

Copy `docs/execution-plans/templates/intent.md` to
`docs/execution-plans/intent/<ID>-<name>.md`. Fill in each section from the conversation
and the repo. Leave the header as `Status: draft` with the placeholder `Accepted by:`.
Give each open question a recommendation.

## 3. Hand over

Give the owner the path, and list the open questions. Don't write the spec until the
owner accepts the intent.
