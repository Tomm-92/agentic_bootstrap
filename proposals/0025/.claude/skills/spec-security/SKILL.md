---
name: spec-security
description: Check a spec, not code, against this repo's security policy before the owner accepts it. Use when writing or reviewing a spec in docs/execution-plans/spec/, and always from /spec. Diffs are reviewed by the CI review, not this skill.
argument-hint: "[spec file; default: the newest spec]"
---

Check a spec against the security checklist. Report findings. Do not edit the spec
unless `/spec` called this skill, which pastes the findings into it.

Keep it cheap: work in this session, start no subagents, and read only the spec and
the files a finding needs.

## 1. Scope

If `$ARGUMENTS` names a spec, check that one. Otherwise check the spec in
`docs/execution-plans/spec/` with the highest ID. Never review a diff or code: say that
the CI review covers diffs, and stop.

## 2. Checklist

The checklist is `checklist.md` in this skill's folder. Read it first. Apply the Spec
line of each rule whose subject the spec touches. Leave out everything its "Already
enforced, don't report" list covers.

## 3. Evidence

Every finding cites a rule ID from the checklist, and the spec line it's about. Read the
rule in `governance/rules.yaml` before you cite it. When a rule's control is still
planned, say so: the spec must not rely on it. Drop any finding you can't back.

## 4. Report

One line per rule the spec touches, most important first:

`<rule ID>: <finding, or "no finding">: <fix, if any>`

Then name each rule you left out as not touched. If a rule can't be met alongside
another, say so plainly, for the spec's Concerns section.
