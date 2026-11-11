"""OBS-001: every model and tool call emits the attributes in ARCHITECTURE.md."""

import pytest
from conftest import call, run_governed, say
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from app.governance import governance_hash

IDENTITY = {'session.id', 'user.id', 'governance.sha', 'guardrail.result'}
MODEL_ATTRIBUTES = IDENTITY | {'model.id', 'tokens.input', 'tokens.output', 'latency.ms'}
TOOL_ATTRIBUTES = IDENTITY | {'tool.name', 'tool.tier'}


def fine() -> dict[str, str]:
  """A tool that works.

  Returns:
    A status.
  """
  return {'status': 'success'}


def broken() -> dict[str, str]:
  """A tool that raises.

  Returns:
    Nothing: it raises.
  """
  raise ValueError('broken')


@pytest.fixture
def repo(governed_repo, telemetry):
  telemetry[0].clear()
  entry = {'tier': 'free', 'rules': [], 'paths': [], 'targets': []}
  governed_repo.edit_yaml('tools.yaml', tools={'fine': entry, 'broken': entry})
  return governed_repo


def _spans(telemetry, name):
  return [s for s in telemetry[0].get_finished_spans() if s.name == name]


def _metric(telemetry, name):
  data = telemetry[1].get_metrics_data()
  return [
    point
    for resource in data.resource_metrics
    for scope in resource.scope_metrics
    for metric in scope.metrics
    if metric.name == name
    for point in metric.data.data_points
  ]


@pytest.mark.asyncio
async def test_session_emits_every_invariant_attribute(repo, telemetry):
  _, stored, _, _ = await run_governed(repo, [call('fine'), say('done')], [fine])
  model_spans = _spans(telemetry, 'governance.model_call')
  [tool_span] = _spans(telemetry, 'execute_tool fine')
  assert len(model_spans) == 2
  for span in model_spans:
    assert set(span.attributes) >= MODEL_ATTRIBUTES
    assert span.attributes['model.id'] == 'fake'
    assert span.attributes['tokens.input'] == 10
    assert span.attributes['tokens.output'] == 5
    assert span.attributes['latency.ms'] >= 0
    assert 'failure.source' not in span.attributes
  assert set(tool_span.attributes) >= TOOL_ATTRIBUTES
  assert tool_span.attributes['tool.tier'] == 'free'
  assert tool_span.attributes['guardrail.result'] == 'allowed'
  for span in [*model_spans, tool_span]:
    assert span.attributes['session.id'] == stored.id
    assert span.attributes['user.id'] == 'u'
    assert span.attributes['governance.sha'] == governance_hash(repo.path)


@pytest.mark.asyncio
async def test_spans_share_one_trace(repo, telemetry):
  await run_governed(repo, [call('fine'), say('done')], [fine])
  traces = {s.context.trace_id for s in telemetry[0].get_finished_spans()}
  assert len(traces) == 1


@pytest.mark.asyncio
async def test_model_error_is_attributed_to_the_model(repo, telemetry):
  with pytest.raises(AssertionError, match='more times than scripted'):
    await run_governed(repo, [])
  [span] = _spans(telemetry, 'governance.model_call')
  assert span.attributes['failure.source'] == 'model'


@pytest.mark.asyncio
async def test_missing_token_count_is_attributed_to_the_harness(repo, telemetry):
  no_usage = LlmResponse(content=types.Content(role='model', parts=[types.Part(text='x')]))
  with pytest.raises(RuntimeError, match='no token count'):
    await run_governed(repo, [no_usage])
  [span] = _spans(telemetry, 'governance.model_call')
  assert span.attributes['failure.source'] == 'harness'


@pytest.mark.asyncio
async def test_tool_error_is_attributed_to_the_tool(repo, telemetry):
  with pytest.raises(ValueError, match='broken'):
    await run_governed(repo, [call('broken'), say('done')], [broken])
  [span] = _spans(telemetry, 'execute_tool broken')
  assert span.attributes['failure.source'] == 'tool'


@pytest.mark.asyncio
async def test_denied_tool_is_attributed_to_policy_and_counted(repo, telemetry):
  def before():
    return sum(p.value for p in _metric(telemetry, 'governance.tool_calls.blocked'))

  start = before()
  await run_governed(repo, [call('unlisted'), say('done')], [fine])
  [span] = _spans(telemetry, 'execute_tool unlisted')
  assert span.attributes['failure.source'] == 'policy'
  assert span.attributes['guardrail.result'] == 'denied'
  assert set(span.attributes) >= TOOL_ATTRIBUTES
  assert before() == start + 1


@pytest.mark.asyncio
async def test_budget_refusal_is_attributed_to_policy_and_counted(repo, telemetry):
  def refusals():
    return sum(p.value for p in _metric(telemetry, 'governance.budget_refusals'))

  start = refusals()
  repo.edit_yaml('thresholds.yaml', session_token_budget=1)
  await run_governed(repo, [say('first')], state={'governance_tokens': 1})
  [span] = _spans(telemetry, 'governance.model_call')
  assert span.attributes['failure.source'] == 'policy'
  assert span.attributes['guardrail.result'] == 'refused'
  assert set(span.attributes) >= MODEL_ATTRIBUTES
  assert refusals() == start + 1


@pytest.mark.asyncio
async def test_session_token_gauge_is_set(repo, telemetry):
  _, stored, _, _ = await run_governed(repo, [say('done')])
  points = [
    p
    for p in _metric(telemetry, 'governance.session_tokens')
    if p.attributes['session.id'] == stored.id
  ]
  assert points[0].value == 15
