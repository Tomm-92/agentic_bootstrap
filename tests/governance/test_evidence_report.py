"""EVID-001: the evidence report summarises what exists, and says what doesn't."""

import json
import sqlite3
import subprocess

from scripts.evidence_report import report


def _git(repo, *args):
  subprocess.run(  # noqa: S603 - fixed git commands, in a temporary repo
    ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com', *args],  # noqa: S607 - from PATH
    cwd=repo,
    check=True,
    capture_output=True,
  )


def _repo(tmp_path):
  _git(tmp_path, 'init', '-q', '-b', 'main')
  _git(tmp_path, 'commit', '-q', '--allow-empty', '-m', 'm\n\nGovernance: abc\nPlan: 0001\n')
  _git(tmp_path, 'commit', '-q', '--allow-empty', '-m', 'no trailers')
  return tmp_path


def test_report_says_what_is_missing(tmp_path):
  text = report(_repo(tmp_path))
  assert 'Commits: 2, of which 1 have a Plan trailer.' in text
  assert 'Governance hashes recorded: 1.' in text
  assert 'No session log' in text
  assert 'No activation ledger' in text


def test_report_summarises_sessions_and_decisions(tmp_path):
  repo = _repo(tmp_path)
  (repo / '.sessions').mkdir()
  decision = {'tool': 't', 'tier': 'confirm', 'result': 'confirmed', 'rule': 'TOOL-001'}
  denied = {'tool': 't', 'tier': 'deny', 'result': 'denied', 'rule': 'FS-001'}
  event = {
    'custom_metadata': {'governance_sha': 'abc'},
    'actions': {
      'state_delta': {'governance_log:1:confirmed': decision, 'governance_log:2:denied': denied}
    },
  }
  with sqlite3.connect(repo / '.sessions/sessions.db') as connection:
    connection.execute('CREATE TABLE events (session_id TEXT, event_data TEXT)')
    connection.execute('INSERT INTO events VALUES (?, ?)', ('s1', json.dumps(event)))
    connection.execute('INSERT INTO events VALUES (?, ?)', ('s1', json.dumps({'author': 'user'})))
  text = report(repo)
  assert 'Sessions: 1, with 2 stored events.' in text
  assert 'stamped with a governance hash: 1' in text
  assert "{'confirmed': 1, 'denied': 1}" in text
  assert 'Approval rate: 100%.' in text
