"""REV-001 on pull requests, with a stub client: nothing here calls a model."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from scripts import ai_review


class StubClient:
  def __init__(self, stop_reason='end_turn'):
    self.calls = []
    self.stop_reason = stop_reason
    self.messages = self

  def create(self, **kwargs):
    self.calls.append(kwargs)
    return SimpleNamespace(
      stop_reason=self.stop_reason,
      content=[SimpleNamespace(type='text', text='finding')],
    )


def _stub_git(monkeypatch):
  monkeypatch.setattr(ai_review, '_git', lambda *args: 'DIFF' if args[0] == 'diff' else '0001\n')


def test_uses_the_allowlisted_reviewer_model(monkeypatch):
  _stub_git(monkeypatch)
  client: Any = StubClient()
  assert ai_review.review(client, 'a', 'b') == 'finding'
  models = yaml.safe_load(Path('governance/allowlists/models.yaml').read_text())['models']
  reviewers = {m['id'] for m in models if 'reviewer' in m['use']}
  writers = {m['id'] for m in models if 'executor' in m['use']}
  assert client.calls[0]['model'] in reviewers
  assert client.calls[0]['model'] not in writers
  assert 'DIFF' in client.calls[0]['messages'][0]['content']


def test_refusal_tells_the_human_and_does_not_retry(monkeypatch):
  _stub_git(monkeypatch)
  client: Any = StubClient(stop_reason='refusal')
  assert ai_review.review(client, 'a', 'b') == ai_review.REFUSED
  assert len(client.calls) == 1
