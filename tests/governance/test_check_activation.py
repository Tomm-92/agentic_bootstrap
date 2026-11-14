"""The activation check, on its own small catalogue: the real one changes when applied."""

import copy
from typing import Any

from scripts.check_activation import problems, read_ledger

CATALOGUE: list[dict[str, Any]] = [
  {
    'id': 'A-1',
    'applies_to': ['build'],
    'rule': 'r',
    'because': 'b',
    'tier': 'deny',
    'kind': 'safety',
    'controls': [
      {'type': 'D', 'at': 'session', 'by': 'proven', 'status': 'planned'},
      {'type': 'D', 'at': 'commit', 'by': 'unproven', 'status': 'planned'},
      {'type': 'H', 'at': 'merge', 'by': 'owner check open', 'status': 'planned'},
      {'type': 'H', 'at': 'merge', 'by': 'confirmed by owner', 'status': 'planned'},
      {'type': 'H', 'at': 'merge', 'by': 'already active', 'status': 'active'},
    ],
  }
]
LEDGER = read_ledger(
  """| Rule | Control | Stage | Evidence | Result | Owner check |
| --- | --- | --- | --- | --- | --- |
| A-1 | proven | S01 | test | pass | none |
| A-1 | unproven | S01 | test | deferred | none |
| A-1 | owner check open | S01 | test | pass | After the run step 6 |
| A-1 | confirmed by owner | S01 | test | pass | Confirmed by the owner, 2026-11-09 |
"""
)


def _activate(position):
  proposed = copy.deepcopy(CATALOGUE)
  proposed[0]['controls'][position]['status'] = 'active'
  return proposed


def test_no_change_passes():
  assert problems(CATALOGUE, copy.deepcopy(CATALOGUE), LEDGER) == []


def test_a_proven_activation_passes():
  assert problems(CATALOGUE, _activate(0), LEDGER) == []


def test_an_activation_the_owner_confirmed_passes():
  assert problems(CATALOGUE, _activate(3), LEDGER) == []


def test_an_unproven_activation_fails():
  assert 'deferred' in problems(CATALOGUE, _activate(1), LEDGER)[0]


def test_an_open_owner_check_fails():
  assert 'owner check is open' in problems(CATALOGUE, _activate(2), LEDGER)[0]


def test_a_rule_field_change_fails():
  proposed = copy.deepcopy(CATALOGUE)
  proposed[0]['tier'] = 'confirm'
  assert 'other than a control status' in problems(CATALOGUE, proposed, LEDGER)[0]


def test_a_removed_control_fails():
  proposed = copy.deepcopy(CATALOGUE)
  del proposed[0]['controls'][1]
  assert 'added or removed' in problems(CATALOGUE, proposed, LEDGER)[0]


def test_a_removed_rule_fails():
  assert 'removed' in problems(CATALOGUE, [], LEDGER)[0]


def test_a_changed_control_fails():
  proposed = copy.deepcopy(CATALOGUE)
  proposed[0]['controls'][0]['type'] = 'ND'
  assert 'beyond its status' in problems(CATALOGUE, proposed, LEDGER)[0]


def test_moving_a_control_back_to_planned_fails():
  proposed = copy.deepcopy(CATALOGUE)
  proposed[0]['controls'][4]['status'] = 'planned'
  found = problems(CATALOGUE, proposed, LEDGER)
  assert any('from active to planned' in problem for problem in found)


def test_a_planned_control_with_no_ledger_row_fails():
  ledger = {k: v for k, v in LEDGER.items() if k[1] != 'unproven'}
  assert 'no ledger row' in problems(CATALOGUE, copy.deepcopy(CATALOGUE), ledger)[0]


def _new_rule(status):
  control = {'type': 'D', 'at': 'ci', 'by': 'new control', 'status': status}
  return {**CATALOGUE[0], 'id': 'B-1', 'controls': [control]}


def test_a_new_rule_with_a_proven_ledger_row_passes():
  ledger = {**LEDGER, ('B-1', 'new control'): ('pass', 'none')}
  assert problems(CATALOGUE, [*CATALOGUE, _new_rule('active')], ledger) == []


def test_a_new_rule_with_no_ledger_row_fails():
  found = problems(CATALOGUE, [*CATALOGUE, _new_rule('planned')], LEDGER)
  assert 'needs a ledger row' in found[0]


def test_a_new_rule_with_an_unproven_active_control_fails():
  ledger = {**LEDGER, ('B-1', 'new control'): ('deferred', 'none')}
  assert 'deferred' in problems(CATALOGUE, [*CATALOGUE, _new_rule('active')], ledger)[0]
