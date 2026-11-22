"""SCOPE-002 in CI: the scope check, on paths and against a temporary repo."""

import os
import subprocess

import pytest

from scripts.check_scope import out_of_scope, problems

GLOBS = ['app/**', 'proposals/0001/**', 'README.md']


@pytest.mark.parametrize('path', ['app/agent.py', 'app/deep/x.py', 'README.md', 'proposals/0001/x'])
def test_paths_inside_any_glob_pass(path):
  assert out_of_scope(GLOBS, set(), [path]) == []


def test_plan_files_are_exempt():
  assert out_of_scope(GLOBS, set(), ['docs/execution-plans/plan/active/0002-x.md']) == []


def test_paths_outside_every_glob_fail():
  assert out_of_scope(GLOBS, set(), ['scripts/x.py', 'app.py']) == ['scripts/x.py', 'app.py']


def test_applying_a_written_proposal_passes():
  assert out_of_scope(GLOBS, {'AGENTS.md'}, ['AGENTS.md']) == []


def test_a_proposal_folder_in_scope_does_not_cover_paths_it_never_held():
  assert out_of_scope(GLOBS, {'AGENTS.md'}, ['CLAUDE.md']) == ['CLAUDE.md']


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

  def commit(files, plan='0001'):
    for name, text in files.items():
      path = tmp_path / name
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text(text)
    git('add', '-A')
    git('commit', '-q', '-m', f'change\n\nPlan: {plan}')

  def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True, text=True).stdout  # noqa: S603, S607 - fixed git commands in a temporary repo

  git('init', '-q', '-b', 'main')
  plan = "---\nid: '0001'\nscope_paths:\n  - app/**\n  - proposals/0001/**\n---\n"
  commit({'docs/execution-plans/plan/active/0001-x.md': plan})
  return commit, git


def test_the_repo_history_reports_only_out_of_scope_changes(repo):
  commit, git = repo
  commit({'app/a.py': 'x', 'proposals/0001/AGENTS.md': 'new'})
  commit({'AGENTS.md': 'new'})
  commit({'CLAUDE.md': 'new', 'proposals/0001/CLAUDE.md': 'new'})
  commit({'scripts/x.py': 'x'})
  git('checkout', '-q', '-b', 'side', 'HEAD~3')
  commit({'other.txt': 'x'}, plan='none')
  git('checkout', '-q', 'main')
  git('merge', '-q', '--no-ff', '-m', 'merge', 'side')
  found = problems(['HEAD'])
  assert len(found) == 1
  assert found[0].endswith('scripts/x.py is outside its scope_paths')


def test_intents_and_specs_are_not_read_as_plans(repo):
  commit, _ = repo
  intent = '# Intent\n\nStatus: draft\n'
  commit(
    {'docs/execution-plans/intent/0001-x.md': intent, 'docs/execution-plans/spec/0001-x.md': intent}
  )
  commit({'app/a.py': 'x'})
  commit({'docs/execution-plans/intent/0002-y.md': intent}, plan='0002')
  commit({'scripts/x.py': 'x'}, plan='0002')
  assert problems(['HEAD']) == []
