import pytest
from conftest import call, say
from google.adk.runners import InMemoryRunner
from google.genai import types

from app import agent


@pytest.mark.asyncio
async def test_project_status(fake_llm):
  fake_llm.script = [call('get_project_status', project='demo'), say('Demo is a placeholder.')]
  runner = InMemoryRunner(agent=agent.root_agent)
  session = await runner.session_service.create_session(app_name=runner.app_name, user_id='u')
  msg = types.Content(role='user', parts=[types.Part(text='Status of demo?')])
  events = [e async for e in runner.run_async(user_id='u', session_id=session.id, new_message=msg)]
  reply = events[-1].content
  assert reply and reply.parts
  assert reply.parts[0].text == 'Demo is a placeholder.'
  [tool_response] = events[1].get_function_responses()
  assert tool_response.response == agent.get_project_status('demo')
