"""Runs one session through the governed app, against the durable session log (EVID-001)."""

import argparse
import asyncio
import sys
from collections.abc import AsyncGenerator
from typing import override

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.genai import types

from app import agent

SESSIONS = agent.REPO / '.sessions'
USAGE = types.GenerateContentResponseUsageMetadata(
  prompt_token_count=10, candidates_token_count=5, total_token_count=15
)


class ScriptedLlm(BaseLlm):
  """Calls the agent's tool once and then replies, spending nothing."""

  model: str = 'scripted-fake'

  @override
  async def generate_content_async(
    self, llm_request: LlmRequest, stream: bool = False
  ) -> AsyncGenerator[LlmResponse]:
    last = llm_request.contents[-1].parts or []
    if any(part.function_response for part in last):
      part = types.Part(text='Demo is a placeholder project.')
    else:
      call = types.FunctionCall(name='get_project_status', args={'project': 'demo'})
      part = types.Part(function_call=call)
    yield LlmResponse(content=types.Content(role='model', parts=[part]), usage_metadata=USAGE)


async def run(prompt: str) -> None:
  SESSIONS.mkdir(exist_ok=True)
  service = DatabaseSessionService(f'sqlite+aiosqlite:///{SESSIONS / "sessions.db"}')
  runner = Runner(app=agent.app, session_service=service)
  session = await service.create_session(app_name=runner.app_name, user_id='local')
  message = types.Content(role='user', parts=[types.Part(text=prompt)])
  sys.stdout.write(f'session {session.id}\n')
  async for event in runner.run_async(user_id='local', session_id=session.id, new_message=message):
    for part in (event.content.parts or []) if event.content else []:
      if part.text:
        sys.stdout.write(f'{part.text}\n')
  await runner.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--fake', action='store_true', help='use a scripted model; spends nothing')
  parser.add_argument('prompt')
  args = parser.parse_args()
  if args.fake:
    agent.root_agent.model = ScriptedLlm()
  asyncio.run(run(args.prompt))
