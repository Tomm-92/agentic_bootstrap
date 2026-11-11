"""The arm script's decisions. Stage 10's dry run and the owner's run cover its commands."""

from pathlib import Path

import yaml

from scripts.arm_governance import (
  CI_AND_HOOK_CONTROLS,
  COST_CONTROL,
  LEDGER,
  SANDBOX_CONTROL,
  activate,
  ci_failures,
)
from scripts.check_activation import read_ledger

RULES = """- {type: D, at: ci, by: ci check (S05), status: planned}
- {type: D, at: ci, by: other check (S05), status: planned}
"""
ROWS = """| Rule | Control | Stage | Evidence | Result | Owner check |
| --- | --- | --- | --- | --- | --- |
| A-1 | ci check (S05) | S05 | a.yml, actionlint | deferred | Jobs run on the test PR |
| A-1 | other check (S05) | S05 | b.yml | deferred | Jobs run on the test PR |
"""


def _job(name, *conclusions):
  steps = [{'name': f'step {i}', 'conclusion': c} for i, c in enumerate(conclusions)]
  return {'name': name, 'steps': steps}


def test_activate_changes_only_the_named_control():
  rules, ledger = activate(RULES, ROWS, [('A-1', 'ci check (S05)')], '2026-11-09')
  assert 'by: ci check (S05), status: active' in rules
  assert 'by: other check (S05), status: planned' in rules
  rows = read_ledger(ledger)
  assert rows['A-1', 'ci check (S05)'] == ('pass', 'Confirmed by the owner, 2026-11-09')
  assert rows['A-1', 'other check (S05)'] == ('deferred', 'Jobs run on the test PR')


def test_every_control_it_activates_changes_in_the_real_catalogue_and_ledger():
  controls = [*CI_AND_HOOK_CONTROLS, SANDBOX_CONTROL, COST_CONTROL]
  rules, ledger = activate(
    Path('governance/rules.yaml').read_text(), LEDGER.read_text(), controls, '2026-11-09'
  )
  statuses = {
    (rule['id'], control['by']): control['status']
    for rule in yaml.safe_load(rules)['rules']
    for control in rule['controls']
  }
  rows = read_ledger(ledger)
  for control in controls:
    assert statuses[control] == 'active'
    assert rows[control] == ('pass', 'Confirmed by the owner, 2026-11-09')


def test_passing_and_skipped_steps_are_clean():
  assert ci_failures([_job('checks', 'success', 'skipped')], ['checks']) == []


def test_a_failed_step_fails_even_when_the_job_reports_success():
  job = {**_job('secrets', 'success', 'failure'), 'conclusion': 'success'}
  assert 'secrets: step "step 1" ended failure' in ci_failures([job], ['secrets'])


def test_a_required_job_that_did_not_run_fails():
  assert ci_failures([], ['dependencies']) == ['dependencies: did not run']
  assert ci_failures([_job('dependencies')], ['dependencies']) == ['dependencies: did not run']


def test_only_the_ignored_step_may_fail():
  job = {
    'name': 'governance',
    'steps': [
      {'name': 'Commit trailers', 'conclusion': 'failure'},
      {'name': 'Rule and profile schema tests', 'conclusion': 'failure'},
    ],
  }
  assert ci_failures([job], ['governance'], ignored_step='Commit trailers') == [
    'governance: step "Rule and profile schema tests" ended failure'
  ]
