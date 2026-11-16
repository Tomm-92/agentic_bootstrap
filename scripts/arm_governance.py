"""Owner-only: applies the proposal, merges it and activates only what its checks prove.

Usage, from the owner's own terminal: .venv/bin/python -m scripts.arm_governance <command>

  apply    Check and apply the proposal on the branch. Stage 10's dry run uses this alone.
  arm      Apply, push, run the test PR, turn on the git hooks, activate and merge to main.
  sandbox  Activate the GOV-002 sandbox control, once a new session has shown the refusals.
  paid     Run the Stage 6 checks with ANTHROPIC_API_KEY set, then activate COST-001 runtime.

Every command stops at the first failure, and running it again resumes.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from scripts.check_activation import problems, read_ledger

REPO = Path(__file__).parent.parent
RULES = REPO / 'governance/rules.yaml'
LEDGER = REPO / 'docs/governance-activation.md'
PROPOSAL = 'proposals/0001'
BASE = 'governance_implementation'
BRANCH = 'governance_bootstrap'
PYTEST = '.venv/bin/pytest'
CI_POLL_SECONDS = 15
CI_TIMEOUT_SECONDS = 1800
# The jobs use continue-on-error, so a green workflow doesn't prove a job passed.
WORKFLOW_JOBS = {'checks': ['checks'], 'governance': ['governance', 'secrets', 'dependencies']}

Control = tuple[str, str]
CI_AND_HOOK_CONTROLS: list[Control] = [
  ('GOV-004', 'governance workflow trailer check (S05)'),
  ('SEC-002', 'gitleaks in the governance workflow (S05)'),
  ('DEP-001', 'vulnerability audit and osv-scanner (S05, A02)'),
  ('GOV-004', '.githooks/commit-msg (S04)'),
  ('EVID-001', 'Governance and Plan trailers enforced by commit-msg (S04)'),
]
SANDBOX_CONTROL: Control = (
  'GOV-002',
  'Claude Code sandbox blocks indirect writes to protected paths (S04)',
)
COST_CONTROL: Control = ('COST-001', 'governance layer enforces session_token_budget (S06)')


class ArmError(Exception):
  """A check failed, so nothing further may be armed."""


def run(*args: str, stdin: str | None = None) -> str:
  """Runs a command from the repo root and returns its output."""
  result = subprocess.run(  # noqa: S603 - fixed commands; the owner runs this script
    args, cwd=REPO, input=stdin, stdout=subprocess.PIPE, text=True, check=True
  )
  return result.stdout.strip()


def say(message: str) -> None:
  sys.stdout.write(f'{message}\n')
  sys.stdout.flush()


def commit(message: str) -> None:
  governance = run('git', 'rev-parse', 'HEAD:governance')
  run(
    'git',
    'commit',
    '-m',
    message,
    '--trailer',
    f'Governance: {governance}',
    '--trailer',
    'Plan: 0001',
  )


def activate(rules: str, ledger: str, controls: list[Control], today: str) -> tuple[str, str]:
  """Returns the rules and ledger text with these controls active and confirmed by the owner."""
  for rule_id, control in controls:
    # YAML quotes a name holding a comma.
    planned = rf"(by: '?{re.escape(control)}'?, status: )planned"
    rules = re.sub(planned, r'\1active', rules)
    names = rf'\| {re.escape(rule_id)} \| {re.escape(control)}'
    row = rf'^({names} \| [^|]* \| [^|]* \|) [a-z]+ \| [^|]* \|$'
    ledger = re.sub(row, rf'\1 pass | Confirmed by the owner, {today} |', ledger, flags=re.M)
  return rules, ledger


def commit_controls(controls: list[Control], message: str) -> None:
  """Activates controls in one commit, after the activation check accepts them."""
  old_rules = RULES.read_text()
  rules, ledger = activate(old_rules, LEDGER.read_text(), controls, date.today().isoformat())
  proposed = yaml.safe_load(rules)['rules']
  active = {(r['id'], c['by']) for r in proposed for c in r['controls'] if c['status'] == 'active'}
  found = [
    f'{rule}: "{name}" did not become active'
    for rule, name in controls
    if (rule, name) not in active
  ]
  found += problems(yaml.safe_load(old_rules)['rules'], proposed, read_ledger(ledger))
  if found:
    raise ArmError('\n'.join(found))
  if rules == old_rules:
    return
  RULES.write_text(rules)
  LEDGER.write_text(ledger)
  run('git', 'add', str(RULES), str(LEDGER))
  commit(message)


def ci_failures(
  jobs: list[dict[str, Any]], required: list[str], ignored_step: str | None = None
) -> list[str]:
  """Returns what failed in a workflow run. A required job that didn't run counts."""
  steps = {job['name']: job['steps'] for job in jobs}
  missing = [f'{name}: did not run' for name in required if not steps.get(name)]
  return missing + [
    f'{name}: step "{step["name"]}" ended {step["conclusion"]}'
    for name, job_steps in steps.items()
    for step in job_steps
    if step['conclusion'] not in ('success', 'skipped') and step['name'] != ignored_step
  ]


def _finished_run(sha: str, workflow: str) -> str:
  listing = ('gh', 'run', 'list', '--commit', sha, '--workflow', workflow, '--event')
  fields = ('pull_request', '--json', 'databaseId,status')
  deadline = time.monotonic() + CI_TIMEOUT_SECONDS
  while time.monotonic() < deadline:
    runs = json.loads(run(*listing, *fields))
    if runs and runs[0]['status'] == 'completed':
      return str(runs[0]['databaseId'])
    time.sleep(CI_POLL_SECONDS)
  raise ArmError(f'{workflow} did not finish on {sha}')


def await_ci(sha: str, ignored_step: str | None = None) -> None:
  """Waits for CI on a commit, and fails unless every job's steps passed."""
  found: list[str] = []
  for workflow, required in WORKFLOW_JOBS.items():
    say(f'Waiting for {workflow} on {sha[:7]}')
    run_id = _finished_run(sha, workflow)
    jobs = json.loads(run('gh', 'run', 'view', run_id, '--json', 'jobs'))['jobs']
    found += [f'{workflow}/{problem}' for problem in ci_failures(jobs, required, ignored_step)]
  if found:
    raise ArmError('\n'.join(found))


def pr_state(head: str) -> str:
  return run(
    'gh', 'pr', 'list', '--head', head, '--state', 'all', '--json', 'state', '-q', '.[0].state'
  )


def require_clean() -> None:
  if run('git', 'status', '--porcelain'):
    raise ArmError('The working tree has uncommitted changes.')


def apply_proposal() -> None:
  """Applying arms every open session, and the gate blocks prompts until the commit lands."""
  require_clean()
  if not (REPO / PROPOSAL).exists():
    return
  run(sys.executable, 'scripts/check_activation.py', f'{PROPOSAL}/governance/rules.yaml')
  run('cp', '-R', f'{PROPOSAL}/.', '.')
  shutil.rmtree(REPO / PROPOSAL)
  run('git', 'add', '-A')
  commit('Apply governance proposal')
  run(PYTEST)
  say('The proposal is applied and the tests pass.')


def prove_git_hooks() -> None:
  run('git', 'config', 'core.hooksPath', '.githooks')
  attempt = ('git', 'commit', '--allow-empty', '-m', 'This should be refused')
  refused = subprocess.run(attempt, cwd=REPO, capture_output=True, check=False)  # noqa: S603 - fixed command
  if refused.returncode == 0:
    run('git', 'reset', '--soft', 'HEAD~1')
    raise ArmError('A commit with no trailers was accepted, so the git hooks are not running.')


def merge_bootstrap() -> None:
  run('git', 'switch', BRANCH)
  apply_proposal()
  if key := os.environ.get('REVIEWER_API_KEY'):
    run('gh', 'secret', 'set', 'ANTHROPIC_API_KEY', stdin=key)
  # Before the hooks are on: pre-push would refuse the base branch's older commits.
  run('git', 'push', '-u', 'origin', BASE)
  run('git', 'push', '-u', 'origin', BRANCH)
  if pr_state(BRANCH) != 'OPEN':
    title = 'Governance bootstrap'
    run('gh', 'pr', 'create', '--base', BASE, '--head', BRANCH, '--title', title, '--body', title)
  await_ci(run('git', 'rev-parse', 'HEAD'))
  prove_git_hooks()
  commit_controls(CI_AND_HOOK_CONTROLS, 'Activate the CI and git hook controls')
  run(PYTEST)
  run('git', 'push')
  await_ci(run('git', 'rev-parse', 'HEAD'))
  run('gh', 'pr', 'merge', BRANCH, '--merge')


def merge_base() -> None:
  if pr_state(BASE) != 'OPEN':
    title = 'Governance instructions and bootstrap'
    run('gh', 'pr', 'create', '--base', 'main', '--head', BASE, '--title', title, '--body', title)
  run('git', 'fetch', 'origin')
  # The base branch's own commits and GitHub's merge commit predate the trailer rule.
  await_ci(run('git', 'rev-parse', f'origin/{BASE}'), ignored_step='Commit trailers')
  run('gh', 'pr', 'merge', BASE, '--merge')


def arm() -> None:
  say('This pushes, merges to main and arms the controls. Do this only after reviewing the branch.')
  if input('Type arm to continue: ') != 'arm':
    raise ArmError('Nothing was changed.')
  require_clean()
  if pr_state(BRANCH) != 'MERGED':
    merge_bootstrap()
  if pr_state(BASE) != 'MERGED':
    merge_base()
  run('git', 'fetch', 'origin')
  run('git', 'switch', 'main')
  run('git', 'pull', '--ff-only', 'origin', 'main')
  run(PYTEST)
  if run('git', 'rev-parse', 'HEAD:governance') != run(
    'git', 'rev-parse', 'origin/main:governance'
  ):
    raise ArmError('The local and remote governance hashes differ.')
  say('Armed. Next: start a new session and run the refusal check in "After the run" step 3.')


def activate_by_pr(branch: str, control: Control, message: str) -> None:
  """main changes only through a PR, so a later activation goes on its own branch."""
  require_clean()
  run('git', 'switch', '-c', branch)
  commit_controls([control], message)
  run(PYTEST)
  run('git', 'push', '-u', 'origin', branch)
  run('gh', 'pr', 'create', '--base', 'main', '--fill')
  await_ci(run('git', 'rev-parse', 'HEAD'))
  run('gh', 'pr', 'merge', '--merge', '--delete-branch')
  run('git', 'switch', 'main')
  run('git', 'pull', '--ff-only', 'origin', 'main')
  say(f'{control[0]} is active: {control[1]}')


def sandbox() -> None:
  activate_by_pr('activate-sandbox', SANDBOX_CONTROL, 'Activate the sandbox control')


def paid() -> None:
  if not os.environ.get('ANTHROPIC_API_KEY'):
    raise ArmError('ANTHROPIC_API_KEY is not set in this terminal.')
  run(sys.executable, '-m', 'scripts.local_session', '--real', 'What is the status of demo?')
  run(PYTEST, '-m', 'integration')
  activate_by_pr('activate-cost-runtime', COST_CONTROL, 'Activate the COST-001 runtime control')


if __name__ == '__main__':
  commands = {'apply': apply_proposal, 'arm': arm, 'sandbox': sandbox, 'paid': paid}
  try:
    commands[sys.argv[1]]()
  except ArmError as error:
    sys.exit(f'Stopped: {error}')
  except subprocess.CalledProcessError as error:
    sys.exit(f'{error.stdout}\nStopped: {" ".join(error.cmd)} failed.')
