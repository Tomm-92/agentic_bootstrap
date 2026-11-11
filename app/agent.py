from pathlib import Path

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.models.anthropic_llm import AnthropicLlm

from .governance import GovernancePlugin

REPO = Path(__file__).parent.parent
MODEL_ID = 'claude-haiku-5-5'


def get_project_status(project: str) -> dict[str, str]:
  """Reports the status of a project.

  Args:
    project: The name of the project to report on.

  Returns:
    A dict with a `status` key and a `report` key describing the project.
  """
  return {'status': 'success', 'report': f'{project} is a placeholder project.'}


root_agent = Agent(
  name='root_agent',
  model=AnthropicLlm(model=MODEL_ID),
  description='Placeholder agent that reports project status; replace with the real agent.',
  instruction='Use get_project_status to answer questions about a project.',
  tools=[get_project_status],
)

# ADK's loader reads `app` first. Building the plugin here makes the agent fail closed at import.
app = App(name='app', root_agent=root_agent, plugins=[GovernancePlugin(REPO)])
