import { AsteroidAgents } from 'asteroid-odyssey';
import {ApiError} from "asteroid-odyssey/dist/generated/agents";

const apiKey: string = process.env.ASTEROID_API_KEY ?? "";
const asteroid = new AsteroidAgents(apiKey);

const workflowID = 'YOUR-WORKFLOW-ID-HERE';

async function runWorkflowExample() {
  const runID: string = await triggerRun(workflowID);
  await checkRunStatus(runID);
  await getRunResult(runID);
}

async function triggerRun(workflowID: string): Promise<string> {
  try{
    const runID = await asteroid.runWorkflow(workflowID, { name: 'Alice' });
    console.log('Workflow run initiated with ID:', runID);
    return runID;
  } catch (error) {
    console.error('Error executing the workflow:', error);
    throw error;
  }
}

async function checkRunStatus(runID: string) {
  // Poll for the workflow status until it completes
  while (true) {
    let status;
    try {
      status = await asteroid.getRunStatus(runID);
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 404) {
        console.error('Error getting the run status:', error);
        break;
      }
      console.error("Run not found- it may not have been created yet")
    }
    console.log('Current workflow status:', status);
    if (status === 'completed') break;
    // Wait for 1 second before checking again
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

async function getRunResult(runID: string) {
  try {
    const result = await asteroid.getRunResult(runID);
    console.log('Workflow run result:', result);
  } catch (error) {
    console.error('Error getting the run result:', error);
  }
}

runWorkflowExample();

