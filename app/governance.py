"""The runtime governance layer: fail closed, stamp evidence, re-inject rules, enforce budgets."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any, override
from urllib.parse import urlsplit

import yaml
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

SHA_KEY = 'governance_sha'
TOKENS_KEY = 'governance_tokens'
# One state key per decision: parallel tool calls would overwrite each other's shared list.
DECISION_PREFIX = 'governance_log:'


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


class GovernedTool(FunctionTool):
  """A tool whose confirmation comes from its tier, so the policy can tell it was built so."""


def governed_tool(
  repo: Path, func: Callable[..., Any], condition: Callable[..., bool] | None = None
) -> FunctionTool:
  """Wraps a function so a `confirm` tier needs human confirmation, or `condition` decides."""
  tier = _load(repo, 'tools.yaml')['tools'][func.__name__]['tier']
  return GovernedTool(
    func, require_confirmation=(condition or True) if tier == 'confirm' else False
  )


class GovernancePlugin(BasePlugin):
  """Attached to the App, so it covers every agent in the tree."""

  def __init__(self, repo: Path) -> None:
    super().__init__(name='governance')
    self.repo = repo
    self.sha = governance_hash(repo)
    self.budget: int = _load(repo, 'thresholds.yaml')['session_token_budget']
    self.output_root = repo / _load(repo, 'profile.yaml')['product_agent']['output_root']
    self.tools: dict[str, dict[str, Any]] = _load(repo, 'tools.yaml')['tools']
    self.services = {
      service
      for services in _load(repo, 'allowlists/services.yaml').values()
      for service in services
    }
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

  def _path_allowed(self, value: object, work_item: object) -> bool:
    if not (isinstance(value, str) and isinstance(work_item, str)):
      return False
    if '\0' in value + work_item:
      return False
    root = self.output_root.resolve()
    folder = (root / work_item).resolve()
    return folder.parent == root and (self.repo / value).resolve().is_relative_to(folder)

  def _target_allowed(self, value: object) -> bool:
    if not isinstance(value, str):
      return False
    try:
      host = urlsplit(value).hostname
    except ValueError:
      return False
    return value in self.services or host in self.services

  def _denial(
    self, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext
  ) -> tuple[str, str] | None:
    entry = self.tools.get(tool.name)
    if entry is None:
      return 'TOOL-001', f'{tool.name} has no tier in governance/tools.yaml'
    if entry['tier'] == 'deny':
      return 'TOOL-001', f'{tool.name} is a deny-tier tool'
    if entry['tier'] == 'confirm' and not isinstance(tool, GovernedTool):
      return 'TOOL-001', f'{tool.name} is confirm-tier but was not built with governed_tool'
    work_item = tool_context.state.get('work_item')
    for arg in entry['paths']:
      if not self._path_allowed(tool_args.get(arg), work_item):
        return 'FS-001', f'{arg} is not inside {self.output_root.name}/<work item>/'
    for arg in entry['targets']:
      if not self._target_allowed(tool_args.get(arg)):
        return 'TOOL-001', f'{arg} is not in governance/allowlists/services.yaml'
    return None

  @override
  async def before_tool_callback(
    self, *, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext
  ) -> dict[str, Any] | None:
    tier = self.tools.get(tool.name, {}).get('tier', 'unlisted')

    def log(result: str, rule: str) -> None:
      key = f'{DECISION_PREFIX}{tool_context.function_call_id}:{result}'
      tool_context.state[key] = {'tool': tool.name, 'tier': tier, 'result': result, 'rule': rule}

    denial = self._denial(tool, tool_args, tool_context)
    if denial:
      log('denied', denial[0])
      return {'status': 'error', 'error': f'{denial[0]}: {denial[1]}'}
    confirmation = tool_context.tool_confirmation
    if confirmation:
      log('confirmed' if confirmation.confirmed else 'rejected', 'TOOL-001')
    elif not (
      isinstance(tool, GovernedTool)
      and await tool.check_require_confirmation(tool_args, tool_context)
    ):
      log('allowed', 'TOOL-001')
    return None
