from google.adk.agents import Agent


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
  model='gemini-3.5-flash',
  description='Placeholder agent that reports project status; replace with the real agent.',
  instruction='Use get_project_status to answer questions about a project.',
  tools=[get_project_status],
)
