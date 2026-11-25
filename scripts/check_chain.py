"""The intent -> spec -> plan chain in CI: each plan a range adds links an accepted intent and spec.

The argument is a rev-list range. Files are read at its last commit. A plan moved from
active/ to completed/ is a rename, not an addition.
"""

import posixpath
import re
import subprocess
import sys
from collections.abc import Callable

PLACEHOLDER = 'Accepted by: <owner>, <YYYY-MM-DD>'
TEMPLATE_POLICY = 'its report on this spec, pasted in'
# Earlier plans predate the chain (0001 to 0016), the spec-security report (to 0025) or
# the current folder depth. main predates the docs move, so its PRs add them all anew.
FIRST_CHECKED = 26


def _git(*args: str) -> subprocess.CompletedProcess[str]:
  return subprocess.run(['git', *args], capture_output=True, text=True, check=False)  # noqa: S603, S607 - fixed git commands


def _accepted(text: str) -> bool:
  lines = text.splitlines()
  accepted_by = [line for line in lines if line.startswith('Accepted by:')]
  return 'Status: accepted' in lines and bool(accepted_by) and PLACEHOLDER not in accepted_by


def plan_problems(plan: str, read: Callable[[str], str | None]) -> list[str]:
  """Returns what is wrong with one plan. `read` returns a repo file's text, or None."""
  text = read(plan) or ''
  none = re.search(r'^Intent: none \((.*)\)', text, re.M)
  if none and none[1].strip() not in ('', '<reason>'):
    return []
  found = []
  for kind in ('Intent', 'Spec'):
    link = re.search(rf'^{kind}: \[[^\]]*\]\(([^)]+)\)', text, re.M)
    if not link:
      found.append(f'needs a {kind}: link, or Intent: none (<reason>)')
      continue
    path = posixpath.normpath(posixpath.join(posixpath.dirname(plan), link[1]))
    linked = read(path)
    if linked is None:
      found.append(f'{kind} link {link[1]} names no file')
    elif not _accepted(linked):
      found.append(f'{path} needs Status: accepted and an Accepted by: line from the owner')
    elif kind == 'Spec':
      policies = linked.partition('## Policies checked')[2].split('\n## ')[0]
      if 'spec-security' not in policies or TEMPLATE_POLICY in policies:
        found.append(f'{path} needs the spec-security report under Policies checked')
  return found


def problems(rev_range: str) -> list[str]:
  """Returns one line per problem in the plans the range adds."""
  head = rev_range.split('..')[-1] or 'HEAD'

  def read(path: str) -> str | None:
    result = _git('show', f'{head}:{path}')
    return result.stdout if result.returncode == 0 else None

  folder = 'docs/execution-plans/plan/'
  added = _git('diff', '--name-only', '--diff-filter=A', '--find-renames', rev_range, '--', folder)
  ids = {
    path: re.match(r'(\d+)-.*\.md$', posixpath.basename(path)) for path in added.stdout.split()
  }
  plans = [path for path, id_ in ids.items() if id_ and int(id_[1]) >= FIRST_CHECKED]
  return [f'{plan}: {problem}' for plan in plans for problem in plan_problems(plan, read)]


if __name__ == '__main__':
  found = problems(sys.argv[1])
  sys.stderr.write(''.join(f'{problem}\n' for problem in found))
  sys.exit(1 if found else 0)
