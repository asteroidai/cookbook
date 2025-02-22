import os
from asteroid_odyssey import Odyssey
from asteroid_odyssey.api.generated.agents.asteroid_agents_api_client.models import CreateWorkflowRequest
from workflows import workflows

api_key = os.getenv('ASTEROID_API_KEY', '')
asteroid = Odyssey(api_key)

agent_name = "ceres"

def create_workflow(request: CreateWorkflowRequest):
    try:
        workflow_id = asteroid.create_workflow(agent_name, request)
        print('Workflow created with ID:', workflow_id)
    except Exception as error:
        print('Error executing the workflow:', error)

def choose_workflow():
    for index, workflow in enumerate(workflows):
        print(f"{index + 1}. {workflow.name}")

    choice_number = input('Choose one of the above workflows: ')
    choice = int(choice_number)
    return workflows[choice - 1]

if __name__ == '__main__':
    workflow = choose_workflow()
    create_workflow(workflow)
