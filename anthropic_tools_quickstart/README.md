# Anthropic Tools Quickstart

## Dependencies

Before you begin, ensure you have the following dependencies installed:

- **Python 3.11+**

### Installation

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Overview

This quickstart guide demonstrates how to integrate Anthropic's AI models with custom supervision logic using the Asteroid SDK. It showcases how to create tool supervisors that enforce business rules, such as limiting the maximum price for booking flights and hotels.

## Quickstart

### Running the Example

1. **Configure Your API Keys**

   Ensure that you have configured your API keys for Asteroid, Anthropic and OpenAI. You can set them as environment variables:

   ```bash
   export ASTEROID_API_KEY="your-asteroid-api-key"
   export ASTEROID_API_URL="your-asteroid-api-url"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Execute the Script**

   ```bash
   python cookbook/anthropic_tools_quickstart/run.py
   ```

3. **Interact with the Assistant**

   Follow the on-screen prompts to enter messages and observe how the supervisors manage tool calls based on your defined rules.
   For example you can try:

   ```
   What's the weather in San Francisco on 12.25.2024?
   ```

   ```
   Book a flight from New York to San Francisco for $200 on 12.25.2024.
   ```

   ```
   Book a hotel in San Francisco for $400 on 12.25.2024.
   ```

### Example Supervisors

- **Max Price Supervisor**: Rejects any tool call where the price exceeds a specified maximum.
- **Human Supervisor**: Escalates tool calls to a human for approval based on custom instructions.
- **LLM Supervisor**: Utilizes a language model to make supervision decisions.