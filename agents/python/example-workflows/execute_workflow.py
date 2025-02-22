import os
import time

from asteroid_odyssey.api.generated.agents.asteroid_agents_api_client.models import WorkflowExecutionRequest
from asteroid_odyssey import Odyssey
from asteroid_odyssey.exceptions import ApiError

api_key = os.getenv('ASTEROID_API_KEY', '')
asteroid = Odyssey(api_key)

workflow_id = 'YOUR-WORKFLOW-ID-HERE'

def run_workflow_example():
    run_id = trigger_run(workflow_id)
    check_run_status(run_id)
    get_run_result(run_id)

def trigger_run(workflow_id):
    try:
        run_id = asteroid.run_workflow(workflow_id, WorkflowExecutionRequest())
        print('Workflow run initiated with ID:', run_id)
        return run_id
    except Exception as error:
        print('Error executing the workflow:', error)
        raise

def check_run_status(run_id):
    while True:
        try:
            status = asteroid.get_run_status(run_id)
        except ApiError as error:
            if error.status_code != 404:
                print('Error getting the run status:', error)
                break
            print("Run not found- it may not have been created yet")
        print('Current workflow status:', status)
        if status == 'completed':
            break
        time.sleep(1)

def get_run_result(run_id):
    try:
        result = asteroid.get_run_result(run_id)
        print('Workflow run result:', result)
    except Exception as error:
        print('Error getting the run result:', error)

if __name__ == '__main__':
    run_workflow_example()
