"""Summarises the evidence for the EVID-001 review in docs/records/evidence_review.md."""

import json
import re
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

DECISION_PREFIX = 'governance_log:'  # Mirrors app.governance, whose import fails while dirty.


def _commits(repo: Path) -> list[str]:
  trailer = '%(trailers:key={},valueonly,separator=)'
  log_format = '%h%x09' + trailer.format('Governance') + '%x09' + trailer.format('Plan')
  log = subprocess.run(  # noqa: S603 - fixed git command
    ['git', '-C', str(repo), 'log', f'--format={log_format}'],  # noqa: S607 - git from PATH
    capture_output=True,
    text=True,
    check=True,
  ).stdout.splitlines()
  rows = [line.split('\t') for line in log]
  plans = Counter(row[2] for row in rows if row[2])
  hashes = {row[1] for row in rows if row[1]}
  return [
    f'Commits: {len(rows)}, of which {sum(bool(r[2]) for r in rows)} have a Plan trailer.',
    f'Governance hashes recorded: {len(hashes)}.',
    f'Commits per plan: {dict(plans)}.',
  ]


def _plans(repo: Path) -> list[str]:
  plans = repo / 'docs/execution-plans/plan'
  active = sorted(p.name for p in plans.glob('active/*.md'))
  completed = sorted(p.name for p in plans.glob('completed/*.md'))
  tracker = repo / 'docs/tech_debt_tracker.md'
  gaps = tracker.read_text().count('\n| ') - 2 if tracker.exists() else 0
  return [
    f'Active plans: {active}.',
    f'Completed plans: {completed}.',
    f'Tech-debt entries: {gaps}.',
  ]


def _ledger(repo: Path) -> list[str]:
  ledger = repo / 'docs/records/governance_activation.md'
  if not ledger.exists():
    return ['No activation ledger.']
  rows = [line.split(' | ') for line in ledger.read_text().splitlines() if line.startswith('| ')]
  return [f'Ledger results: {dict(Counter(row[4] for row in rows[2:]))}.']


def _transcripts(repo: Path) -> list[str]:
  folder = Path.home() / '.claude/projects' / re.sub(r'[^a-zA-Z0-9]', '-', str(repo.resolve()))
  return [f'Coding-agent transcripts: {len(list(folder.glob("*.jsonl")))} in {folder}.']


def _sessions(repo: Path) -> list[str]:
  # scripts/local_session.py writes .sessions/, and `adk web` defaults to app/.adk/.
  databases = [*sorted(repo.glob('.sessions/*.db')), *repo.glob('app/.adk/session.db')]
  if not databases:
    return ['No session log at .sessions/*.db or app/.adk/session.db.']
  # Keyed by event id, so a database copied from another counts its events once.
  rows: dict[str, tuple[str, str]] = {}
  for database in databases:
    with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as connection:
      query = 'SELECT id, session_id, event_data FROM events'
      rows |= {id_: (session, data) for id_, session, data in connection.execute(query)}
  events = [json.loads(data) for _, data in rows.values()]
  decisions = [
    value
    for event in events
    for key, value in event.get('actions', {}).get('state_delta', {}).items()
    if key.startswith(DECISION_PREFIX)
  ]
  results = Counter(d['result'] for d in decisions)
  answered = results['confirmed'] + results['rejected']
  approval = f'{results["confirmed"] / answered:.0%}' if answered else 'no confirmations yet'
  stamped = [e for e in events if (e.get('custom_metadata') or {}).get('governance_sha')]
  return [
    f'Sessions: {len({session for session, _ in rows.values()})}, with {len(events)} stored'
    f' events, in {", ".join(str(d.relative_to(repo)) for d in databases)}.',
    f'Events stamped with a governance hash: {len(stamped)} (user messages are not stamped).',
    f'Tool decisions by result: {dict(results)}.',
    f'Tool decisions by rule: {dict(Counter(d["rule"] for d in decisions))}.',
    f'Approval rate: {approval}.',
  ]


def report(repo: Path) -> str:
  sections = {
    'Commits': _commits,
    'Plans': _plans,
    'Ledger': _ledger,
    'Transcripts': _transcripts,
    'Product-agent sessions': _sessions,
  }
  lines = [
    f'{title}:\n' + '\n'.join(f'- {line}' for line in section(repo))
    for title, section in sections.items()
  ]
  return '\n\n'.join(lines) + '\n\nTraces and alerts: see observability/ and Grafana.\n'


if __name__ == '__main__':
  sys.stdout.write(report(Path(__file__).parent.parent))
