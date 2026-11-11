"""GOV-003: the rule catalogue and profile are well formed."""

from pathlib import Path

import pytest
import yaml

GOVERNANCE = Path(__file__).parent.parent.parent / 'governance'
RULES = yaml.safe_load((GOVERNANCE / 'rules.yaml').read_text())['rules']
PROFILE = yaml.safe_load((GOVERNANCE / 'profile.yaml').read_text())
AGENT_KEYS = {
  'path',
  'framework',
  'output_root',
  'purpose',
  'output',
  'intent_artifact',
  'tools',
  'verification',
  'package_ecosystems',
  'external_targets',
}
by_id = pytest.mark.parametrize('rule', RULES, ids=[r['id'] for r in RULES])


def test_rule_ids_are_unique():
  ids = [r['id'] for r in RULES]
  assert len(ids) == len(set(ids))


@by_id
def test_rule_fields(rule):
  assert set(rule) == {'id', 'applies_to', 'rule', 'because', 'tier', 'kind', 'controls'}
  assert rule['because'].strip()
  assert rule['applies_to']
  assert set(rule['applies_to']) <= {'build', 'runtime'}
  assert rule['tier'] in {'free', 'confirm', 'deny'}
  assert rule['kind'] in {'safety', 'capability'}
  assert rule['controls']


@by_id
def test_control_fields(rule):
  for control in rule['controls']:
    assert set(control) == {'type', 'at', 'by', 'status'}, control
    assert control['type'] in {'D', 'ND', 'H'}
    assert control['status'] in {'active', 'planned'}


@by_id
def test_tier_has_the_control_it_needs(rule):
  types = {c['type'] for c in rule['controls']}
  if rule['tier'] == 'deny':
    assert 'D' in types
  if rule['tier'] == 'confirm':
    assert 'H' in types


def test_profile_has_every_key():
  assert set(PROFILE) == {'project', 'product_agent'}
  assert set(PROFILE['product_agent']) == AGENT_KEYS


def test_bootstrap_keys_are_filled():
  agent = PROFILE['product_agent']
  assert PROFILE['project']
  assert agent['path']
  assert agent['framework']
  assert agent['output_root']
