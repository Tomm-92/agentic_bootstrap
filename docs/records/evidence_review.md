# Evidence review

Held each sprint by the owner (EVID-001). Start from `.venv/bin/python -m scripts.evidence_report`.

## Inputs

- Coding-agent transcripts
- Commit trailers
- Product-agent session logs and governance logs (`.sessions/*.db` from `scripts/local_session.py`, and
  `app/.adk/session.db` from `adk web`)
- Traces and alerts (`observability/`)
- `docs/bootstrapper_tech_debt_tracker.md` and `docs/agent_tech_debt_tracker.md`
- PR review findings: the ai-review comments and their `ai-review` artifacts. A recurring
  Important finding is a candidate rule or `AGENTS.md` change.

Phase A05 adds verification reports, eval trends and run records.

## Questions

- Which rules were escalated most?
- Which were never triggered?
- Which behaviours did no rule cover?
- Is the approval rate near 100%? If so, `confirm` is too common, and consent fatigue is
  a risk.

## Output

Rule-change proposals under `proposals/`, applied only through owner PRs. Record the date
and outcome of each review below.

| Date | Reviewer | Outcome |
| --- | --- | --- |
| 2026-11-11 | Tom Wilkinson (owner) | First review, covering 2 real claude-haiku-5-5 runs. No escalations, no confirmations, no rule changes. Two gaps found: the answer misreported the tool status, and one tool call ran without a logged decision. |
