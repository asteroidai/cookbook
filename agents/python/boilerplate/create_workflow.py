import os

from asteroid_odyssey.api.generated.agents.asteroid_agents_api_client.models import CreateWorkflowRequest, CreateWorkflowRequestFields, \
    CreateWorkflowRequestProvider
from asteroid_odyssey import Odyssey


api_key = os.getenv('ASTEROID_API_KEY', '')
asteroid = Odyssey(api_key)

agent_name = "ceres"

request = CreateWorkflowRequest(
    name="Reddit Summariser- PY",
    fields=CreateWorkflowRequestFields.from_dict({
        "workflow_name": "Reddit Summariser- PY",
        "start_url": "https://www.google.com",
    }),
    prompts=["Go to reddit, find a post and summarize it"],
    provider=CreateWorkflowRequestProvider.ANTHROPIC
)

def create_workflow():
    try:
        workflow_id = asteroid.create_workflow(agent_name, request)
        print('Workflow created with ID:', workflow_id)
    except Exception as error:
        print('Error executing the workflow:', error)

if __name__ == '__main__':
    create_workflow()
