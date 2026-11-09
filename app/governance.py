"""The runtime governance layer: fail closed, stamp evidence, re-inject rules, enforce budgets."""

import subprocess
from pathlib import Path
from typing import Any, override

import yaml
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.genai import types

SHA_KEY = 'governance_sha'
TOKENS_KEY = 'governance_tokens'


class GovernanceError(RuntimeError):
  """Governance is missing or dirty, or a model response can't be accounted for."""


def _git(repo: Path, *args: str) -> str:
  try:
    result = subprocess.run(  # noqa: S603 - fixed git commands
      ['git', '-C', str(repo), *args],  # noqa: S607 - git comes from PATH
      capture_output=True,
      text=True,
      check=True,
    )
  except (subprocess.CalledProcessError, FileNotFoundError) as error:
    raise GovernanceError(f'git {args[0]} failed in {repo}: {error}') from error
  return result.stdout.strip()


def governance_hash(repo: Path) -> str:
  """Returns the committed governance hash, or raises while governance is unusable."""
  sha = _git(repo, 'rev-parse', '-q', '--verify', 'HEAD:governance')
  if _git(repo, 'status', '--porcelain', '--', 'governance'):
    raise GovernanceError(f'{repo}/governance has uncommitted changes')
  return sha


def _load(repo: Path, name: str) -> dict[str, Any]:
  loaded: dict[str, Any] = yaml.safe_load((repo / 'governance' / name).read_text())
  return loaded


def _refusal(text: str) -> types.Content:
  return types.Content(role='model', parts=[types.Part(text=text)])


class GovernancePlugin(BasePlugin):
  """Attached to the App, so it covers every agent in the tree."""

  def __init__(self, repo: Path) -> None:
    super().__init__(name='governance')
    self.repo = repo
    self.sha = governance_hash(repo)
    self.budget: int = _load(repo, 'thresholds.yaml')['session_token_budget']
    self.profile = _load(repo, 'profile.yaml')
    runtime_rules = [
      f'{r["id"]}: {r["rule"]}. Because: {r["because"]}'
      for r in _load(repo, 'rules.yaml')['rules']
      if 'runtime' in r['applies_to']
    ]
    self.rules_text = f'Governance rules in effect ({self.sha}):\n' + '\n'.join(runtime_rules)

  @override
  async def before_run_callback(
    self, *, invocation_context: InvocationContext
  ) -> types.Content | None:
    del invocation_context  # Required by BasePlugin's signature.
    try:
      sha = governance_hash(self.repo)
    except GovernanceError as error:
      return _refusal(f'GOV-005: refused, governance is unusable: {error}')
    if sha != self.sha:
      return _refusal(f'GOV-005: refused, governance changed from {self.sha} to {sha}. Restart.')
    return None

  @override
  async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
  ) -> Event | None:
    del invocation_context  # Required by BasePlugin's signature.
    event.custom_metadata = {**(event.custom_metadata or {}), SHA_KEY: self.sha}
    event.actions.state_delta[SHA_KEY] = self.sha
    return None

  @override
  async def before_model_callback(
    self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> LlmResponse | None:
    tokens = callback_context.state.get(TOKENS_KEY, 0)
    if tokens >= self.budget:
      message = f'COST-001: refused, the session used {tokens} of {self.budget} tokens.'
      return LlmResponse(content=_refusal(message))
    llm_request.append_instructions([self.rules_text])
    return None

  @override
  async def after_model_callback(
    self, *, callback_context: CallbackContext, llm_response: LlmResponse
  ) -> LlmResponse | None:
    if llm_response.partial:
      return None
    usage = llm_response.usage_metadata
    if usage is None or usage.total_token_count is None:
      raise GovernanceError('COST-001: the model response has no token count')
    tokens = callback_context.state.get(TOKENS_KEY, 0) + usage.total_token_count
    callback_context.state[TOKENS_KEY] = tokens
    return None
