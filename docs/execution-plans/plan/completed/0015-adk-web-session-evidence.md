---
id: '0015'
rules: [SCOPE-001, SCOPE-002, EVID-001, DATA-001]
scope_paths:
  - .gitignore
  - scripts/evidence_report.py
  - tests/governance/test_evidence_report.py
  - docs/SECURITY.md
  - docs/REVIEW.md
  - ARCHITECTURE.md
  - docs/exec-plans/**
---

# Plan 0015: count adk web sessions as evidence, and keep them out of git

Ported from plan 0010 of `agentic_tools_v2` (commit `0a79152`), not cherry-picked.

## Goal

The product agent's sessions can be stored in two places, and only one of them is
treated as evidence:

| Database | Written by | Class | Read by the evidence report | Ignored by git |
| --- | --- | --- | --- | --- |
| `.sessions/sessions.db` | `scripts/local_session.py` | `DatabaseSessionService` | Yes | Yes |
| `app/.adk/session.db` | `adk web .`, by default | `SqliteSessionService` | No | No |

`adk web` picks its database in `create_session_service_from_options`
(`google/adk/cli/utils/service_factory.py`). With no `--session_service_uri` it uses
per-agent local storage at `<agent>/.adk/session.db`, so the owner's real sessions go
there. `scripts/evidence_report.py` reads only `.sessions/sessions.db`, so the evidence
review under EVID-001 would miss them. `docs/SECURITY.md` and `docs/REVIEW.md` name only
`.sessions/sessions.db`.

`app/.adk/` holds prompts and tool results word for word (DATA-001), and `git add .`
would commit it.

Both databases have an `events` table with `id`, `session_id` and `event_data` columns,
so one query works on either. `adk web` loads `app` from `app/agent.py`, whose `App`
sets no compaction config, so compaction is off for its sessions too.

## Evidence

- On 18 Nov 2026, `git check-ignore -v app/.adk/session.db` matched no rule.
  `git log --all -- app/.adk` is empty, and `app/.adk/` doesn't exist, so nothing has
  leaked and there is no older database to keep.
- `.sessions/sessions.db` holds 2 sessions and 8 events.
- `_sessions` in `scripts/evidence_report.py` and its test match `agentic_tools_v2`
  before `0a79152`.

## Checklist

- [x] `.gitignore`: add `app/.adk/`. Check that `git check-ignore app/.adk/session.db`
      prints the rule.
- [x] `scripts/evidence_report.py`: make `_sessions` read every `.sessions/*.db` and
      `app/.adk/session.db`. Merge their events, counting each event once by its `id`
      and each session once by its `session_id`, because a database copied from the
      other can hold the same events. Name the files read in the `Sessions:` line. When
      none exists, say so and name both locations.
- [x] `tests/governance/test_evidence_report.py`: write one session to
      `.sessions/sessions.db` and another to `app/.adk/session.db`, and repeat one event
      in both. Assert that both sessions are counted and the repeated event once. Prove
      the test can fail by temporarily reading only `.sessions/sessions.db`.
- [x] Run `.venv/bin/python -m scripts.evidence_report`. Its `Sessions:` line reports
      2 sessions and 8 events in `.sessions/sessions.db`.
- [x] `docs/SECURITY.md`: lines 13 and 48 name both locations. Line 13 says git ignores
      both.
- [x] `docs/REVIEW.md` line 9: name both locations.
- [x] `ARCHITECTURE.md`, the EVID-001 row: add `adk web`'s `SqliteSessionService` at
      `app/.adk/session.db`, with compaction off through `app`.
- [x] The unit and governance test suites pass, as do ruff, mypy and vulture.

## Decisions

- The report reads both locations. Making both writers use one database was rejected:
  - Pointing `adk web` at `.sessions/` needs `--session_service_uri` on every run. That
    is one more thing to remember, which plan 0014 avoided for the same reason.
  - Moving `scripts/local_session.py` to `app/.adk/` changes the EVID-001 control and
    its activation evidence.
- Read `.sessions/*.db`, not only `sessions.db`, so a saved copy counts with no code
  change. Events are counted once by `id`, so an overlapping copy doesn't inflate the
  counts.
- Leave the activation ledger (`docs/governance-activation.md`) alone. Its EVID-001
  rows record what was checked at the time.
- Ignore only `app/.adk/`, not every `.adk/`. The project has one agent package.
- `README.md` line 251 names `.sessions/sessions.db` as where `scripts/local_session.py`
  writes. That is still true, so it is out of scope.

## Risks

- If `adk web` cannot create local storage, it falls back to in-memory sessions and
  only logs a warning (`service_factory.py`). That run leaves no session log. Its traces
  still record the timeline (plan 0014).
- A later ADK version may move the default database. The report then doesn't list
  `app/.adk/session.db` among the files it read, rather than failing silently.
- Assumption: session IDs are unique across the two writers. Both generate UUIDs.

## Owner actions

1. `docs/SECURITY.md` is not yet signed off. When you sign it, the session-log item now
   covers both databases.
