import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types

from app import agent
from app.governance import GovernancePlugin

USAGE = types.GenerateContentResponseUsageMetadata(
  prompt_token_count=10, candidates_token_count=5, total_token_count=15
)


def call(name: str, **args) -> LlmResponse:
  """A model turn that calls one tool."""
  part = types.Part(function_call=types.FunctionCall(name=name, args=args))
  return LlmResponse(content=types.Content(role='model', parts=[part]), usage_metadata=USAGE)


def say(text: str) -> LlmResponse:
  """A model turn that replies with text."""
  content = types.Content(role='model', parts=[types.Part(text=text)])
  return LlmResponse(content=content, usage_metadata=USAGE)


class FakeLlm(BaseLlm):
  """Returns scripted responses in order and records every request."""

  model: str = 'fake'
  script: list[LlmResponse] = []
  requests: list[LlmRequest] = []

  async def generate_content_async(self, llm_request, stream=False):
    del stream  # Required by BaseLlm's signature.
    self.requests.append(llm_request)
    if not self.script:
      raise AssertionError('The agent called the model more times than scripted.')
    yield self.script.pop(0)


@pytest.fixture
def fake_llm(monkeypatch):
  """Replaces the root agent's model, and checks the test used its whole script."""
  llm = FakeLlm()
  monkeypatch.setattr(agent.root_agent, 'model', llm)
  yield llm
  assert not llm.script, f'The agent stopped before using: {llm.script}'


class GovernedRepo:
  """A temporary repo holding a copy of the real governance, so tests can change it."""

  def __init__(self, path: Path):
    self.path = path
    shutil.copytree(Path(__file__).parents[2] / 'governance', path / 'governance')
    self.git('init', '-q', '-b', 'main')
    self.commit()

  def git(self, *args):
    subprocess.run(  # noqa: S603 - fixed git commands, in a temporary repo
      ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com', *args],  # noqa: S607 - from PATH
      cwd=self.path,
      check=True,
      capture_output=True,
    )

  def commit(self):
    self.git('add', '-A')
    self.git('commit', '-q', '-m', 'governance')

  def edit_yaml(self, name, **changes):
    path = self.path / 'governance' / name
    path.write_text(yaml.safe_dump({**yaml.safe_load(path.read_text()), **changes}))
    self.commit()


@pytest.fixture
def governed_repo(tmp_path):
  return GovernedRepo(tmp_path)


async def run_governed(repo, script, tools=(), state=None, message='Go'):
  """Runs one session of a test agent under the plugin, and returns its pieces."""
  llm = FakeLlm(script=list(script))
  root = Agent(name='root', model=llm, description='Test agent.', tools=list(tools))
  app = App(name='governed_test', root_agent=root, plugins=[GovernancePlugin(repo.path)])
  runner = InMemoryRunner(app=app)
  session = await runner.session_service.create_session(
    app_name=runner.app_name, user_id='u', state=state
  )
  content = types.Content(role='user', parts=[types.Part(text=message)])
  events = [
    e async for e in runner.run_async(user_id='u', session_id=session.id, new_message=content)
  ]
  stored = await runner.session_service.get_session(
    app_name=runner.app_name, user_id='u', session_id=session.id
  )
  return events, stored, llm, runner
