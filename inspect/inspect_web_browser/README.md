# Inspect AI Web Browser Example

## Overview

This example demonstrates how to use the `inspect_ai` library to create an AI agent that can interact with web pages using a web browser tool. The agent performs tasks involving web navigation and form submissions autonomously.

The assistant receives instructions to interact with a website, navigates to the specified URL, fills out forms, and submits information as directed.

### Key Features Demonstrated:

- **Web Interaction**: Shows how the agent can use the `web_browser` tool to navigate websites and interact with web elements.
- **Autonomous Execution**: The AI agent plans and performs web actions without human guidance.
- **Sample Task**: The agent is instructed to sign up for updates on a website using a provided email address.

## Dependencies

Before you begin, ensure you have the following dependencies installed:

- **Python 3.11+**
- **inspect-ai**
- **asteroid-sdk**

### Installation

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Example

1. **Configure Your API Keys**

   Ensure that you have configured your API keys for Asteroid and OpenAI. You can set them as environment variables:

   ```bash
   export ASTEROID_API_KEY="your-asteroid-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Execute the Script**

   Navigate to the `cookbook/inspect/inspect_web_browser` directory and run the script:

   ```bash
   python run.py
   ```

3. **Observe the Output**

   The script instructs the AI agent to navigate to `http://asteroid.ai/` and sign up using the email address `hello@test.com`. You can follow the agent's steps and web interactions through the console output.

## Customization

You can customize the example to suit different web interaction tasks:

- **Modify the Task Instruction**: Change the `input` text in `run.py` to instruct the agent to perform different actions on the web.
- **Add More Tools**: Incorporate additional tools if needed for more complex tasks.
- **Adjust Execution Settings**: Modify parameters such as the AI model or enable tracing and approval workflows.

## Conclusion

This example illustrates how to empower an AI agent with web browsing capabilities using the `inspect_ai` library. It showcases the potential for creating autonomous agents that can interact with web environments to complete tasks such as form submissions, data scraping, and navigation. 