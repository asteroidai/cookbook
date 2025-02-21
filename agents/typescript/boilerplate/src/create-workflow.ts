import {AsteroidAgents} from "asteroid-odyssey";
import {CreateWorkflowRequest} from "asteroid-odyssey/dist/generated/agents";

const apiKey: string = process.env.ASTEROID_API_KEY ?? "";
const asteroid = new AsteroidAgents(apiKey);

/**
 * Ceres is our browser running agent that can execute tasks for you. This is the only one at the moment,
 * but there's more coming ASAP.
 */
const agentName: string = "ceres";

const request: CreateWorkflowRequest = {
  name: "Your workflow name",
  fields: {
    "workflow_name": "Your workflow name",
    "start_url": "https://www.google.com",
  },
  prompts: ["Prompt for the agent"],
  provider: CreateWorkflowRequest.provider.ANTHROPIC
}

async function createWorkflow() {
  try {
    const workflowId = await asteroid.createWorkflow(agentName, request);
    console.log('Workflow created with ID:', workflowId);
  } catch (error) {
    console.error('Error executing the workflow:', error);
  }
}

createWorkflow();
