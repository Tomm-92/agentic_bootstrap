"""REV-001 on pull requests, with a stub client and fake git: nothing here calls a model."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from scripts import ai_review

TALLY = 'Tally: important=1 nit=2'
FILES = {
  'base': {
    'REVIEW.md': 'RUBRIC',
    'AGENTS.md': 'AGENTS',
    'app/AGENTS.md': 'APP_AGENTS',
    'ARCHITECTURE.md': 'ARCHITECTURE',
    'docs/exec-plans/spec/0001-x.md': 'BASE_SPEC',
  },
  'head': {
    'docs/exec-plans/active/0001-x.md': 'PLAN',
    'docs/exec-plans/intent/0001-x.md': 'INTENT',
    'docs/exec-plans/spec/0001-x.md': 'SPEC',
    'REVIEW.md': 'HEAD_RUBRIC',
  },
}


class StubClient:
  def __init__(self, stop_reason='end_turn', text=f'finding\n{TALLY}'):
    self.calls = []
    self.stop_reason = stop_reason
    self.text = text
    self.messages = self

  def create(self, **kwargs):
    self.calls.append(kwargs)
    return SimpleNamespace(
      stop_reason=self.stop_reason, content=[SimpleNamespace(type='text', text=self.text)]
    )


def _fake_git(monkeypatch, files=FILES):
  def git(*args):
    match args:
      case ('show', ref):
        sha, path = ref.split(':', 1)
        return files[sha][path]
      case ('ls-tree', '--name-only', sha, folder):
        return ''.join(f'{path}\n' for path in files[sha] if path.startswith(folder))
      case ('log', *_):
        return '0001\n'
      case ('diff', '--name-only', _):
        return 'a.py\n'
      case ('diff', _):
        return 'DIFF'

  monkeypatch.setattr(ai_review, '_git', git)


def test_uses_the_allowlisted_reviewer_model(monkeypatch):
  _fake_git(monkeypatch)
  client: Any = StubClient()
  assert ai_review.review(client, 'base', 'head') == f'finding\n{TALLY}'
  models = yaml.safe_load(Path('governance/allowlists/models.yaml').read_text())['models']
  reviewers = {m['id'] for m in models if 'reviewer' in m['use']}
  writers = {m['id'] for m in models if 'executor' in m['use']}
  assert client.calls[0]['model'] in reviewers
  assert client.calls[0]['model'] not in writers


def test_instructions_come_from_base_and_the_pr_from_head(monkeypatch):
  _fake_git(monkeypatch)
  client: Any = StubClient()
  ai_review.review(client, 'base', 'head')
  system = client.calls[0]['system']
  content = client.calls[0]['messages'][0]['content']
  for text in ('RUBRIC', 'AGENTS', 'APP_AGENTS', 'ARCHITECTURE'):
    assert text in system
  assert 'HEAD_RUBRIC' not in system
  for text in ('PLAN', 'INTENT', 'SPEC', 'a.py', 'DIFF'):
    assert text in content
  assert 'BASE_SPEC' not in content


def test_a_missing_spec_is_stated(monkeypatch):
  head = {k: v for k, v in FILES['head'].items() if '/spec/' not in k}
  _fake_git(monkeypatch, {'base': FILES['base'], 'head': head})
  client: Any = StubClient()
  ai_review.review(client, 'base', 'head')
  assert "No spec for plan '0001'." in client.calls[0]['messages'][0]['content']


def test_a_missing_or_malformed_tally_is_marked_unavailable(monkeypatch):
  _fake_git(monkeypatch)
  for text in ('finding', 'finding\n**Tally: important=1 nit=2**', 'Tally: important=1\nmore'):
    client: Any = StubClient(text=text)
    assert ai_review.review(client, 'base', 'head').endswith(f'\n{ai_review.UNAVAILABLE}')


def test_refusal_tells_the_human_and_does_not_retry(monkeypatch):
  _fake_git(monkeypatch)
  client: Any = StubClient(stop_reason='refusal')
  assert ai_review.review(client, 'base', 'head') == ai_review.REFUSED
  assert len(client.calls) == 1
