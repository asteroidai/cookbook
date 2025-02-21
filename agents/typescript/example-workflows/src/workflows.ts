import {CreateWorkflowRequest} from "asteroid-odyssey/dist/generated/agents";


export const workflows: CreateWorkflowRequest[] = [
  {
    name: "W3 Challenge",
    fields: {
      "workflow_name": "Coding Challenge",
      "start_url": "https://www.google.com",
    },
    prompts: ["I want you to complete a coding challenge for me. This can be done on any website; and I want you to do it in order to explain to me what was done, to help me learn to code"],
    provider: CreateWorkflowRequest.provider.ANTHROPIC
  },
  {
    name: "Reddit AI Summariser",
    fields: {
      "workflow_name": "Reddit AI Summariser",
      "start_url": "https://www.google.com",
    },
    prompts: ["I want you to go to reddit and find me a well known AI based subreddit. I then want you to find the top recent posts, and summarise the top 3 posts for me."],
    provider: CreateWorkflowRequest.provider.ANTHROPIC
  },
  {
    name: "World News Summariser",
    fields: {
      "workflow_name": "World New Summariser",
      "start_url": "https://www.google.com",
    },
    prompts: [
      `I want to get an overall view of recent world events. In order to do this, can you go to a news website and choose a headline.
      Then, can you look at other news websites and summarise the same headline from different perspectives.`
    ],
    provider: CreateWorkflowRequest.provider.ANTHROPIC
  },

]
