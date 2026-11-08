"""Real-model tests. These spend credits: run with `.venv/bin/pytest -m integration`."""

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

from app import agent


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_replies():
  runner = InMemoryRunner(agent=agent.root_agent)
  session = await runner.session_service.create_session(app_name=runner.app_name, user_id='u')
  msg = types.Content(role='user', parts=[types.Part(text='What is the status of demo?')])
  events = [e async for e in runner.run_async(user_id='u', session_id=session.id, new_message=msg)]
  reply = events[-1].content
  assert reply and reply.parts
  assert reply.parts[0].text
