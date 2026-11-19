# Tech-debt tracker

Gaps deferred on purpose, and what closes them.

| Gap | Rule | Close by |
| --- | --- | --- |
| The bootstrap run itself isn't gated by these controls: its rules are instructions until the owner applies the proposal, and a long run works against short sessions. Code quality's locks and gates do apply. | GOV-001, GOV-002, GOV-006, SCOPE-001, SCOPE-002 | The owner reviews the whole branch before merging. Closes for later sessions when the owner applies the proposal |
| Deny rules don't stop scripts that write files themselves. | GOV-002 | Stage 4 sandbox, live once the owner applies it |
| The plan check proves a plan exists, not that edits stay in scope. | SCOPE-002 | Stage 4, live once the owner applies it |
| Commit trailers are instructions, not checks. | GOV-004 | Stages 4 and 5, live once the owner sets `core.hooksPath` |
| The prompt hook restates the governance hash and plan, not the rules' text, and nothing limits a coding session's length. | GOV-006 | Stage 9 evidence review: tighten if transcripts show drift late in sessions |
| Coding agents other than Claude Code get checks, trailers, plan scope and protected paths at commit or in CI, not during the session. Nothing pins their governance hash per session, and nothing stops their pushes or commits on `main` until branch protection exists. | GOV-001, GOV-002, GOV-006, SCOPE-001 | Branch protection (see "When the repo changes") and owner review |
| The edit gate checks scope only for the Edit, Write and NotebookEdit tools. A shell command can write outside `scope_paths`, because the sandbox blocks only protected paths. | SCOPE-002 | The CI scope check reports it at the pull request |
| The CI scope check accepts any path that has a file in the plan's proposal folder, and trusts the plan's `scope_paths` as of the commit, so a plan can widen its own scope. | SCOPE-002 | Owner review of proposals and plan diffs |
| CODEOWNERS, branch protection and required checks are unavailable on private GitHub Free with one author. | GOV-002, DEP-001 | See "When the repo changes" |
| In Claude-only dev mode the reviewer has a different model ID but may be the same family as the planner and executor, so they can share blind spots. | REV-001 | Before production: move the reviewer to a different model family and run the eval suite (MODEL-001) |
| All runtime rules are planned until the owner applies the activation proposal. | GOV-005 to QUAL-001 | Stages 6 to 10, then A01 to A06 in `docs/agent_governance_implementation.md` |
| The proposed sandbox can't be proven inside the run: only a session started under those settings shows the write refused. | GOV-002 | "After the run" step 3 |
| `branch_guard.sh` reads command text, so `sh -c 'git push'`, aliases and `GIT_CONFIG_*` variables get past it, and a write to `.git/config` can repoint `core.hooksPath`. | GOV-002, GOV-004 | CI trailer check and owner review; consider adding `./.git/config` to `denyWrite` |
| The sandbox blocks `docker`, so an armed session can't run the local stack or a verification sandbox. | GOV-002, SBX-001 | The owner runs the stack; phase A02 decides whether to exclude `docker` |
| ADK stores the user's message without calling plugins, so that one stored event has no governance stamp. | GOV-005, EVID-001 | Accept, or wrap the session service to stamp in `append_event` |
| Nothing expires evidence after `retention_days`, and session logs hold prompts unredacted. | EVID-001, DATA-001 | `docs/SECURITY.md` sign-off |
| FS-001 checks a path when the tool is called, so a symlink made afterwards can still escape. | FS-001 | Phase A02's sandbox |
| `commit-msg` compares the trailer with `HEAD`, which during `git commit --amend` is the commit being amended, not its parent. Amending a commit that changed `governance/` needs the new hash locally, and `check_trailers.sh` then flags it in CI. | GOV-004 | Avoid amending governance commits; CI check and owner review |
| `ai-review.yml` runs the PR's own copy of `scripts/ai_review.py` with the API key available. | REV-001, SEC-002 | When the repo gains a collaborator, run the script from the base branch |
| The manual run and integration tests against `claude-haiku-5-5` haven't run, because `ANTHROPIC_API_KEY` was unset. Token counting hasn't seen a real response. | COST-001 | "After the run" step 4 |
| The `governance.session_tokens` gauge is labelled per session, so its cardinality grows with sessions. Fine locally; a shared backend needs a different approach. | COST-001, OBS-001 | Before moving to a shared backend |
| ADK captures prompts and responses in spans by default, so traces hold them. | DATA-001 | `docs/SECURITY.md` sign-off |
| `scripts/check_scope.py` counts only the files in a plan's proposal folder, so a proposal shipped as a `.diff` doesn't cover the paths it patches. The patched paths must be in the plan's `scope_paths`, or the owner's apply commit fails the scope check. | SCOPE-002 | Plan 0013: teach the check to read the paths a `.diff` patches |
| Nothing enforces the intent → spec → plan chain. A plan can skip its intent, and an agent could set `Status: accepted` on an intent or spec itself. | GOV-002, SCOPE-001 | A CI check that every new plan links an accepted intent and spec, or gives `Intent: none (<reason>)`; until then the `AGENTS.md` rule and owner review |
| An intent can't be committed on its own, because `commit-msg` and CI need a `Plan:` trailer naming a plan in `active/` or `completed/`. The intent, spec and plan go in one commit, so acceptance at each gate isn't its own commit. | GOV-004 | Change `check_trailers.sh` to accept a trailer naming an intent or spec |
| Nothing checks that a plan stays in sync with the diff as the build departs from it. | SCOPE-001 | A hook that flags a diff the plan doesn't describe; `ai_review.py` already flags departures at the pull request |
| With `defaultMode: plan`, a tool that starts Claude Code non-interactively starts in plan mode unless it passes its own `--permission-mode`. | GOV-002 | Pass `--permission-mode` in any such tool |
