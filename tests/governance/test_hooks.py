"""GOV-001, GOV-002, GOV-004, GOV-006, SCOPE-001, SCOPE-002: the hooks, against temporary repos."""

import json
import os
import subprocess
from pathlib import Path

import pytest

PROJECT = Path(__file__).parent.parent.parent
HOOKS = Path(os.environ.get('HOOKS_DIR', '.claude/hooks'))
HOOKS = HOOKS if HOOKS.is_absolute() else PROJECT / HOOKS
GITHOOKS = PROJECT / '.githooks'
PLAN = (
  "---\nid: '0001'\nrules: [SCOPE-002]\nscope_paths:\n  - app/**\n  - scripts/**\n---\n\n# Plan\n"
)
ZERO = '0' * 40
GIT_ENV = {
  'GIT_CONFIG_GLOBAL': os.devnull,
  'GIT_CONFIG_NOSYSTEM': '1',
  'GIT_AUTHOR_NAME': 't',
  'GIT_AUTHOR_EMAIL': 't@example.com',
  'GIT_COMMITTER_NAME': 't',
  'GIT_COMMITTER_EMAIL': 't@example.com',
}


class Repo:
  def __init__(self, path):
    self.path = path

  def run(self, *cmd, stdin=None):
    env = {**os.environ, **GIT_ENV, 'CLAUDE_PROJECT_DIR': str(self.path)}
    return subprocess.run(  # noqa: S603 - fixed test commands, run inside a temporary repo
      [str(c) for c in cmd],
      cwd=self.path,
      input=stdin,
      text=True,
      capture_output=True,
      check=False,
      env=env,
    )

  def git(self, *args):
    result = self.run('git', *args)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()

  def write(self, relative, text='x\n'):
    path = self.path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

  def commit(self, message='m'):
    self.git('add', '-A')
    self.git('commit', '-q', '--allow-empty', '-m', message)

  def sha(self):
    return self.git('rev-parse', 'HEAD:governance')

  def gate(self, event, session='s', **fields):
    payload = {'hook_event_name': event, 'session_id': session, **fields}
    return self.run(HOOKS / 'governance_gate.sh', stdin=json.dumps(payload))

  def edit(self, path):
    return self.gate('PreToolUse', tool_input={'file_path': str(path)})

  def guard(self, command):
    return self.run(
      HOOKS / 'branch_guard.sh', stdin=json.dumps({'tool_input': {'command': command}})
    )

  def commit_msg(self, message):
    file = self.path.parent / 'COMMIT_EDITMSG'
    file.write_text(message)
    return self.run(GITHOOKS / 'commit-msg', file)


def denied(result):
  if not result.stdout:
    return False
  return json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'] == 'deny'


def blocked(result):
  return result.stdout.startswith('{') and json.loads(result.stdout)['decision'] == 'block'


@pytest.fixture
def repo(tmp_path):
  repo = Repo(tmp_path / 'repo')
  repo.path.mkdir()
  repo.git('init', '-q', '-b', 'main')
  repo.write('.gitignore', '.venv\n.claude/.session_governance/\n')
  repo.write('governance/rules.yaml', 'rules: []\n')
  (repo.path / '.venv').symlink_to(PROJECT / '.venv')
  repo.commit()
  return repo


def add_plan(repo, name='0001-a.md', text=PLAN):
  repo.write(f'docs/execution-plans/plan/active/{name}', text)


# --- SessionStart and UserPromptSubmit -------------------------------------------------


def test_session_start_reports_hash_session_and_plan(repo):
  add_plan(repo)
  result = repo.gate('SessionStart', session='abc', source='startup')
  assert result.returncode == 0
  assert repo.sha() in result.stdout
  assert '0001-a.md' in result.stdout
  assert 'abc' in result.stdout


def test_session_start_warns_when_git_hooks_are_off(repo):
  assert 'git hooks are off' in repo.gate('SessionStart', source='startup').stdout


def test_prompt_allowed_when_clean_and_restates_hash_and_plan(repo):
  add_plan(repo)
  result = repo.gate('UserPromptSubmit')
  assert not blocked(result)
  assert repo.sha() in result.stdout
  assert '0001-a.md' in result.stdout


def _change_governance(repo):
  repo.write('governance/rules.yaml', 'rules: [changed]\n')
  repo.commit()


def test_prompt_blocked_after_hash_change_until_clear(repo):
  repo.gate('SessionStart', source='startup')
  _change_governance(repo)
  result = repo.gate('UserPromptSubmit')
  assert blocked(result)
  assert 'GOV-006' in result.stdout
  repo.gate('SessionStart', source='clear')
  assert not blocked(repo.gate('UserPromptSubmit'))


def test_new_session_gets_the_new_hash(repo):
  repo.gate('SessionStart', source='startup')
  _change_governance(repo)
  assert blocked(repo.gate('UserPromptSubmit'))
  assert not blocked(repo.gate('UserPromptSubmit', session='other'))


@pytest.mark.parametrize('source', ['resume', 'compact'])
def test_resumed_session_keeps_the_old_pin(repo, source):
  repo.gate('SessionStart', source='startup')
  _change_governance(repo)
  assert 'GOV-006' in repo.gate('SessionStart', source=source).stdout
  assert blocked(repo.gate('UserPromptSubmit'))


def _dirty(repo):
  repo.write('governance/rules.yaml', 'rules: [dirty]\n')


def _untracked(repo):
  repo.write('governance/new.yaml', 'a: 1\n')


def _missing(repo):
  (repo.path / 'governance/rules.yaml').unlink()


@pytest.mark.parametrize('spoil', [_dirty, _untracked, _missing])
def test_prompt_blocked_and_session_start_fails_when_spoiled(repo, spoil):
  spoil(repo)
  assert blocked(repo.gate('UserPromptSubmit'))
  assert repo.gate('SessionStart', source='startup').returncode == 2


def test_prompt_blocked_when_governance_never_committed(tmp_path):
  repo = Repo(tmp_path / 'fresh')
  repo.path.mkdir()
  repo.git('init', '-q', '-b', 'main')
  repo.write('governance/rules.yaml', 'rules: []\n')
  (repo.path / '.venv').symlink_to(PROJECT / '.venv')
  result = repo.gate('UserPromptSubmit')
  assert blocked(result)
  assert 'not committed' in result.stdout


# --- PreToolUse: plans and scope -------------------------------------------------------


@pytest.mark.parametrize(('plans', 'is_denied'), [(0, True), (1, False), (2, True)])
def test_edit_needs_exactly_one_plan(repo, plans, is_denied):
  for number in range(plans):
    add_plan(repo, f'000{number}-a.md')
  assert denied(repo.edit(repo.path / 'app/x.py')) is is_denied


def test_plan_files_are_editable_with_no_plan(repo):
  assert not denied(repo.edit(repo.path / 'docs/execution-plans/plan/active/0002-new.md'))


@pytest.mark.parametrize('path', ['app/deep/x.py', 'scripts/x.sh'])
def test_scope_inside_allowed(repo, path):
  add_plan(repo)
  assert not denied(repo.edit(repo.path / path))


def test_scope_outside_denied(repo):
  add_plan(repo)
  result = repo.edit(repo.path / 'README.md')
  assert denied(result)
  assert 'SCOPE-002' in result.stdout


def test_scope_outside_the_repo_denied(repo):
  add_plan(repo)
  assert denied(repo.edit('/etc/app/x.py'))


def test_scope_missing_front_matter_denied(repo):
  add_plan(repo, text='# No front matter\n')
  result = repo.edit(repo.path / 'app/x.py')
  assert denied(result)
  assert 'no YAML front matter' in result.stdout


def test_scope_path_cannot_borrow_the_plan_exemption(repo):
  assert denied(repo.edit(f'{repo.path}/docs/execution-plans/../../x'))
  add_plan(repo)
  assert denied(repo.edit(f'{repo.path}/docs/execution-plans/../../x'))


# --- Branch guard ----------------------------------------------------------------------


@pytest.mark.parametrize(
  'command',
  [
    'git commit -m x',
    'git -C . commit -m x',
    'git -c user.name=x commit -m x',
    'git status && git commit -m x',
    'git commit --amend',
  ],
)
def test_guard_denies_commit_on_main(repo, command):
  assert denied(repo.guard(command))


@pytest.mark.parametrize('command', ['git status', 'git stash push'])
def test_guard_allows_other_commands_on_main(repo, command):
  assert not denied(repo.guard(command))


@pytest.mark.parametrize(
  'command',
  ['git commit -m x', 'git commit --amend', 'git commit -m "explain -n"', "git commit -m '-n'"],
)
def test_guard_allows_commits_on_another_branch(repo, command):
  repo.git('switch', '-q', '-c', 'work')
  assert not denied(repo.guard(command))


@pytest.mark.parametrize(
  'command',
  [
    'git push',
    'git push origin main',
    'git -C . push',
    'git -c push.default=current push',
    'git status; git push',
    'git commit --no-verify -m x',
    'git commit -n -m x',
    'git commit -nm x',
    'git -C . commit -n -m x',
    'git config core.hooksPath /dev/null',
    'git config --local core.hooksPath x',
    'git config --unset core.hooksPath',
    'git -C . config core.hooksPath x',
    'git -c core.hooksPath=/dev/null commit -m x',
    'git -c CORE.HOOKSPATH=x status',
  ],
)
def test_guard_denies_on_any_branch(repo, command):
  repo.git('switch', '-q', '-c', 'work')
  assert denied(repo.guard(command))


@pytest.mark.parametrize(
  'command',
  [
    'git config core.hooksPath',
    'git config --get core.hooksPath',
    'git log --grep "git push"',
    'echo "git push"',
  ],
)
def test_guard_allows_lookalikes(repo, command):
  repo.git('switch', '-q', '-c', 'work')
  assert not denied(repo.guard(command))


# --- commit-msg, check_trailers and pre-push -------------------------------------------


def trailers(repo, plan='0001'):
  return f'm\n\nGovernance: {repo.sha()}\nPlan: {plan}\n'


def test_commit_msg_accepts_valid_trailers(repo):
  add_plan(repo)
  result = repo.commit_msg(trailers(repo))
  assert result.returncode == 0, result.stderr


def test_commit_msg_accepts_a_plan_in_completed(repo):
  repo.write('docs/execution-plans/plan/completed/0001-a.md', PLAN)
  assert repo.commit_msg(trailers(repo)).returncode == 0


@pytest.mark.parametrize(
  ('make_message', 'expected'),
  [
    (lambda _: 'm\n', 'Governance'),
    (lambda _: f'm\n\nPlan: 0001\nGovernance: {ZERO}\n', 'Governance'),
    (lambda r: f'm\n\nGovernance: {r.sha()}\n', 'Plan'),
    (lambda r: trailers(r, '9999'), 'Plan'),
    (lambda r: trailers(r, '../0001'), 'Plan'),
    (lambda r: f'm\n\nPlan: 0001\nGovernance: {ZERO}\nGovernance: {r.sha()}\n', 'Governance'),
  ],
)
def test_commit_msg_rejects_bad_trailers(repo, make_message, expected):
  add_plan(repo)
  result = repo.commit_msg(make_message(repo))
  assert result.returncode != 0
  assert expected in result.stderr


def test_commit_msg_ignores_a_plan_outside_active_and_completed(repo):
  repo.write('docs/execution-plans/plan/abandoned/0001-a.md', PLAN)
  assert repo.commit_msg(trailers(repo)).returncode != 0


def test_commit_msg_allows_the_root_commit(tmp_path):
  repo = Repo(tmp_path / 'fresh')
  repo.path.mkdir()
  repo.git('init', '-q', '-b', 'main')
  assert repo.commit_msg('first\n').returncode == 0


def test_commit_msg_on_the_commit_that_first_adds_governance(tmp_path):
  repo = Repo(tmp_path / 'fresh')
  repo.path.mkdir()
  repo.git('init', '-q', '-b', 'main')
  repo.write('docs/execution-plans/plan/active/0001-a.md', PLAN)
  repo.commit()
  repo.write('governance/rules.yaml', 'rules: []\n')
  assert repo.commit_msg('m\n\nPlan: 0001\n').returncode == 0
  assert repo.commit_msg('m\n').returncode != 0


def test_commit_changing_governance_records_its_parents_hash(repo):
  add_plan(repo)
  old = repo.sha()
  repo.write('governance/rules.yaml', 'rules: [next]\n')
  repo.git('add', '-A')
  assert repo.commit_msg(f'm\n\nGovernance: {old}\nPlan: 0001\n').returncode == 0


def test_check_trailers_compares_each_commit_with_its_parent(repo):
  add_plan(repo)
  repo.commit(trailers(repo))
  start = repo.git('rev-parse', 'HEAD')
  old = repo.sha()
  repo.write('governance/rules.yaml', 'rules: [next]\n')
  repo.commit(f'changes governance\n\nGovernance: {old}\nPlan: 0001\n')
  repo.commit(trailers(repo))
  result = repo.run(GITHOOKS / 'check_trailers.sh', f'{start}..HEAD')
  assert result.returncode == 0, result.stderr
  repo.commit('no trailers')
  assert repo.run(GITHOOKS / 'check_trailers.sh', f'{start}..HEAD').returncode != 0


def _push(repo, local, remote):
  return repo.run(GITHOOKS / 'pre-push', 'origin', 'url', stdin=f'refs/a {local} refs/b {remote}\n')


def test_pre_push_checks_an_existing_remote_branch(repo):
  add_plan(repo)
  repo.commit(trailers(repo))
  remote = repo.git('rev-parse', 'HEAD')
  repo.commit(trailers(repo))
  assert _push(repo, repo.git('rev-parse', 'HEAD'), remote).returncode == 0
  repo.commit('no trailers')
  assert _push(repo, repo.git('rev-parse', 'HEAD'), remote).returncode != 0


def test_pre_push_checks_a_new_remote_branch(repo):
  add_plan(repo)
  repo.commit('no trailers')
  result = _push(repo, repo.git('rev-parse', 'HEAD'), ZERO)
  assert result.returncode != 0
  assert 'Governance' in result.stderr


def test_pre_push_skips_a_branch_deletion(repo):
  assert _push(repo, ZERO, repo.git('rev-parse', 'HEAD')).returncode == 0
