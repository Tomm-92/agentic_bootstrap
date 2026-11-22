"""QUAL-001: a score above 1 links to evidence that exists."""

import re
from pathlib import Path

RECORDS = Path(__file__).parent.parent.parent / 'docs/records'


def problems(text, docs):
  found = []
  for area, score, evidence in re.findall(r'^\| ([^|]+) \| (\d) \| ([^|]*) \|$', text, re.M):
    links = re.findall(r'\]\(([^)]+)\)', evidence)
    if int(score) > 1 and not links:
      found.append(f'{area}: no evidence link')
    for link in links:
      path = (docs / link).resolve()
      if not path.exists():
        found.append(f'{area}: {link} does not exist')
      if 'proposals' in path.relative_to(docs.parent.parent.resolve()).parts:
        found.append(f'{area}: {link} is deleted when the proposal is applied')
  return found


def test_every_score_above_one_has_existing_evidence():
  text = (RECORDS / 'quality_score.md').read_text()
  assert len(re.findall(r'^\| [^|]+ \| \d \| ', text, re.M)) == 8
  assert problems(text, RECORDS.resolve()) == []


def test_a_score_with_no_link_fails(tmp_path):
  docs = tmp_path / 'docs'
  docs.mkdir()
  assert problems('| Area | 3 | None |\n', docs) == ['Area: no evidence link']


def test_a_score_of_one_needs_no_link(tmp_path):
  assert problems('| Area | 1 | None |\n', tmp_path) == []


def test_a_missing_path_fails(tmp_path):
  docs = tmp_path / 'docs'
  docs.mkdir()
  assert problems('| Area | 3 | [x](gone.py) |\n', docs) == ['Area: gone.py does not exist']


def test_a_link_under_proposals_fails(tmp_path):
  records = tmp_path / 'docs/records'
  records.mkdir(parents=True)
  target = tmp_path / 'proposals/0001/x.py'
  target.parent.mkdir(parents=True)
  target.write_text('x')
  found = problems('| Area | 3 | [x](../../proposals/0001/x.py) |\n', records.resolve())
  assert found == ['Area: ../../proposals/0001/x.py is deleted when the proposal is applied']
