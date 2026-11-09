"""TOOL-001 and FS-001: the before-tool policy, called through the fake model."""

import pytest
from conftest import call, run_governed, say
from google.adk.flows.llm_flows.functions import REQUEST_CONFIRMATION_FUNCTION_CALL_NAME
from google.genai import types

from app.governance import DECISION_PREFIX, governed_tool

TOOLS = {
  'free_tool': {'tier': 'free', 'rules': [], 'paths': [], 'targets': []},
  'write_file': {'tier': 'free', 'rules': ['FS-001'], 'paths': ['path'], 'targets': []},
  'send': {'tier': 'free', 'rules': ['TOOL-001'], 'paths': [], 'targets': ['url']},
  'denied_tool': {'tier': 'deny', 'rules': [], 'paths': [], 'targets': []},
  'confirm_tool': {'tier': 'confirm', 'rules': [], 'paths': [], 'targets': []},
}
ran: list[str] = []


def free_tool() -> dict[str, str]:
  """A free tool.

  Returns:
    A status.
  """
  ran.append('free_tool')
  return {'status': 'success'}


def unlisted_tool() -> dict[str, str]:
  """A tool nobody classified.

  Returns:
    A status.
  """
  ran.append('unlisted_tool')
  return {'status': 'success'}


def denied_tool() -> dict[str, str]:
  """A deny-tier tool.

  Returns:
    A status.
  """
  ran.append('denied_tool')
  return {'status': 'success'}


def write_file(path: str = '') -> dict[str, str]:
  """A tool that takes a path.

  Args:
    path: Where to write.

  Returns:
    A status.
  """
  ran.append(path)
  return {'status': 'success'}


def send(url: str = '') -> dict[str, str]:
  """A tool that takes a target.

  Args:
    url: Where to send.

  Returns:
    A status.
  """
  ran.append(url)
  return {'status': 'success'}


def confirm_tool(amount: int = 0) -> dict[str, str]:
  """A tool that needs confirmation.

  Args:
    amount: How much.

  Returns:
    A status.
  """
  ran.append('confirm_tool')
  return {'status': 'success', 'amount': str(amount)}


@pytest.fixture
def repo(governed_repo):
  ran.clear()
  governed_repo.edit_yaml('tools.yaml', tools=TOOLS)
  return governed_repo


async def _call_once(repo, tool, state=None, **args):
  name = tool.name if hasattr(tool, 'name') else tool.__name__
  events, stored, _, runner = await run_governed(
    repo, [call(name, **args), say('done')], [tool], state=state
  )
  responses = [r.response for e in events for r in e.get_function_responses()]
  return responses[0], stored, events, runner


def _decisions(stored):
  return [v for k, v in stored.state.items() if k.startswith(DECISION_PREFIX)]


def _is_denied(response, rule):
  return response['status'] == 'error' and rule in response['error']


@pytest.mark.asyncio
async def test_unlisted_tool_on_the_agent_is_denied(repo):
  response, stored, _, _ = await _call_once(repo, unlisted_tool)
  assert _is_denied(response, 'TOOL-001')
  assert ran == []
  assert _decisions(stored)[0]['tier'] == 'unlisted'


@pytest.mark.asyncio
async def test_a_name_the_model_invented_is_denied(repo):
  events, _, _, _ = await run_governed(repo, [call('invented'), say('done')], [free_tool])
  [response] = [r.response for e in events for r in e.get_function_responses()]
  assert _is_denied(response, 'TOOL-001')


@pytest.mark.asyncio
async def test_deny_tier_tool_is_denied(repo):
  response, _, _, _ = await _call_once(repo, denied_tool)
  assert _is_denied(response, 'TOOL-001')
  assert ran == []


@pytest.mark.asyncio
async def test_free_tool_runs_and_is_logged(repo):
  response, stored, _, _ = await _call_once(repo, free_tool)
  assert response['status'] == 'success'
  assert ran == ['free_tool']
  assert _decisions(stored) == [
    {'tool': 'free_tool', 'tier': 'free', 'result': 'allowed', 'rule': 'TOOL-001'}
  ]


# --- FS-001 ----------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
  'path',
  [
    'output/w1/../w2/x',
    'output/w1/../../x',
    'output/w2/x',
    '/etc/passwd',
    'app/agent.py',
    'output/w1/a\0b',
  ],
)
async def test_path_escape_is_denied(repo, path):
  response, stored, _, _ = await _call_once(repo, write_file, state={'work_item': 'w1'}, path=path)
  assert _is_denied(response, 'FS-001')
  assert ran == []
  assert _decisions(stored)[0]['result'] == 'denied'
  assert _decisions(stored)[0]['rule'] == 'FS-001'


@pytest.mark.asyncio
async def test_symlink_escape_is_denied(repo, tmp_path_factory):
  outside = tmp_path_factory.mktemp('outside')
  (repo.path / 'output/w1').mkdir(parents=True)
  (repo.path / 'output/w1/link').symlink_to(outside)
  response, _, _, _ = await _call_once(
    repo, write_file, state={'work_item': 'w1'}, path='output/w1/link/x'
  )
  assert _is_denied(response, 'FS-001')


@pytest.mark.asyncio
async def test_any_path_is_denied_with_no_work_item(repo):
  response, _, _, _ = await _call_once(repo, write_file, path='output/w1/x')
  assert _is_denied(response, 'FS-001')


@pytest.mark.asyncio
@pytest.mark.parametrize('work_item', ['..', '.', '', 'a/b', '../..', '/etc', 7])
async def test_work_item_that_escapes_the_output_root_is_denied(repo, work_item):
  response, _, _, _ = await _call_once(
    repo, write_file, state={'work_item': work_item}, path='output/x'
  )
  assert _is_denied(response, 'FS-001')


@pytest.mark.asyncio
async def test_missing_path_argument_is_denied(repo):
  response, _, _, _ = await _call_once(repo, write_file, state={'work_item': 'w1'})
  assert _is_denied(response, 'FS-001')


@pytest.mark.asyncio
@pytest.mark.parametrize('prefix', ['', '{repo}/'])
async def test_path_inside_the_work_item_is_allowed(repo, prefix):
  path = prefix.format(repo=repo.path.resolve()) + 'output/w1/deep/x'
  response, _, _, _ = await _call_once(repo, write_file, state={'work_item': 'w1'}, path=path)
  assert response['status'] == 'success'
  assert ran == [path]


# --- External targets ------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
  'url',
  [
    'https://evil.example.com/x',
    'https://api.anthropic.com.evil.example.com/',
    'https://evil.example.com/api.anthropic.com',
    'http://[bad',
  ],
)
async def test_non_allowlisted_target_is_denied(repo, url):
  response, _, _, _ = await _call_once(repo, send, url=url)
  assert _is_denied(response, 'TOOL-001')
  assert ran == []


@pytest.mark.asyncio
async def test_missing_target_argument_is_denied(repo):
  response, _, _, _ = await _call_once(repo, send)
  assert _is_denied(response, 'TOOL-001')


@pytest.mark.asyncio
@pytest.mark.parametrize('url', ['https://api.anthropic.com/v1/messages', 'api.anthropic.com'])
async def test_allowlisted_target_matches_on_hostname_or_exact_string(repo, url):
  response, _, _, _ = await _call_once(repo, send, url=url)
  assert response['status'] == 'success'


# --- Confirmation ----------------------------------------------------------------------


def _confirmation_reply(events, confirmed):
  [request] = [
    c
    for e in events
    for c in e.get_function_calls()
    if c.name == REQUEST_CONFIRMATION_FUNCTION_CALL_NAME
  ]
  reply = types.FunctionResponse(
    id=request.id, name=request.name, response={'confirmed': confirmed}
  )
  return types.Content(role='user', parts=[types.Part(function_response=reply)])


async def _answer(runner, stored, events, confirmed):
  message = _confirmation_reply(events, confirmed)
  [e async for e in runner.run_async(user_id='u', session_id=stored.id, new_message=message)]
  return await runner.session_service.get_session(
    app_name=runner.app_name, user_id='u', session_id=stored.id
  )


@pytest.mark.asyncio
@pytest.mark.parametrize(('confirmed', 'result'), [(True, 'confirmed'), (False, 'rejected')])
async def test_confirm_tool_waits_for_confirmation(repo, confirmed, result):
  tool = governed_tool(repo.path, confirm_tool)
  _, stored, events, runner = await _call_once(repo, tool)
  assert ran == []
  assert _decisions(stored) == []
  stored = await _answer(runner, stored, events, confirmed)
  assert ran == (['confirm_tool'] if confirmed else [])
  assert [d['result'] for d in _decisions(stored)] == [result]


@pytest.mark.asyncio
async def test_callable_condition_is_honoured(repo):
  tool = governed_tool(repo.path, confirm_tool, condition=lambda amount: amount > 5)
  response, stored, _, _ = await _call_once(repo, tool, amount=1)
  assert response['status'] == 'success'
  assert ran == ['confirm_tool']
  assert _decisions(stored)[0]['result'] == 'allowed'

  ran.clear()
  _, stored, _, _ = await _call_once(
    repo, governed_tool(repo.path, confirm_tool, condition=lambda amount: amount > 5), amount=9
  )
  assert ran == []
  assert _decisions(stored) == []


@pytest.mark.asyncio
async def test_confirm_tool_not_built_with_governed_tool_is_denied(repo):
  response, _, _, _ = await _call_once(repo, confirm_tool)
  assert _is_denied(response, 'TOOL-001')
  assert 'governed_tool' in response['error']
  assert ran == []


@pytest.mark.asyncio
async def test_free_tool_built_with_governed_tool_needs_no_confirmation(repo):
  response, _, _, _ = await _call_once(repo, governed_tool(repo.path, free_tool))
  assert response['status'] == 'success'
  assert ran == ['free_tool']
