"""GOV-005, COST-001, MODEL-001 and EVID-001: the runtime governance layer, with no real model."""

import pytest
import yaml
from anthropic.types import Message, TextBlock, Usage
from conftest import USAGE, FakeLlm, GovernedRepo, call, run_governed, say
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.models.anthropic_llm import AnthropicLlm, message_to_generate_content_response
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types

from app import agent
from app.governance import SHA_KEY, TOKENS_KEY, GovernanceError, GovernancePlugin, governance_hash


def _text(event):
  return ''.join(p.text or '' for p in event.content.parts)


def test_startup_fails_when_governance_is_missing(tmp_path):
  with pytest.raises(GovernanceError):
    GovernancePlugin(tmp_path)


def test_startup_fails_when_governance_is_uncommitted(tmp_path):
  repo = GovernedRepo(tmp_path)
  repo.git('rm', '-rq', '--cached', 'governance')
  repo.git('commit', '-q', '-m', 'untrack')
  with pytest.raises(GovernanceError):
    GovernancePlugin(tmp_path)


def test_startup_fails_when_governance_is_dirty(governed_repo):
  (governed_repo.path / 'governance/rules.yaml').write_text('rules: []\n')
  with pytest.raises(GovernanceError, match='uncommitted'):
    GovernancePlugin(governed_repo.path)


def test_startup_reads_the_committed_hash(governed_repo):
  assert GovernancePlugin(governed_repo.path).sha == governance_hash(governed_repo.path)


async def _run_changing_governance_first(repo, change):
  plugin = GovernancePlugin(repo.path)
  fake = FakeLlm()
  root = Agent(name='root', model=fake, description='Test agent.')
  app = App(name='halt_test', root_agent=root, plugins=[plugin])
  runner = InMemoryRunner(app=app)
  session = await runner.session_service.create_session(app_name=runner.app_name, user_id='u')
  change()
  content = types.Content(role='user', parts=[types.Part(text='Go')])
  events = [
    e async for e in runner.run_async(user_id='u', session_id=session.id, new_message=content)
  ]
  return events, fake


@pytest.mark.asyncio
async def test_run_halts_on_a_hash_change(governed_repo):
  def change():
    governed_repo.edit_yaml('thresholds.yaml', session_token_budget=1)

  events, fake = await _run_changing_governance_first(governed_repo, change)
  assert 'GOV-005' in _text(events[-1])
  assert 'changed' in _text(events[-1])
  assert fake.requests == []


@pytest.mark.asyncio
async def test_run_halts_when_governance_turns_dirty(governed_repo):
  def change():
    (governed_repo.path / 'governance/rules.yaml').write_text('rules: []\n')

  events, fake = await _run_changing_governance_first(governed_repo, change)
  assert 'GOV-005' in _text(events[-1])
  assert fake.requests == []


@pytest.mark.asyncio
async def test_every_event_carries_the_hash(governed_repo):
  def tool() -> dict[str, str]:
    """A test tool.

    Returns:
      A status.
    """
    return {'status': 'success'}

  governed_repo.edit_yaml(
    'tools.yaml', tools={'tool': {'tier': 'free', 'rules': [], 'paths': [], 'targets': []}}
  )
  sha = governance_hash(governed_repo.path)
  events, stored, _, _ = await run_governed(governed_repo, [call('tool'), say('done')], [tool])
  assert len(events) >= 3
  assert all(e.custom_metadata[SHA_KEY] == sha for e in events)
  agent_events = [e for e in stored.events if e.author != 'user']
  assert len(agent_events) == len(events)
  assert all(e.custom_metadata[SHA_KEY] == sha for e in agent_events)
  assert stored.state[SHA_KEY] == sha


@pytest.mark.asyncio
async def test_runtime_rules_appear_in_the_model_request(governed_repo):
  _, _, llm, _ = await run_governed(governed_repo, [say('done')])
  instruction = llm.requests[0].config.system_instruction
  assert 'FS-001' in instruction
  assert 'Because:' in instruction
  assert governance_hash(governed_repo.path) in instruction
  assert 'GOV-001' not in instruction  # A build-only rule.


@pytest.mark.asyncio
async def test_session_is_refused_once_over_budget(governed_repo):
  governed_repo.edit_yaml('thresholds.yaml', session_token_budget=15)
  events, stored, llm, _ = await run_governed(governed_repo, [say('first')], state={TOKENS_KEY: 15})
  assert 'COST-001' in _text(events[-1])
  assert llm.requests == []
  assert llm.script  # The model was never reached.
  assert stored.state[TOKENS_KEY] == 15


@pytest.mark.asyncio
async def test_tokens_are_counted_across_calls_and_persist(governed_repo):
  _, stored, _, _ = await run_governed(governed_repo, [call('nope'), say('done')], message='Go')
  assert stored.state[TOKENS_KEY] == 2 * USAGE.total_token_count


@pytest.mark.asyncio
async def test_budget_stops_a_session_partway(governed_repo):
  governed_repo.edit_yaml('thresholds.yaml', session_token_budget=USAGE.total_token_count)
  events, _, llm, _ = await run_governed(governed_repo, [call('nope'), say('unreached')])
  assert 'COST-001' in _text(events[-1])
  assert len(llm.requests) == 1


@pytest.mark.asyncio
async def test_missing_token_count_is_an_error(governed_repo):
  no_usage = LlmResponse(content=types.Content(role='model', parts=[types.Part(text='x')]))
  with pytest.raises(RuntimeError, match='no token count'):
    await run_governed(governed_repo, [no_usage])


def test_adk_converts_an_anthropic_message_to_a_token_count():
  message = Message(
    id='m',
    type='message',
    role='assistant',
    model='claude-haiku-5-5',
    content=[TextBlock(type='text', text='hi')],
    usage=Usage(input_tokens=7, output_tokens=3),
    stop_reason='end_turn',
  )
  usage = message_to_generate_content_response(message).usage_metadata
  assert usage
  assert usage.total_token_count == 10


def _allowed_models():
  models = yaml.safe_load((agent.REPO / 'governance/allowlists/models.yaml').read_text())['models']
  return {m['id'] for m in models}


def test_every_configured_model_is_allowlisted():
  assert agent.MODEL_ID in _allowed_models()
  model = agent.root_agent.model
  assert isinstance(model, AnthropicLlm)
  assert model.model == agent.MODEL_ID


def test_agent_loads_the_way_the_runner_loads_it():
  loaded = AgentLoader(str(agent.REPO)).load_agent('app')
  assert isinstance(loaded, App)
  assert any(isinstance(p, GovernancePlugin) for p in loaded.plugins)
  assert loaded.root_agent is agent.root_agent


def test_compaction_is_off():
  assert agent.app.events_compaction_config is None
