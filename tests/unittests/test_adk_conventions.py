"""The conventions in app/AGENTS.md that can be checked without a model."""

import inspect
from pathlib import Path

from google.adk.cli.utils.agent_loader import AgentLoader
from google.adk.tools.tool_context import ToolContext

from app import agent

PROJECT = Path(__file__).parent.parent.parent


def _all_agents(root=agent.root_agent):
  yield root
  for sub_agent in root.sub_agents:
    yield from _all_agents(sub_agent)


def test_agent_folders_are_laid_out_for_adk_web():
  # ADK lists every top-level folder with an agent.py, a root_agent.yaml or
  # an __init__.py, so tests/ must not be a package.
  names = AgentLoader(str(PROJECT)).list_agents()
  assert names == ['app']
  for name in names:
    assert name.isidentifier(), name
    assert 'from . import agent' in (PROJECT / name / '__init__.py').read_text()


def test_only_the_root_sets_a_model():
  # Non-LLM agents have no model field.
  models = [a.name for a in _all_agents() if getattr(a, 'model', None)]
  assert models == [agent.root_agent.name]


def test_every_agent_has_a_description():
  assert all(a.description for a in _all_agents())


def test_tool_schemas_are_complete():
  tools = {t for a in _all_agents() for t in a.tools if inspect.isfunction(t)}
  for tool in tools:
    # eval_str resolves string annotations from `from __future__ import annotations`.
    sig = inspect.signature(tool, eval_str=True)
    params = [p for p in sig.parameters.values() if p.annotation is not ToolContext]
    doc = tool.__doc__ or ''
    assert sig.return_annotation is not inspect.Signature.empty, tool.__name__
    assert all(p.annotation is not inspect.Parameter.empty for p in params), tool.__name__
    assert 'Returns:' in doc, tool.__name__
    assert all(f'{p.name}:' in doc for p in params), tool.__name__
