"""The project skills and the security checklist: well formed, and citing only what exists."""

import json
import re
from pathlib import Path

import pytest
import yaml

SKILLS = sorted(Path('.claude/skills').glob('*/SKILL.md'))
CHECKLIST = Path('.claude/skills/spec-security/checklist.md')
SECURITY_RULES = {'SEC-001', 'SEC-002', 'DATA-001', 'DEP-001', 'TOOL-001', 'FS-001', 'SBX-001'}
# Backticked repo paths with a file extension. Bare names such as `checklist.md` are
# relative to something else, so they aren't checked.
REPO_PATH = re.compile(r'`([\w.-]+/[\w./-]*\.\w+)`')


@pytest.mark.parametrize('skill', SKILLS, ids=lambda p: p.parent.name)
def test_skill_has_a_name_and_description(skill):
  front = yaml.safe_load(skill.read_text().split('---\n', 2)[1])
  assert front['name'] == skill.parent.name
  assert front['description'].strip()


def test_checklist_cites_only_real_rules_and_covers_the_security_ones():
  rules = {r['id'] for r in yaml.safe_load(Path('governance/rules.yaml').read_text())['rules']}
  cited = set(re.findall(r'\b[A-Z]+-\d{3}\b', CHECKLIST.read_text()))
  assert cited <= rules
  assert cited >= SECURITY_RULES


@pytest.mark.parametrize('doc', [*SKILLS, CHECKLIST], ids=str)
def test_every_cited_repo_path_exists(doc):
  missing = [p for p in REPO_PATH.findall(doc.read_text()) if not Path(p).exists()]
  assert not missing


def test_the_built_in_security_review_is_off():
  settings = json.loads(Path('.claude/settings.json').read_text())
  assert settings['skillOverrides']['security-review'] == 'off'
