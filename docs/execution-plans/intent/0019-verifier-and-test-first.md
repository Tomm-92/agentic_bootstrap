# Intent 0019: verifier subagent and failing test first

Author: Claude, drafted for the owner
Status: accepted
Accepted by: Thomas Wilkinson, 2026-11-22

<!-- Copy to docs/exec-plans/intent/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts the spec. -->

## Problem

Plays 07 and 08 of the
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook)
are stage 3 in `docs/exec-plans/handover.md`. Two things are missing.

- **"Done" is claimed, not shown.** The Stop hook (`checks_on_stop.sh`) blocks a turn
  while checks fail. But an agent's report that a task is done carries no check
  output, and nothing asks for it. There's no scoped helper that only runs the checks
  and reports. `.claude/agents/` doesn't exist.
- **Bug fixes can bend the test.** Nothing says a bug fix starts with a failing test
  committed before the fix. Nothing stops an agent changing a test until it passes.
  The playbook wants the test committed first and a hook keeping the agent off it.

This hurts the owner, who has to trust a "done" without the evidence, and can't tell
from a diff whether a test was weakened to pass.

The playbook's third part of these plays, parallel sessions in git worktrees, is out
of scope. The owner decided to drop it: the owner accepts and applies every artifact,
so more sessions mostly lengthen the review queue, and little of the remaining work is
independent.

## Proposed outcome

- **A verifier subagent** at `.claude/agents/verifier.md`. It has Bash and Read only.
  It runs the repo's checks and the free scripted `local_session`, never `--real`, and
  reports their literal output. It never edits. Any agent or the owner can call it.
- **`AGENTS.md` says, under Tests:**
  - For a bug fix, commit a failing test first, then fix the code without editing
    that test.
  - When a test fails, assume the code is wrong. Change a test only when the active
    plan says the behaviour it checks is changing, or when you can say why the test
    itself is wrong.
  - Change a test in its own commit, and give the reason in the commit message. If
    the test is one the plan says not to edit, such as a bug fix's failing test, stop
    and ask the owner instead.
  - Before reporting a task done, run the checks and paste their output.
- **Optionally, a hook that locks tests.** It denies edits to test files the active
  plan lists as locked. It stays fast, and it only checks the file being edited. This
  depends on the owner's decision below.
- **`REVIEW.md` is updated** if this adds anything CI enforces, so the PR reviewer
  doesn't repeat it.
- **The handover shows stage 3 done,** records that parallel sessions were dropped,
  and corrects anything in its stage 3 and 4 sections that turned out wrong.

## Affected users and systems

- **The owner:** sees check output in "done" reports, and applies the proposals.
- **Coding agents:** follow the new `AGENTS.md` rules and can call the verifier.
- **`.claude/agents/`** (new). The sandbox may block writes there at the real path, as
  it blocks `.claude/skills/`. If so, it goes in `proposals/0019/`.
- **`AGENTS.md`** (protected, so by proposal).
- **`.claude/hooks/governance_gate.sh` and the plan template**, if the locked-test
  hook is built. The hook is protected, so it goes by proposal.
- **`README.md`**, where it lists the review commands, and tests for any new or
  changed script.
- **Stage 4,** whose evals will check these rules.
- **Not affected:** the product agent in `app/`, and the runtime rules.

## Constraints

- **GOV-002:** `AGENTS.md`, `.claude/hooks/` and `.claude/settings.json` change only
  through `proposals/0019/`.
- **COST-001:** the verifier never runs `--real` or `pytest -m integration`. The build
  makes no paid calls.
- **Concise code:** no new script where an existing check command will do.

## Open questions

1. **Build the locked-test hook now, or wait?** Waiting means building it once the
   evidence review shows an agent editing a test to make it pass. Recommendation:
   wait. The failing test committed first, and each test change in its own commit
   with a reason, make a weakened test visible in review. Stage 4's evals can check
   for it too.
2. **How does the verifier run the checks?** `checks_on_stop.sh` reads hook input
   from stdin and skips itself when its fingerprint file matches. Run as is, it can
   pass without checking anything. The options are to run the check commands
   directly (the README's "Run the checks by hand" block), or to change the hook so
   it can run standalone. Recommendation: run the commands directly, so the hook
   doesn't change.
3. **A second subagent?** The handover suggests a `simplifier` or `researcher` only if
   a real need shows up. Recommendation: none now.
4. **Where does "paste the check output" apply?** Only to the final report of a task,
   or to every turn that edits code? Recommendation: the final report only. The Stop
   hook already covers each turn.
