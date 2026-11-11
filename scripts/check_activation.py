"""Checks a proposed rules.yaml: only proven controls may become active, and nothing else moves."""

import sys
from pathlib import Path
from typing import Any

import yaml

Rule = dict[str, Any]
Ledger = dict[tuple[str, str], tuple[str, str]]


def read_ledger(text: str) -> Ledger:
  """Maps (rule, control) to (result, owner check)."""
  rows = [line.strip('| ').split(' | ') for line in text.splitlines() if line.startswith('| ')]
  return {(row[0], row[1]): (row[4], row[5]) for row in rows[2:]}


def _proven(rule_id: str, control: dict[str, str], ledger: Ledger) -> str | None:
  row = ledger.get((rule_id, control['by']))
  if row is None:
    return f'{rule_id}: "{control["by"]}" is active with no ledger row'
  result, owner_check = row
  if result != 'pass':
    return f'{rule_id}: "{control["by"]}" is active, but its ledger result is {result}'
  if owner_check != 'none' and not owner_check.lower().startswith('confirmed'):
    return f'{rule_id}: "{control["by"]}" is active, but its owner check is open: {owner_check}'
  return None


def _compare_rule(old: Rule, new: Rule, ledger: Ledger) -> list[str]:
  rule_id = old['id']
  fields = {k: v for k, v in old.items() if k != 'controls'}
  if fields != {k: v for k, v in new.items() if k != 'controls'}:
    return [f'{rule_id}: a field other than a control status changed']
  if len(old['controls']) != len(new['controls']):
    return [f'{rule_id}: a control was added or removed']
  found: list[str | None] = []
  for before, after in zip(old['controls'], new['controls'], strict=True):
    if {**before, 'status': ''} != {**after, 'status': ''}:
      found.append(f'{rule_id}: "{before["by"]}" changed beyond its status')
    elif before['status'] == after['status']:
      continue
    elif after['status'] != 'active':
      found.append(f'{rule_id}: "{before["by"]}" moved from active to {after["status"]}')
    else:
      found.append(_proven(rule_id, after, ledger))
  return [problem for problem in found if problem]


def _check_new_rule(rule: Rule, ledger: Ledger) -> list[str]:
  if not any(row_rule == rule['id'] for row_rule, _ in ledger):
    return [f'{rule["id"]}: a new rule needs a ledger row']
  active = [c for c in rule['controls'] if c['status'] == 'active']
  return [p for c in active if (p := _proven(rule['id'], c, ledger))]


def problems(current: list[Rule], proposed: list[Rule], ledger: Ledger) -> list[str]:
  """Returns everything that stops the proposal being applied."""
  old = {rule['id']: rule for rule in current}
  new = {rule['id']: rule for rule in proposed}
  found = [f'{rule_id}: the rule was removed' for rule_id in old.keys() - new.keys()]
  for rule_id, rule in new.items():
    if rule_id in old:
      found += _compare_rule(old[rule_id], rule, ledger)
    else:
      found += _check_new_rule(rule, ledger)
  found += [
    f'{rule["id"]}: "{control["by"]}" is planned with no ledger row'
    for rule in proposed
    for control in rule['controls']
    if control['status'] == 'planned' and (rule['id'], control['by']) not in ledger
  ]
  return found


if __name__ == '__main__':
  repo = Path(__file__).parent.parent
  found = problems(
    yaml.safe_load((repo / 'governance/rules.yaml').read_text())['rules'],
    yaml.safe_load(Path(sys.argv[1]).read_text())['rules'],
    read_ledger((repo / 'docs/governance-activation.md').read_text()),
  )
  sys.stderr.write(''.join(f'{problem}\n' for problem in found))
  sys.stdout.write('The proposal passes.\n' if not found else '')
  sys.exit(1 if found else 0)
