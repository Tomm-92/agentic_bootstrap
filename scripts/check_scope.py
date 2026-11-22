"""SCOPE-002 in CI: each commit changes only paths inside the scope_paths of the plan it names.

The arguments are a rev-list range. Merge and root commits are skipped, and so are commits
whose plan can't be found, because the trailer check already reports those.
"""

import subprocess
import sys
from fnmatch import fnmatch

import yaml


def _git(*args: str) -> str:
  result = subprocess.run(['git', *args], capture_output=True, text=True, check=True)  # noqa: S603, S607 - fixed git commands
  return result.stdout


def out_of_scope(globs: list[str], proposed: set[str], changed: list[str]) -> list[str]:
  """Returns the changed paths outside the plan's scope.

  `proposed` holds the paths the plan's proposal folder covers, so the owner's commit
  applying a proposal passes. `fnmatch` matches as governance_gate.sh does.
  """
  return [
    path
    for path in changed
    if not path.startswith('docs/execution-plans/')
    and path not in proposed
    and not any(fnmatch(path, glob) for glob in globs)
  ]


def _plan_globs(commit: str, plan_id: str) -> list[str] | None:
  plan_folders = ('docs/execution-plans/plan/active', 'docs/execution-plans/plan/completed')
  for path in _git('ls-tree', '-r', '--name-only', commit, '--', *plan_folders).split():
    if fnmatch(path, f'docs/execution-plans/plan/*/{plan_id}-*.md'):
      front = _git('show', f'{commit}:{path}').split('---\n', 2)[1]
      return list(yaml.safe_load(front)['scope_paths'])
  return None


def problems(rev_range: list[str]) -> list[str]:
  """Returns one line for each changed path outside its commit's plan scope."""
  found = []
  for commit in _git('rev-list', '--min-parents=1', '--max-parents=1', *rev_range).split():
    plan_id = _git('log', '-1', '--format=%(trailers:key=Plan,valueonly)', commit).strip()
    globs = _plan_globs(commit, plan_id) if plan_id.isalnum() else None
    if globs is None:
      continue
    prefix = f'proposals/{plan_id}/'
    # The parent covers a proposal deleted as it is applied, the commit one added alongside.
    listed = [
      _git('ls-tree', '-r', '--name-only', tree, '--', prefix).splitlines()
      for tree in (f'{commit}^', commit)
    ]
    proposed = {path.removeprefix(prefix) for paths in listed for path in paths}
    changed = _git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).splitlines()
    found += [
      f'{commit[:12]} (plan {plan_id}): {path} is outside its scope_paths'
      for path in out_of_scope(globs, proposed, changed)
    ]
  return found


if __name__ == '__main__':
  found = problems(sys.argv[1:])
  sys.stderr.write(''.join(f'{problem}\n' for problem in found))
  sys.exit(1 if found else 0)
