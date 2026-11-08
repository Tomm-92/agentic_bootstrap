import pytest
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from app import agent


def call(name: str, **args) -> LlmResponse:
  """A model turn that calls one tool."""
  part = types.Part(function_call=types.FunctionCall(name=name, args=args))
  return LlmResponse(content=types.Content(role='model', parts=[part]))


def say(text: str) -> LlmResponse:
  """A model turn that replies with text."""
  return LlmResponse(content=types.Content(role='model', parts=[types.Part(text=text)]))


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
