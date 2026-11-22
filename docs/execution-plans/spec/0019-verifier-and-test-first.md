# Spec 0019: verifier subagent and failing test first

Intent: [0019-verifier-and-test-first](../intent/0019-verifier-and-test-first.md)
Status: accepted
Accepted by: Tom Wilkinson, 2026-11-22

<!-- Copy to docs/exec-plans/spec/<ID>-<name>.md. Only the owner sets Status: accepted.
Acceptance starts plan mode. -->

## Requirements

1. `.claude/agents/verifier.md` defines a Claude Code subagent named `verifier`:
   - Its frontmatter gives `tools: Bash, Read`, and this `description`, worded so
     the main session calls it without being asked:

     ```text
     Use proactively before reporting any task done, and whenever the user asks
     whether the checks pass. Runs the repo's checks (the same command as CI) and,
     for changes to app/, one free scripted session, then reports the literal
     output. Never edits or fixes anything.
     ```
   - Its model is inherited from the calling session. Its frontmatter sets no `model`.
   - The sandbox blocks writes to `.claude/agents/` at the real path. This was checked
     on 2026-11-22, when `mkdir .claude/agents` failed with "Operation not
     permitted". So the file is written to `proposals/0019/.claude/agents/verifier.md`,
     and the owner copies it into place.
2. The verifier runs the checks with the same command as CI's `checks` workflow,
   after removing the Stop hook's fingerprint so the checks can't be skipped:

   ```bash
   rm -f .claude/.checks_fingerprint
   echo '{}' | CLAUDE_PROJECT_DIR=$PWD .claude/hooks/checks_on_stop.sh
   ```

   It reports the command, the exit code, and the literal output. Exit 0 with no
   output means every check passed, and the report says so in those words.
3. When the change touches `app/`, the verifier also runs one scripted session, and
   reports its literal output:

   ```bash
   .venv/bin/python -m scripts.local_session "What is the status of demo?"
   ```

   It never passes `--real`, and never runs `pytest -m integration` (COST-001).
4. The verifier never edits, creates or deletes files, other than the fingerprint
   file in requirement 2. It doesn't fix failures, and it doesn't suggest fixes. It
   reports what failed and stops.
5. The `AGENTS.md` proposal (`proposals/0019/AGENTS.md`) adds these lines to the end
   of the Tests section. They're the intent's rules, and requirement 6 settles how to
   commit a failing test:
   - For a bug fix, first commit a test that reproduces the bug, marked
     `@pytest.mark.xfail(strict=True, reason='<the bug>')`. Then fix the code. The fix
     commit removes that marker, and changes nothing else in the test.
   - When a test fails, assume the code is wrong. Change a test only when the active
     plan says the behaviour it checks is changing, or when you can say why the test
     itself is wrong.
   - Change a test in its own commit, and give the reason in the commit message. If
     the test is a bug fix's reproducing test, stop and ask the owner instead.
   - Before reporting a task done, run the checks, or ask the `verifier` subagent to,
     and paste the output into the report.
6. A bug fix's first commit passes the checks. A plain failing test would make the
   Stop hook block the turn and fail CI on that commit. A strict `xfail` passes while
   the bug exists, and turns into a failure (XPASS) once the code is fixed, so the fix
   commit has to remove the marker.
7. "Paste the output" applies to the final report of a task, not to every turn. The
   Stop hook already checks each turn that changed files.
8. `README.md` lists the verifier in the "Review commands" table under Code quality,
   with its source `.claude/agents/verifier.md`, and says it runs the same checks as
   CI and never edits.
9. `REVIEW.md` doesn't change. This adds no CI check.
10. `docs/exec-plans/handover.md` marks stage 3 done (plan 0019). Its stage 3 section
    records what was built and decided. In stage 4, "It doesn't edit a failing test"
    becomes the rules in requirement 5: test changes come in their own commit with a
    reason, and a bug fix starts with a strict `xfail`.

## Design

**One check command, shared with CI.** The intent recommended running the README's
"Run the checks by hand" commands. That list leaves out the bare `noqa` and
`type: ignore` check, and it would drift from the hook. CI runs the hook itself with
an empty input, and the hook only skips when its fingerprint matches. So deleting the
fingerprint first makes the verifier run exactly what CI runs, and the hook doesn't
change. The fingerprint is a gitignored cache. On a pass the hook writes it again,
which is what the Stop hook would do anyway.

**The verifier's prompt.** A short body: the two commands, when to run the second,
and the report format (command, exit code, literal output, nothing more). It says
not to edit, fix or retry. With tools limited to Bash and Read, it has no Edit or
Write.

**Scripted sessions only for `app/`.** Each `local_session` run adds a session to
`.sessions/sessions.db`, which the evidence review reads (EVID-001). Running one on
every verification would fill the evidence with scripted sessions. Changes outside
`app/` don't change what a session does, so the checks are enough.

**Strict `xfail` for the reproducing test.** The test is committed as it will stay.
Only the marker comes off. `strict=True` is required, because a plain `xfail` passes
quietly once the bug is fixed, and the marker would never be removed. The fix
commit's diff to the test is one deleted line, so a reviewer can see the test wasn't
weakened.

**Options rejected:**
- **The locked-test hook** (handover step 3). The intent recommended waiting. A strict
  `xfail`, and test changes in their own commits, make a weakened test visible in
  review. Build it if the evidence review finds an agent editing a test to make it
  pass.
- **Running the README's commands directly.** Covered above: it drifts from CI.
- **A `--standalone` flag for `checks_on_stop.sh`.** It changes a protected hook to
  save one `rm`.
- **A second subagent** (`simplifier` or `researcher`). There's no need for one yet.
  `/simplify` already exists.
- **A cheaper model for the verifier.** Setting `model: haiku` would save tokens. But
  it adds a model choice that `governance/allowlists/models.yaml` doesn't cover, for
  a task that is mostly running commands. Revisit if verifier runs show up as a cost.
- **A unit test of the verifier's frontmatter.** The file sits in `proposals/` until
  the owner applies it, so a test in this plan would fail until then. Stage 4's evals
  can test the verifier as it runs.

## Out of scope

- The locked-test hook, and a `locked_tests:` plan field.
- Parallel sessions in git worktrees. The owner dropped them, and the handover's
  unassigned gaps record it.
- Any change to `checks_on_stop.sh`, `.claude/settings.json` or CI.
- Evals that check these rules. They belong to stage 4.
- Retrofitting `xfail` tests for past bug fixes.

## Policies checked

- `governance/rules.yaml`:
  - **GOV-002:** `AGENTS.md` and `.claude/agents/verifier.md` change by proposal in
    `proposals/0019/`. The verifier file isn't a protected path, but the sandbox
    blocks it, so it goes the same way.
  - **COST-001:** the verifier never runs `--real` or integration tests, and the
    `ask` rule `Bash(*local_session*--real*)` in `.claude/settings.json` would stop it
    if it tried. Its own tokens come from the calling session, like any subagent. The
    build makes no paid calls.
  - **EVID-001:** scripted sessions run only for `app/` changes (Design).
  - **SEC-001:** the verifier reads no `.env` file. `Read(**/.env)` is denied, and the
    sandbox denies reading it too.
  - **GOV-004, GOV-006, SCOPE-001, SCOPE-002:** one plan, one session, the trailers,
    and edits inside `scope_paths`. A bug fix's two commits both carry the trailers.
  - **DEP-001:** no new dependencies. `pytest.mark.xfail` is built in.
- `docs/SECURITY.md`: no data, secrets or access change. The verifier runs commands
  any session can already run.
- `app/AGENTS.md`: `app/` doesn't change, so nothing applies.

## Concerns

- **"Never edits" is an instruction, not a control.** The verifier has Bash, and Bash
  can write files. Limiting `tools` takes away Edit and Write, and the sandbox, deny
  rules and `governance_gate.sh`'s scope check still apply to its Bash commands. But
  nothing stops it running `sed -i` on a file in scope. An edit would still show up in
  the diff, and in the calling session's next Stop hook run.
- **Deleting the fingerprint is a side effect.** It's a cache, and the worst it does
  is make the next Stop hook run the checks again. But it is a write, which is why
  requirement 4 names it.
- **Stop-hook output is short on success.** A passing run prints nothing, so the
  "pasted output" for a pass is the command and `exit 0`. That's the same evidence CI
  gives. The playbook's "paste the output" expects more on a pass, but this repo's
  check command doesn't produce it.
- **"Proactively" makes a call likely, not certain.** Claude Code decides from the
  description whether to delegate, so the main session may still skip the verifier.
  The `AGENTS.md` rule to paste check output applies either way, and the Stop hook
  runs the checks on every turn that changed files regardless.
- **The xfail rule depends on the agent following it.** Until stage 4's evals or the
  locked-test hook exist, only review checks that a bug fix started with a strict
  `xfail`, and that the fix commit only removed the marker.
