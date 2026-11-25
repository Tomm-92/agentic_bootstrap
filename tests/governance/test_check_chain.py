"""The intent -> spec -> plan chain check, on file texts and against a temporary repo."""

import os
import subprocess

import pytest

from scripts.check_chain import plan_problems, problems

PLAN = 'docs/execution-plans/plan/active/0030-x.md'
INTENT = 'docs/execution-plans/intent/0030-x.md'
SPEC = 'docs/execution-plans/spec/0030-x.md'
LINKS = 'Intent: [0030-x](../../intent/0030-x.md)\nSpec: [0030-x](../../spec/0030-x.md)\n'
ACCEPTED = 'Status: accepted\nAccepted by: Owner, 2026-11-25\n'
UNACCEPTED = ' and an Accepted by: line from the owner'
UNDER = ' under Policies checked'
POLICIES = (
  '## Policies checked\n\n`spec-security` report:\n\n- SEC-001: no finding.\n\n## Concerns\n'
)


def check(plan=LINKS, intent=ACCEPTED, spec=ACCEPTED + POLICIES):
  files = {PLAN: plan, INTENT: intent, SPEC: spec}
  return plan_problems(PLAN, files.get)


def test_an_accepted_chain_passes():
  assert check() == []


@pytest.mark.parametrize('reason', ['typo fix', 'doc correction'])
def test_intent_none_with_a_reason_passes(reason):
  assert check(plan=f'Intent: none ({reason})\n', intent=None, spec=None) == []


@pytest.mark.parametrize('reason', ['', '  ', '<reason>'])
def test_intent_none_without_a_reason_fails(reason):
  assert check(plan=f'Intent: none ({reason})\n', intent=None, spec=None)


def test_a_plan_with_no_links_fails():
  found = check(plan='# Plan\n')
  assert len(found) == 2
  assert 'Intent: link' in found[0]


def test_a_link_to_a_missing_file_fails():
  assert check(spec=None) == ['Spec link ../../spec/0030-x.md names no file']


@pytest.mark.parametrize(
  'header',
  [
    'Status: draft\nAccepted by: Owner, 2026-11-25\n',
    'Status: accepted\nAccepted by: <owner>, <YYYY-MM-DD>\n',
    'Status: accepted\n',
  ],
)
def test_an_unaccepted_intent_fails(header):
  assert check(intent=header) == [f'{INTENT} needs Status: accepted' + UNACCEPTED]


@pytest.mark.parametrize(
  'policies',
  [
    '## Policies checked\n\n- GOV-002: ok.\n\n## Concerns\n\nspec-security only here.\n',
    '## Policies checked\n\n- `spec-security`: its report on this spec, pasted in.\n',
  ],
)
def test_a_spec_without_a_spec_security_report_fails(policies):
  assert check(spec=ACCEPTED + policies) == [f'{SPEC} needs the spec-security report' + UNDER]


@pytest.fixture
def repo(tmp_path, monkeypatch):
  env = {
    'GIT_CONFIG_GLOBAL': os.devnull,
    'GIT_CONFIG_NOSYSTEM': '1',
    'GIT_AUTHOR_NAME': 't',
    'GIT_AUTHOR_EMAIL': 't@example.com',
    'GIT_COMMITTER_NAME': 't',
    'GIT_COMMITTER_EMAIL': 't@example.com',
  }
  for key, value in env.items():
    monkeypatch.setenv(key, value)
  monkeypatch.chdir(tmp_path)

  def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True, text=True).stdout  # noqa: S603, S607 - fixed git commands in a temporary repo

  def commit(files):
    for name, text in files.items():
      path = tmp_path / name
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(text)
    git('add', '-A')
    git('commit', '-q', '-m', 'change')

  git('init', '-q', '-b', 'main')
  commit({'docs/execution-plans/plan/active/0040-old.md': '# A plan with no links\n'})
  git('tag', 'base')
  return commit, git


def test_only_added_plans_are_checked_at_the_head(repo):
  commit, git = repo
  commit({PLAN: LINKS, INTENT: ACCEPTED, SPEC: 'Status: draft\n'})
  commit({SPEC: ACCEPTED + POLICIES})
  assert problems('base..HEAD') == []
  commit({'docs/execution-plans/plan/active/0031-y.md': '# Plan\n'})
  assert [line.split(':')[0] for line in problems('base..HEAD')] == [
    'docs/execution-plans/plan/active/0031-y.md'
  ] * 2


def test_moving_a_plan_to_completed_is_not_an_addition(repo):
  _, git = repo
  os.makedirs('docs/execution-plans/plan/completed')
  git('mv', 'docs/execution-plans/plan/active/0040-old.md', 'docs/execution-plans/plan/completed/')
  git('commit', '-q', '-m', 'move')
  assert problems('base..HEAD') == []


def test_plans_before_the_first_checked_id_and_other_files_are_skipped(repo):
  commit, _ = repo
  commit({'docs/execution-plans/plan/completed/0025-z.md': '# Plan\n'})
  commit({'docs/execution-plans/plan/active/.gitkeep': ''})
  assert problems('base..HEAD') == []
