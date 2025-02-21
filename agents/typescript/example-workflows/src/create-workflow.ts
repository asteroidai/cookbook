import {workflows} from "./workflows";
import * as readline from 'readline';
import {AsteroidAgents} from "asteroid-odyssey";
import {CreateWorkflowRequest} from "asteroid-odyssey/dist/generated/agents";

const apiKey: string = process.env.ASTEROID_API_KEY ?? "";
const asteroid = new AsteroidAgents(apiKey);

/**
 * Ceres is our browser running agent that can execute tasks for you. This is the only one at the moment,
 * but there's more coming ASAP.
 */
const agentName: string = "ceres";

async function createWorkflow(request: CreateWorkflowRequest) {
  try {
    const workflowId = await asteroid.createWorkflow(agentName, request);
    console.log('Workflow created with ID:', workflowId);
  } catch (error) {
    console.error('Error executing the workflow:', error);
  }
}

function chooseWorkflow(): Promise<typeof workflows[0]> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  workflows.forEach((workflow, index) => {
    console.log(`${index + 1}. ${workflow.name}`);
  });

  return new Promise((resolve) => {
    rl.question('Choose one of the above workflows: ', (choiceNumber) => {
      const choice = parseInt(choiceNumber);
      rl.close(); // Close the readline interface
      resolve(workflows[choice - 1]);
    });
  });
}

chooseWorkflow().then((workflow) => {
  createWorkflow(workflow);
});
