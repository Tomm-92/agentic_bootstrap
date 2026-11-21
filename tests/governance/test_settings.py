"""GOV-002 and COST-001: the settings deny every protected path, keep code quality's controls
and sandbox, and ask before paid-model runs."""

import json
import os
import re
from pathlib import Path

import pytest

PROJECT = Path(__file__).parent.parent.parent
SETTINGS = json.loads(
  Path(os.environ.get('SETTINGS_PATH', PROJECT / '.claude/settings.json')).read_text()
)

PROTECTED = {
  'Edit(/governance/**)': './governance',
  'Edit(/docs/governance_implementation.md)': './docs/governance_implementation.md',
  'Edit(/docs/agent_governance_implementation.md)': './docs/agent_governance_implementation.md',
  'Edit(/docs/aws_hosting_implementation.md)': './docs/aws_hosting_implementation.md',
  'Edit(/.claude/settings.json)': './.claude/settings.json',
  'Edit(/.claude/settings.local.json)': './.claude/settings.local.json',
  'Edit(/.claude/hooks/**)': './.claude/hooks',
  'Edit(/.github/**)': './.github',
  'Edit(/.githooks/**)': './.githooks',
  'Edit(/AGENTS.md)': './AGENTS.md',
  'Edit(/CLAUDE.md)': './CLAUDE.md',
  'Edit(/app/AGENTS.md)': './app/AGENTS.md',
  'Edit(/app/CLAUDE.md)': './app/CLAUDE.md',
  'Edit(/ruff.toml)': './ruff.toml',
  'Edit(/pytest.ini)': './pytest.ini',
  'Edit(/mypy.ini)': './mypy.ini',
}
CODE_QUALITY_DENY = [
  'Edit(/.github/workflows/**)',
  'Read(**/.env)',
]


def _commands(event):
  return [hook['command'] for group in SETTINGS['hooks'][event] for hook in group['hooks']]


def _matched(event, matcher):
  return [
    hook['command']
    for group in SETTINGS['hooks'][event]
    if group.get('matcher') == matcher
    for hook in group['hooks']
  ]


@pytest.mark.parametrize('rule', PROTECTED)
def test_protected_path_has_a_deny_rule(rule):
  assert rule in SETTINGS['permissions']['deny']


@pytest.mark.parametrize('path', PROTECTED.values())
def test_protected_path_is_denied_by_the_sandbox(path):
  assert path in SETTINGS['sandbox']['filesystem']['denyWrite']


def test_sandbox_paths_are_relative_to_the_project():
  assert all(p.startswith('./') for p in SETTINGS['sandbox']['filesystem']['denyWrite'])


def test_sandbox_has_no_escape():
  sandbox = SETTINGS['sandbox']
  assert sandbox['enabled'] is True
  assert sandbox['failIfUnavailable'] is True
  assert sandbox['allowUnsandboxedCommands'] is False
  assert 'excludedCommands' not in sandbox


@pytest.mark.parametrize('rule', [*CODE_QUALITY_DENY, 'Bash(git push:*)'])
def test_other_deny_rules_are_kept(rule):
  assert rule in SETTINGS['permissions']['deny']


@pytest.mark.parametrize(
  'rule',
  [
    'Bash(*pytest* -m integration*)',
    'Bash(*local_session*--real*)',
    'Bash(*adk run*)',
    'Bash(*adk web*)',
  ],
)
def test_paid_model_runs_ask_first(rule):
  assert rule in SETTINGS['permissions']['ask']


def test_code_quality_hooks_are_kept():
  assert any('lint_on_edit.sh' in c for c in _matched('PostToolUse', 'Edit|Write'))
  assert any('checks_on_stop.sh' in c for c in _commands('Stop'))


def test_governance_hooks_are_wired():
  assert any('governance_gate.sh' in c for c in _commands('SessionStart'))
  assert any('governance_gate.sh' in c for c in _commands('UserPromptSubmit'))
  assert any('governance_gate.sh' in c for c in _matched('PreToolUse', 'Edit|Write|NotebookEdit'))
  assert any('branch_guard.sh' in c for c in _matched('PreToolUse', 'Bash'))


def test_every_hook_script_exists():
  commands = [c for event in SETTINGS['hooks'] for c in _commands(event)]
  assert commands
  for command in commands:
    name = re.fullmatch(r'"\$CLAUDE_PROJECT_DIR"/\.claude/hooks/(\S+\.sh)', command)
    assert name, command
    assert (PROJECT / '.claude/hooks' / name[1]).exists(), command
